"""Cross-cutting terms: product models, provenance helpers, not-stated records, qualification, redundancy and
the shapes for feature statements.

Each entry: local name -> label, definition (one sentence, our own words), and the parents or
property details the generator needs. See docs/MODELING.md, patterns X1 to X7.
"""

from rdflib import BNode, Literal
from rdflib.collection import Collection
from rdflib.namespace import OWL, PROV, RDF, SH, XSD

from .namespaces import AIF, OA, S223

# Classes that are neither equipment nor components.
CORE_CLASSES = {
    "ProductModel": {
        "label": "Product model",
        "definition": "A vendor product as sold under one model or part number, standing for the specification that every unit of that model shares.",
        "parents": [OWL.Thing],
    },
    "Source": {
        "label": "Source document",
        "definition": "A vendor document or web page registered in the source registry, identified by its checksum, from which values in this ontology are read.",
        "parents": [OWL.Thing],
    },
    "NotStatedRecord": {
        "label": "Not-stated record",
        "definition": "A record that the listed documents of a product model were read and none of them states a given item.",
        "parents": [OWL.Thing],
    },
    "Qualification": {
        "label": "Qualification",
        "definition": "A statement by a vendor or platform owner that a product, or a combination of products, has been tested or certified to work together.",
        "parents": [OWL.Thing],
    },
    "ReferenceArchitecture": {
        "label": "Reference architecture",
        "definition": "A vendor-published design of a whole AI cluster for one GPU platform and one compute network, naming the kinds of equipment it includes.",
        "parents": [OWL.Thing],
    },
    "ReferenceRole": {
        "label": "Reference role",
        "definition": "One kind of equipment a reference architecture includes, such as its compute network switches or its management servers.",
        "parents": [OWL.Thing],
    },
    "RedundancyGroup": {
        "label": "Redundancy group",
        "definition": "A set of like units inside a product, such as its pumps, power supplies or fans, described by the redundancy scheme they follow or by how many are fitted and how many must work to carry the full load.",
        "parents": [OWL.Thing],
    },
}

# Object and datatype properties we define. "domain" and "range" express meaning; constraints live in shapes.
RELATIONS = {
    "hasModel": {
        "type": OWL.ObjectProperty,
        "label": "has model",
        "definition": "Links an installed unit to the product model whose specification it takes.",
        "range": AIF.ProductModel,
    },
    "condition": {
        "type": OWL.DatatypeProperty,
        "label": "condition",
        "definition": "The circumstances under which a value holds, such as a coolant temperature or an altitude, written in our own words.",
        "domain": S223.Property,
        "range": XSD.string,
    },
    "basis": {
        "type": OWL.ObjectProperty,
        "label": "basis",
        "definition": "Whether a value is read directly from a document or derived by combining several statements.",
        "range": AIF["EnumerationKind-Basis"],
    },
    "reasoning": {
        "type": OWL.DatatypeProperty,
        "label": "reasoning",
        "definition": "How a derived value was obtained from the statements it rests on, written in our own words.",
        "range": XSD.string,
    },
    "section": {
        "type": OWL.DatatypeProperty,
        "label": "section",
        "definition": "The heading of the part of a web page or list a value comes from, written in our own words.",
        "domain": OA.SpecificResource,
        "range": XSD.string,
    },
    "aboutModel": {
        "type": OWL.ObjectProperty,
        "label": "about model",
        "definition": "The product model a not-stated record or a qualification concerns.",
        "range": AIF.ProductModel,
    },
    "aboutQuantityKind": {
        "type": OWL.ObjectProperty,
        "label": "about quantity kind",
        "definition": "The kind of quantity a not-stated record says the documents do not give.",
        "domain": AIF.NotStatedRecord,
    },
    "aboutPropertyClass": {
        "type": OWL.ObjectProperty,
        "label": "about property class",
        "definition": "The class of property a not-stated record says the documents do not give, when a quantity kind alone is not specific enough.",
        "domain": AIF.NotStatedRecord,
    },
    "aboutConnectionPointClass": {
        "type": OWL.ObjectProperty,
        "label": "about connection point class",
        "definition": "The kind of connection point whose missing value a not-stated record concerns.",
        "domain": AIF.NotStatedRecord,
    },
    "checkedSource": {
        "type": OWL.ObjectProperty,
        "label": "checked source",
        "definition": "A document that was read for a not-stated record and found not to state the item.",
        "range": AIF.Source,
    },
    "qualificationScope": {
        "type": OWL.ObjectProperty,
        "label": "qualification scope",
        "definition": "What a qualification covers: a pairing of components, a validated configuration, a certified system, a catalog entry or an endorsed design.",
        "domain": AIF.Qualification,
        "range": AIF["EnumerationKind-QualificationScope"],
    },
    "qualifiedBy": {
        "type": OWL.ObjectProperty,
        "label": "qualified by",
        "definition": "The organization that issued a qualification.",
        "domain": AIF.Qualification,
    },
    "qualifiedItem": {
        "type": OWL.ObjectProperty,
        "label": "qualified item",
        "definition": "A product model a qualification names.",
        "domain": AIF.Qualification,
        "range": AIF.ProductModel,
    },
    "firmwareVersion": {
        "type": OWL.DatatypeProperty,
        "label": "firmware version",
        "definition": "The firmware release a qualification was stated for.",
        "domain": AIF.Qualification,
        "range": XSD.string,
    },
    "hasRedundancyGroup": {
        "type": OWL.ObjectProperty,
        "label": "has redundancy group",
        "definition": "Links a product model to a redundancy group of its internal units.",
        "domain": AIF.ProductModel,
        "range": AIF.RedundancyGroup,
    },
    "memberModel": {
        "type": OWL.ObjectProperty,
        "label": "member model",
        "definition": "The product model of the units in a redundancy group.",
        "domain": AIF.RedundancyGroup,
        "range": AIF.ProductModel,
    },
    "memberClass": {
        "type": OWL.ObjectProperty,
        "label": "member class",
        "definition": "The equipment or component class of the units in a redundancy group, given when the units have no product model of their own.",
        "domain": AIF.RedundancyGroup,
    },
    "redundancyScheme": {
        "type": OWL.ObjectProperty,
        "label": "redundancy scheme",
        "definition": "The redundancy scheme, such as N+1 or 2N, that the units of a redundancy group follow.",
        "domain": AIF.RedundancyGroup,
        "range": AIF["EnumerationKind-RedundancyScheme"],
    },
    "installedCount": {
        "type": OWL.DatatypeProperty,
        "label": "installed count",
        "definition": "How many units of a redundancy group are fitted.",
        "domain": AIF.RedundancyGroup,
        "range": XSD.integer,
    },
    "requiredCount": {
        "type": OWL.DatatypeProperty,
        "label": "required count",
        "definition": "How many units of a redundancy group must work to carry the full load.",
        "domain": AIF.RedundancyGroup,
        "range": XSD.integer,
    },
    "gpuPlatform": {
        "type": OWL.ObjectProperty,
        "label": "GPU platform",
        "definition": "The GPU platform a reference architecture is designed for.",
        "domain": AIF.ReferenceArchitecture,
        "range": AIF["EnumerationKind-GPUPlatform"],
    },
    "computeFabric": {
        "type": OWL.ObjectProperty,
        "label": "compute fabric",
        "definition": "The protocol of the compute network in a reference architecture.",
        "domain": AIF.ReferenceArchitecture,
        "range": AIF["EnumerationKind-NetworkProtocol"],
    },
    "hasReferenceRole": {
        "type": OWL.ObjectProperty,
        "label": "has reference role",
        "definition": "Links a reference architecture to one kind of equipment it includes.",
        "domain": AIF.ReferenceArchitecture,
        "range": AIF.ReferenceRole,
    },
    "roleClass": {
        "type": OWL.ObjectProperty,
        "label": "role class",
        "definition": "The equipment class that fills a reference role.",
        "domain": AIF.ReferenceRole,
    },
    "roleFunction": {
        "type": OWL.ObjectProperty,
        "label": "role function",
        "definition": "The enumerated function that narrows a reference role within its class, such as out-of-band management for an Ethernet switch.",
        "domain": AIF.ReferenceRole,
    },
    "sha256": {
        "type": OWL.DatatypeProperty,
        "label": "SHA-256 checksum",
        "definition": "The SHA-256 checksum of the original file of a source document.",
        "domain": AIF.Source,
        "range": XSD.string,
    },
}

# Enumeration kinds in 223's pattern: the kind and each member are classes and instances of themselves.
CORE_ENUMERATIONS = {
    "Basis": {
        "label": "Basis",
        "definition": "Whether a value is read directly from a document or derived from several statements.",
        "values": {
            "Stated": {"label": "Stated", "definition": "The value is printed in the cited document as it is recorded."},
            "Derived": {"label": "Derived", "definition": "The value is obtained by combining or computing from several printed statements."},
        },
    },
    "QualificationScope": {
        "label": "Qualification scope",
        "definition": "The kinds of thing a qualification can cover.",
        "values": {
            "ComponentPairing": {"label": "Component pairing", "definition": "Two components, such as a cable and a switch, tested together."},
            "ValidatedConfiguration": {"label": "Validated configuration", "definition": "A set of hardware with stated firmware and software versions tested together as a whole."},
            "CertifiedSystem": {"label": "Certified system", "definition": "A server or rack system certified by a platform owner for a workload."},
            "CatalogEntry": {"label": "Catalog entry", "definition": "A listing of a system in a platform owner's catalog of qualified systems."},
            "EndorsedDesign": {"label": "Endorsed design", "definition": "A facility or rack design reviewed and endorsed by a platform owner."},
        },
    },
    "RedundancyScheme": {
        "label": "Redundancy scheme",
        "definition": "The ways a set of like units is sized against the number N of units that the full load needs.",
        "values": {
            "N": {"label": "N", "definition": "Exactly as many units as the full load needs and no spare, also written N+0."},
            "N+1": {"label": "N+1", "definition": "One spare unit beyond the N units that the full load needs."},
            "N+2": {"label": "N+2", "definition": "Two spare units beyond the N units that the full load needs."},
            "N+N": {"label": "N+N", "definition": "N spare units beyond the N units that the full load needs, so that the load is still carried when half of the units fail."},
            "2N": {"label": "2N", "definition": "Two complete sets of the N units that the full load needs, each able to carry the full load on its own, such as two independent power paths."},
            "2N+1": {"label": "2N+1", "definition": "Two complete sets of the N units that the full load needs, as in 2N, and one further spare unit."},
        },
    },
}

# Members we add to 223's existing aspect enumeration (s223:EnumerationKind-Aspect).
ASPECTS = {
    "Required": {"label": "Required", "definition": "The vendor states the value as a need of the device, which the supplying side has to meet."},
    "Recommended": {"label": "Recommended", "definition": "The vendor states the value as advice rather than as a requirement."},
    "Operating": {"label": "Operating", "definition": "The value bounds the normal operating range, as opposed to a limit the device tolerates without operating normally."},
}


# ---------------------------------------------------------------------------------------------
# Shapes for feature statements (docs/CONVENTIONS.md section 9, docs/MODELING.md pattern X7). A feature
# statement is a W3C Web Annotation with the describing motivation. SHACL Core has no target for annotations
# with a given motivation, so each shape targets every annotation and holds when the annotation is either not
# describing or meets the check.

FEATURE_STATEMENT_SHAPES = {
    "FeatureStatementTargetShape": "A feature statement targets exactly one product model.",
    "FeatureStatementBodyShape": "A feature statement has exactly one textual body whose rdf:value is one English text.",
    "FeatureStatementProvenanceShape": "A feature statement cites where it comes from with prov:wasDerivedFrom: a specific resource with a source document and a selector.",
}


def _node(g, *pairs) -> BNode:
    node = BNode()
    for predicate, obj in pairs:
        g.add((node, predicate, obj))
    return node


def _feature_statement_check(g, name: str) -> BNode:
    one = (SH.minCount, Literal(1)), (SH.maxCount, Literal(1))
    if name == "FeatureStatementTargetShape":
        check = _node(g, (SH.path, OA.hasTarget), *one, (SH["class"], AIF.ProductModel))
    elif name == "FeatureStatementBodyShape":
        languages = BNode()
        Collection(g, languages, [Literal("en")])
        value = _node(g, (SH.path, RDF.value), *one, (SH.datatype, RDF.langString), (SH.languageIn, languages))
        check = _node(g, (SH.path, OA.hasBody), *one, (SH["class"], OA.TextualBody),
                      (SH.node, _node(g, (SH.property, value))))
    else:
        source = _node(g, (SH.path, OA.hasSource), (SH.minCount, Literal(1)), (SH["class"], AIF.Source))
        selector = _node(g, (SH.path, OA.hasSelector), (SH.minCount, Literal(1)))
        check = _node(g, (SH.path, PROV.wasDerivedFrom), (SH.minCount, Literal(1)), (SH["class"], OA.SpecificResource),
                      (SH.node, _node(g, (SH.property, source), (SH.property, selector))))
    return _node(g, (SH.property, check))


def add_shapes(builder, module: str) -> None:
    g = builder.shapes
    for term in (OA.Annotation, OA.motivatedBy, OA.describing, OA.hasTarget, OA.hasBody, OA.TextualBody,
                 OA.SpecificResource, OA.hasSource, OA.hasSelector, PROV.wasDerivedFrom, AIF.ProductModel, AIF.Source):
        builder.references.append((f"{module}.FEATURE_STATEMENT_SHAPES", term))
    for name, message in FEATURE_STATEMENT_SHAPES.items():
        shape = AIF[name]
        not_describing = _node(g, (SH["not"], _node(g, (SH.path, OA.motivatedBy), (SH.hasValue, OA.describing))))
        alternatives = BNode()
        Collection(g, alternatives, [not_describing, _feature_statement_check(g, name)])
        g.add((shape, RDF.type, SH.NodeShape))
        g.add((shape, SH.targetClass, OA.Annotation))
        g.add((shape, SH["or"], alternatives))
        g.add((shape, SH.message, Literal(message, lang="en")))
