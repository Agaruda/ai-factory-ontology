"""Generate schema/ai-factory.ttl and schema/ai-factory-shapes.ttl from schema/definitions.

    uv run python pipeline/build_schema.py          # write both files
    uv run python pipeline/build_schema.py --check  # fail if the files are out of date
    uv run python pipeline/build_schema.py --dry-run  # build and check the definitions, write nothing

Every IRI a definition points to (parent class, mapping, quantity kind, unit) must exist in the pinned
standards under schema/vendor/ or in the generated schema; names, labels and definitions are checked
against docs/CONVENTIONS.md section 3.
"""

from __future__ import annotations

import argparse
import importlib
import re
import sys
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.compare import to_canonical_graph
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, SKOS, XSD

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "schema"))

from definitions.namespaces import AIF, ONTOLOGY_IRI, PREFIXES, QUDT, S223, VERSION  # noqa: E402

MODULES = ["core", "common", "compute_network", "cooling", "power"]
VENDOR = ROOT / "schema" / "vendor"
VENDOR_FILES = ["brick.ttl", "ashrae-223.ttl", "qudt-schema.ttl", "qudt-quantitykind.ttl", "qudt-unit.ttl",
                "oa.ttl", "prov-o.ttl", "skos.rdf", "dcterms.ttl"]
SCHEMA_OUT = ROOT / "schema" / "ai-factory.ttl"
SHAPES_OUT = ROOT / "schema" / "ai-factory-shapes.ttl"

CLASS_NAME = re.compile(r"^[A-Z][A-Za-z0-9]*$")
MEMBER_NAME = re.compile(r"^[A-Za-z0-9.+-]+$")
PROPERTY_NAME = re.compile(r"^[a-z][A-Za-z0-9]*$")


class DefinitionError(Exception):
    pass


def new_graph() -> Graph:
    g = Graph()
    for prefix, namespace in PREFIXES.items():
        g.bind(prefix, namespace, override=True, replace=True)
    return g


def check_text(where: str, entry: dict) -> None:
    label, definition = entry.get("label"), entry.get("definition")
    if not label or not definition:
        raise DefinitionError(f"{where}: label and definition are required")
    for name, text in (("label", label), ("definition", definition)):
        if not text.isascii() or "\n" in text:
            raise DefinitionError(f"{where}: {name} must be one line of ASCII English")
    if label.endswith("."):
        raise DefinitionError(f"{where}: a label does not end with a period")
    if not definition.endswith(".") or len(definition) > 320:
        raise DefinitionError(f"{where}: a definition is one sentence ending with a period, at most 320 characters")
    if re.search(r"\.\s+[A-Z]", definition[:-1]):
        raise DefinitionError(f"{where}: a definition is one sentence")


class Builder:
    def __init__(self) -> None:
        self.schema = new_graph()
        self.shapes = new_graph()
        self.defined: set[URIRef] = set()
        self.references: list[tuple[str, URIRef]] = []

    # -- helpers -------------------------------------------------------------------------------

    def define(self, iri: URIRef, where: str) -> None:
        if iri in self.defined:
            raise DefinitionError(f"{where}: {iri} is defined twice")
        self.defined.add(iri)

    def describe(self, iri: URIRef, entry: dict) -> None:
        g = self.schema
        g.add((iri, RDFS.label, Literal(entry["label"], lang="en")))
        g.add((iri, SKOS.definition, Literal(entry["definition"], lang="en")))
        g.add((iri, RDFS.comment, Literal(entry["definition"], lang="en")))
        for key, predicate in (("exact_match", SKOS.exactMatch), ("close_match", SKOS.closeMatch),
                               ("broad_match", SKOS.broadMatch), ("narrow_match", SKOS.narrowMatch)):
            for target in entry.get(key, []):
                self.references.append((f"{iri} {key}", target))
                g.add((iri, predicate, target))

    def subclass(self, iri: URIRef, parent: URIRef, where: str) -> None:
        self.references.append((where, parent))
        self.schema.add((iri, RDFS.subClassOf, parent))

    # -- classes -------------------------------------------------------------------------------

    def add_class_tree(self, tree: dict, parent: URIRef | None, module: str) -> None:
        for name, entry in tree.items():
            where = f"{module}.{name}"
            if not CLASS_NAME.match(name):
                raise DefinitionError(f"{where}: class names are UpperCamelCase")
            check_text(where, entry)
            iri = AIF[name]
            self.define(iri, where)
            self.schema.add((iri, RDF.type, OWL.Class))
            self.schema.add((iri, RDF.type, S223.Class))
            parents = ([parent] if parent is not None else []) + list(entry.get("parents", []))
            if not parents:
                raise DefinitionError(f"{where}: a top-level class needs a Brick or 223 parent")
            for p in parents:
                self.subclass(iri, p, where)
            self.describe(iri, entry)
            for requirement in entry.get("connection_points", []):
                self.add_connection_point_requirement(iri, requirement, where)
            self.add_class_tree(entry.get("subclasses", {}), iri, module)

    def add_simple_classes(self, classes: dict, module: str) -> None:
        for name, entry in classes.items():
            where = f"{module}.{name}"
            if not CLASS_NAME.match(name):
                raise DefinitionError(f"{where}: class names are UpperCamelCase")
            check_text(where, entry)
            iri = AIF[name]
            self.define(iri, where)
            self.schema.add((iri, RDF.type, OWL.Class))
            for p in entry.get("parents", []):
                self.subclass(iri, p, where)
            self.describe(iri, entry)

    # -- enumerations and media (223 pattern: each member is a class and an instance of itself) -----

    def add_member(self, iri: URIRef, parent: URIRef, entry: dict, where: str) -> None:
        check_text(where, entry)
        self.define(iri, where)
        for t in (S223.Class, iri, SH.NodeShape):
            self.schema.add((iri, RDF.type, t))
        self.subclass(iri, parent, where)
        self.describe(iri, entry)
        for predicate, obj in entry.get("triples", []):
            self.schema.add((iri, predicate, obj))
        for constituent in entry.get("composed_of", []):
            node = BNode()
            self.schema.add((iri, S223.composedOf, node))
            self.add_quantity_node(node, constituent, where)

    def add_quantity_node(self, node: BNode, spec: dict, where: str) -> None:
        g = self.schema
        g.add((node, RDF.type, S223.QuantifiableProperty))
        g.add((node, RDFS.label, Literal(spec["label"], lang="en")))
        if "value" in spec:  # 223 leaves the amount out of a generic mix (label "Unspecified")
            g.add((node, S223.hasValue, Literal(spec["value"], datatype=XSD.decimal)))
        for key, predicate in (("of_constituent", S223.ofConstituent), ("quantity_kind", QUDT.hasQuantityKind),
                               ("unit", QUDT.hasUnit)):
            self.references.append((where, spec[key]))
            g.add((node, predicate, spec[key]))

    def add_enumerations(self, enumerations: dict, module: str) -> None:
        for kind_name, entry in enumerations.items():
            where = f"{module}.EnumerationKind-{kind_name}"
            if not CLASS_NAME.match(kind_name):
                raise DefinitionError(f"{where}: enumeration kinds are UpperCamelCase")
            kind = AIF[f"EnumerationKind-{kind_name}"]
            self.add_member(kind, entry.get("parent", S223.EnumerationKind), entry, where)
            for value_name, value in entry["values"].items():
                if not MEMBER_NAME.match(value_name):
                    raise DefinitionError(f"{where}.{value_name}: member names use letters, digits, '.', '+' and '-'")
                self.add_member(AIF[f"{kind_name}-{value_name}"], kind, value, f"{where}.{value_name}")

    def add_extension_members(self, kind: URIRef, prefix: str, members: dict, module: str) -> None:
        """Members we add to an enumeration kind that 223 defines (for example aspects)."""
        for name, entry in members.items():
            self.add_member(AIF[f"{prefix}-{name}"], kind, entry, f"{module}.{prefix}-{name}")

    def add_media(self, media: dict, module: str) -> None:
        for name, entry in media.items():
            self.add_member(AIF[name], entry["parent"], entry, f"{module}.{name}")

    def add_units(self, units: dict, module: str) -> None:
        """Units QUDT lacks, written in QUDT's pattern so unit-aware tools can convert them."""
        for name, entry in units.items():
            where = f"{module}.Unit-{name}"
            if not MEMBER_NAME.match(name):
                raise DefinitionError(f"{where}: unit names use letters, digits, '.', '+' and '-'")
            check_text(where, entry)
            iri = AIF[f"Unit-{name}"]
            self.define(iri, where)
            self.schema.add((iri, RDF.type, QUDT.Unit))
            self.describe(iri, entry)
            self.schema.add((iri, QUDT.symbol, Literal(entry["symbol"])))
            self.schema.add((iri, QUDT.conversionMultiplier, Literal(entry["multiplier"], datatype=XSD.decimal)))
            for kind in entry["quantity_kinds"]:
                self.references.append((where, kind))
                self.schema.add((iri, QUDT.hasQuantityKind, kind))

    # -- properties ----------------------------------------------------------------------------

    def add_property_classes(self, properties: dict, module: str) -> None:
        for name, entry in properties.items():
            where = f"{module}.{name}"
            if not CLASS_NAME.match(name):
                raise DefinitionError(f"{where}: property classes are UpperCamelCase")
            check_text(where, entry)
            iri = AIF[name]
            self.define(iri, where)
            self.schema.add((iri, RDF.type, OWL.Class))
            self.schema.add((iri, RDF.type, S223.Class))
            self.subclass(iri, entry["parent"], where)
            self.describe(iri, entry)
            shape = self.class_shape(iri)
            if "quantity_kind" in entry:
                self.references.append((where, entry["quantity_kind"]))
                self.value_constraint(shape, QUDT.hasQuantityKind, entry["quantity_kind"])
                units = entry.get("units", [])
                for u in units:
                    self.references.append((where, u))
                if units:
                    self.in_constraint(shape, QUDT.hasUnit, units)
            if "enumeration" in entry:
                kind = AIF[f"EnumerationKind-{entry['enumeration']}"]
                self.references.append((where, kind))
                self.value_constraint(shape, S223.hasEnumerationKind, kind)

    def add_relations(self, relations: dict, module: str) -> None:
        for name, entry in relations.items():
            where = f"{module}.{name}"
            if not PROPERTY_NAME.match(name):
                raise DefinitionError(f"{where}: properties are lowerCamelCase")
            check_text(where, entry)
            iri = AIF[name]
            self.define(iri, where)
            self.schema.add((iri, RDF.type, entry["type"]))
            self.describe(iri, entry)
            for key, predicate in (("domain", RDFS.domain), ("range", RDFS.range)):
                if key in entry:
                    self.references.append((where, entry[key]))
                    self.schema.add((iri, predicate, entry[key]))

    # -- shapes --------------------------------------------------------------------------------

    def class_shape(self, iri: URIRef) -> URIRef:
        shape = URIRef(f"{iri}Shape")
        if (shape, RDF.type, SH.NodeShape) not in self.shapes:
            self.shapes.add((shape, RDF.type, SH.NodeShape))
            self.shapes.add((shape, SH.targetClass, iri))
        return shape

    def value_constraint(self, shape: URIRef, path: URIRef, value: URIRef) -> None:
        p = BNode()
        self.shapes.add((shape, SH.property, p))
        self.shapes.add((p, SH.path, path))
        self.shapes.add((p, SH.hasValue, value))
        self.shapes.add((p, SH.maxCount, Literal(1)))

    def in_constraint(self, shape: URIRef, path: URIRef, values: list[URIRef]) -> None:
        p = BNode()
        lst = BNode()
        Collection(self.shapes, lst, list(values))
        self.shapes.add((shape, SH.property, p))
        self.shapes.add((p, SH.path, path))
        self.shapes.add((p, SH["in"], lst))

    def add_connection_point_requirement(self, cls: URIRef, req: dict, where: str) -> None:
        """A class needs at least `min` connection points of a kind, medium and role."""
        shape = self.class_shape(cls)
        p, q = BNode(), BNode()
        self.shapes.add((shape, SH.property, p))
        self.shapes.add((p, SH.path, S223.hasConnectionPoint))
        self.shapes.add((p, SH.qualifiedValueShape, q))
        self.shapes.add((p, SH.qualifiedMinCount, Literal(req.get("min", 1))))
        self.shapes.add((p, SH.message, Literal(req["message"], lang="en")))
        # A missing connection point usually means the documents do not describe it, so the default is a warning.
        self.shapes.add((p, SH.severity, req.get("severity", SH.Warning)))
        self.references.append((where, req["class"]))
        self.shapes.add((q, SH["class"], req["class"]))
        if "medium" in req:
            self.references.append((where, req["medium"]))
            m = BNode()
            self.shapes.add((q, SH.property, m))
            self.shapes.add((m, SH.path, S223.hasMedium))
            self.shapes.add((m, SH["class"], req["medium"]))
        for role in req.get("roles", []):
            self.references.append((where, role))
            r = BNode()
            self.shapes.add((q, SH.property, r))
            self.shapes.add((r, SH.path, S223.hasRole))
            self.shapes.add((r, SH.hasValue, role))

    def add_shapes(self, shapes_fn, module: str) -> None:
        shapes_fn(self, module)

    # -- whole build ---------------------------------------------------------------------------

    def header(self) -> None:
        g = self.schema
        o = URIRef(ONTOLOGY_IRI)
        g.add((o, RDF.type, OWL.Ontology))
        g.add((o, RDFS.label, Literal("AI Factory Ontology", lang="en")))
        g.add((o, DCTERMS.title, Literal("AI Factory Ontology", lang="en")))
        g.add((o, DCTERMS.description, Literal(
            "An extension of Brick and ASHRAE Standard 223 for AI data centers: GPU systems and the network, "
            "liquid-cooling and power equipment around them, with product specifications and compatibility rules.",
            lang="en")))
        g.add((o, OWL.versionInfo, Literal(VERSION)))
        g.add((o, OWL.imports, URIRef("https://brickschema.org/schema/1.4/Brick")))
        g.add((o, OWL.imports, URIRef("http://data.ashrae.org/standard223/1.0/model/all")))
        s = URIRef(f"{ONTOLOGY_IRI}/shapes")
        self.shapes.add((s, RDF.type, OWL.Ontology))
        self.shapes.add((s, RDFS.label, Literal("AI Factory Ontology structure shapes", lang="en")))
        self.shapes.add((s, OWL.imports, o))

    def build(self) -> None:
        self.header()
        for module_name in MODULES:
            try:
                module = importlib.import_module(f"definitions.{module_name}")
            except ModuleNotFoundError:
                continue
            for attr, method in (("CORE_CLASSES", self.add_simple_classes), ("EQUIPMENT", None),
                                 ("COMPONENTS", None), ("SYSTEMS", None), ("CONNECTION_POINTS", self.add_simple_classes),
                                 ("PROPERTIES", self.add_property_classes), ("RELATIONS", self.add_relations),
                                 ("CORE_ENUMERATIONS", self.add_enumerations), ("ENUMERATIONS", self.add_enumerations),
                                 ("MEDIA", self.add_media), ("UNITS", self.add_units)):
                value = getattr(module, attr, None)
                if value is None:
                    continue
                if method is None:
                    self.add_class_tree(value, None, module_name)
                else:
                    method(value, module_name)
            if hasattr(module, "ASPECTS"):
                self.add_extension_members(S223["EnumerationKind-Aspect"], "Aspect", module.ASPECTS, module_name)
            if hasattr(module, "add_shapes"):
                self.add_shapes(module.add_shapes, module_name)


    def check_references(self) -> None:
        vendor = Graph()
        for name in VENDOR_FILES:
            vendor.parse(VENDOR / name)
        known = set(vendor.subjects()) | self.defined
        known |= {OWL.Thing, XSD.string, XSD.integer, XSD.decimal, XSD.boolean}
        missing = sorted({(where, str(iri)) for where, iri in self.references if iri not in known})
        if missing:
            raise DefinitionError("unknown IRIs:\n" + "\n".join(f"  {w}: {i}" for w, i in missing))


def serialize(g: Graph) -> str:
    """Turtle in the fixed layout; blank nodes get canonical labels so the output is byte-stable."""
    out = new_graph()
    for triple in to_canonical_graph(g):
        out.add(triple)
    return out.serialize(format="longturtle")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="fail if the generated files are out of date")
    parser.add_argument("--dry-run", action="store_true", help="build and check the definitions, write nothing")
    args = parser.parse_args()
    builder = Builder()
    try:
        builder.build()
        builder.check_references()
    except DefinitionError as error:
        print(f"build_schema: {error}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(f"ok: {len(builder.defined)} terms, {len(builder.schema)} schema triples, {len(builder.shapes)} shape triples")
        return 0
    outputs = {SCHEMA_OUT: serialize(builder.schema), SHAPES_OUT: serialize(builder.shapes)}
    if args.check:
        stale = [p.name for p, text in outputs.items() if not p.exists() or p.read_text() != text]
        if stale:
            print(f"build_schema: out of date: {', '.join(stale)}", file=sys.stderr)
            return 1
        return 0
    for path, text in outputs.items():
        path.write_text(text)
    print(f"wrote {SCHEMA_OUT.relative_to(ROOT)} ({len(builder.schema)} triples), "
          f"{SHAPES_OUT.relative_to(ROOT)} ({len(builder.shapes)} triples)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
