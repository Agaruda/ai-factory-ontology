"""Namespaces used by the AI Factory Ontology and the prefixes written into every Turtle file."""

from rdflib import Namespace
from rdflib.namespace import DCTERMS, OWL, PROV, RDF, RDFS, SH, SKOS, XSD

AIF = Namespace("https://w3id.org/ai-factory#")
AIFM = Namespace("https://w3id.org/ai-factory/model/")
AIFS = Namespace("https://w3id.org/ai-factory/source/")
AIFORG = Namespace("https://w3id.org/ai-factory/org/")

BRICK = Namespace("https://brickschema.org/schema/Brick#")
S223 = Namespace("http://data.ashrae.org/standard223#")
REC = Namespace("https://w3id.org/rec#")
QUDT = Namespace("http://qudt.org/schema/qudt/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
QK = Namespace("http://qudt.org/vocab/quantitykind/")
OA = Namespace("http://www.w3.org/ns/oa#")

ONTOLOGY_IRI = "https://w3id.org/ai-factory"
VERSION = "0.2.0"

PREFIXES = {
    "ai-factory": AIF,
    "ai-factory-model": AIFM,
    "ai-factory-source": AIFS,
    "ai-factory-org": AIFORG,
    "brick": BRICK,
    "s223": S223,
    "rec": REC,
    "qudt": QUDT,
    "unit": UNIT,
    "quantitykind": QK,
    "oa": OA,
    "prov": PROV,
    "dcterms": DCTERMS,
    "skos": SKOS,
    "sh": SH,
    "owl": OWL,
    "rdf": RDF,
    "rdfs": RDFS,
    "xsd": XSD,
}
