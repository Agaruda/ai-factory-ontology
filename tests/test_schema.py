"""Checks on the generated schema, its shapes and the example models in tests/fixtures/."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pyshacl
import pytest
from rdflib import Graph
from rdflib.namespace import RDF, SH

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schema"
VENDOR = SCHEMA / "vendor"
FIXTURES = ROOT / "tests" / "fixtures"
PY = sys.executable


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([PY, *args], cwd=ROOT, capture_output=True, text=True)


def test_generated_schema_is_up_to_date():
    result = run("pipeline/build_schema.py", "--check")
    assert result.returncode == 0, result.stderr


def test_schema_loads_with_the_standards_it_extends():
    g = Graph()
    for name in ("brick.ttl", "ashrae-223.ttl"):
        g.parse(VENDOR / name)
    g.parse(SCHEMA / "ai-factory.ttl")
    g.parse(SCHEMA / "ai-factory-shapes.ttl")
    assert len(g) > 0


def test_turtle_files_keep_the_fixed_layout():
    targets = [str(SCHEMA / name) for name in ("ai-factory.ttl", "ai-factory-shapes.ttl")]
    if FIXTURES.exists():
        targets.append(str(FIXTURES))
    result = run("pipeline/format_ttl.py", "--check", *targets)
    assert result.returncode == 0, result.stdout


def fixture_graph() -> Graph:
    g = Graph()
    for path in sorted(FIXTURES.glob("*.ttl")):
        g.parse(path)
    return g


def our_results(results: Graph) -> list[str]:
    found = []
    for r in results.subjects(RDF.type, SH.ValidationResult):
        focus = str(results.value(r, SH.focusNode))
        if "w3id.org/ai-factory" in focus:
            severity = str(results.value(r, SH.resultSeverity)).rsplit("#", 1)[-1]
            found.append(f"{severity} {focus}: {results.value(r, SH.resultMessage)}")
    return found


@pytest.mark.skipif(not any(FIXTURES.glob("*.ttl")), reason="no example models yet")
def test_example_models_satisfy_our_shapes():
    data = fixture_graph()
    for name in ("ai-factory.ttl",):
        data.parse(SCHEMA / name)
    for name in ("brick.ttl", "ashrae-223.ttl"):
        data.parse(VENDOR / name)
    shapes = Graph().parse(SCHEMA / "ai-factory-shapes.ttl")
    _, results, _ = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    problems = [p for p in our_results(results) if not p.startswith("Info")]
    assert problems == []


FEATURE_STATEMENT_CASES = """
@prefix oa: <http://www.w3.org/ns/oa#> .
@prefix ai-factory-model: <https://w3id.org/ai-factory/model/> .
@prefix ai-factory-org: <https://w3id.org/ai-factory/org/> .

ai-factory-model:example-unknown.feature-1 a oa:Annotation ;
    oa:motivatedBy oa:describing ;
    oa:hasTarget ai-factory-org:example-thermal .

ai-factory-model:example-unknown.note-1 a oa:Annotation ;
    oa:motivatedBy oa:commenting .
"""


def test_feature_statement_shapes_report_a_malformed_statement():
    """A describing annotation with no body or provenance, aimed at an organization, fails all three checks;
    an annotation with another motivation is not checked."""
    data = Graph().parse(data=FEATURE_STATEMENT_CASES, format="turtle")
    shapes = Graph().parse(SCHEMA / "ai-factory-shapes.ttl")
    _, results, _ = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    failed: dict[str, set[str]] = {}
    for r in results.subjects(RDF.type, SH.ValidationResult):
        focus = str(results.value(r, SH.focusNode)).rsplit("/", 1)[-1]
        failed.setdefault(focus, set()).add(str(results.value(r, SH.sourceShape)).rsplit("#", 1)[-1])
    assert failed == {"example-unknown.feature-1": {
        "FeatureStatementTargetShape", "FeatureStatementBodyShape", "FeatureStatementProvenanceShape"}}


COOLANT_CASES = """
@prefix ai-factory: <https://w3id.org/ai-factory#> .
@prefix ai-factory-model: <https://w3id.org/ai-factory/model/> .
@prefix s223: <http://data.ashrae.org/standard223#> .

ai-factory-model:example-unknown.in a ai-factory:LiquidInlet ;
    s223:hasMedium s223:Fluid-Water ;
    s223:hasProperty ai-factory-model:example-unknown.in.coolant , ai-factory-model:example-unknown.in.coolant-2 ,
        ai-factory-model:example-unknown.in.coolant-3 .

ai-factory-model:example-unknown.in.coolant a ai-factory:CoolantProperty ;
    s223:hasEnumerationKind s223:Mix-Fluid ; s223:hasValue s223:Water-GlycolSolution .

ai-factory-model:example-unknown.in.coolant-2 a ai-factory:CoolantProperty ;
    s223:hasEnumerationKind s223:Mix-Fluid ; s223:hasValue ai-factory:Fluid-DielectricLiquid .

ai-factory-model:example-unknown.in.coolant-3 a ai-factory:CoolantProperty ;
    s223:hasEnumerationKind s223:Mix-Fluid ; s223:hasValue s223:Fluid-Air .

ai-factory-model:example-unknown.loose a ai-factory:CoolantProperty ;
    s223:hasEnumerationKind s223:Mix-Fluid ; s223:hasValue s223:Fluid-Water .
"""


def test_coolant_shapes_report_coolants_that_do_not_fit_their_point():
    """A glycol solution on a water point passes; a dielectric liquid on it is not within the point's medium, air is
    no coolant (and not within it either), and a coolant property on no connection point is reported."""
    data = Graph().parse(data=COOLANT_CASES, format="turtle").parse(SCHEMA / "ai-factory.ttl").parse(VENDOR / "ashrae-223.ttl")
    shapes = Graph().parse(SCHEMA / "ai-factory-shapes.ttl")
    _, results, _ = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    failed: dict[str, set[str]] = {}
    for r in results.subjects(RDF.type, SH.ValidationResult):
        focus = str(results.value(r, SH.focusNode)).rsplit("/", 1)[-1]
        failed.setdefault(focus, set()).add(str(results.value(r, SH.sourceConstraintComponent)).rsplit("#", 1)[-1])
    assert failed == {"example-unknown.in.coolant-2": {"SPARQLConstraintComponent"},
                      "example-unknown.in.coolant-3": {"OrConstraintComponent", "SPARQLConstraintComponent"},
                      "example-unknown.loose": {"MinCountConstraintComponent"}}


@pytest.mark.slow
@pytest.mark.skipif(not any(FIXTURES.glob("*.ttl")), reason="no example models yet")
def test_example_models_satisfy_ashrae_223_shapes():
    """223's own shapes on our data; slow (QUDT units are large), run with `pytest -m slow`."""
    data = fixture_graph()
    data.parse(SCHEMA / "ai-factory.ttl")
    for name in ("ashrae-223.ttl", "qudt-schema.ttl", "qudt-quantitykind.ttl", "qudt-unit.ttl"):
        data.parse(VENDOR / name)
    shapes = Graph().parse(VENDOR / "ashrae-223.ttl")
    _, results, _ = pyshacl.validate(data, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    problems = [p for p in our_results(results) if p.startswith("Violation")]
    assert problems == []
