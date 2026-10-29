"""Each competency question (tests/competency/*.rq) answered on the example models in tests/fixtures/."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from rdflib import Graph, Namespace

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "tests" / "competency"
AIF = Namespace("https://w3id.org/ai-factory#")
AIFM = Namespace("https://w3id.org/ai-factory/model/")
AIFS = Namespace("https://w3id.org/ai-factory/source/")
S223 = Namespace("http://data.ashrae.org/standard223#")
BRICK = Namespace("https://brickschema.org/schema/Brick#")
QK = Namespace("http://qudt.org/vocab/quantitykind/")

CDU = AIFM["example-cdu-l2l-500"]
SERVER = AIFM["example-gpu-server-8g"]
NIC = AIFM["example-nic-x800"]
SWITCH = AIFM["example-ib-switch-64"]
OPTIC = AIFM["example-osfp-800-sr8"]
GENSET = AIFM["example-genset-2000"]


@pytest.fixture(scope="module")
def graph() -> Graph:
    g = Graph()
    for path in sorted((ROOT / "tests" / "fixtures").glob("*.ttl")):
        g.parse(path)
    g.parse(ROOT / "schema" / "ai-factory.ttl")
    for name in ("brick.ttl", "ashrae-223.ttl"):
        g.parse(ROOT / "schema" / "vendor" / name)
    return g


def ask(graph: Graph, key: str, model) -> list[dict]:
    query = (QUERIES / f"{key}.rq").read_text()
    return [{k: v for k, v in row.asdict().items()} for row in graph.query(query, initBindings={"model": model})]


def column(rows: list[dict], name: str) -> set:
    return {r[name] for r in rows if name in r}


def number(value) -> Decimal:
    return Decimal(str(value))


def test_every_question_has_a_query():
    listed = {line.split("|")[1].strip() for line in (QUERIES / "README.md").read_text().splitlines()
              if line.startswith("| ") and line.split("|")[1].strip()[:1] in "CNOQFKP" and line.split("|")[1].strip() != "Id"}
    assert listed == {p.stem for p in QUERIES.glob("*.rq")}
    assert len(listed) == 21


def test_c1_kind_of_equipment(graph):
    rows = ask(graph, "C1", CDU)
    assert column(rows, "class") == {AIF.LiquidToLiquidCDU, AIF.CoolantDistributionUnit} or AIF.LiquidToLiquidCDU in column(rows, "class")
    assert BRICK.HVAC_Equipment in column(rows, "brickClass")
    assert S223.Equipment in column(rows, "s223Class")


def test_c2_components(graph):
    rows = ask(graph, "C2", SERVER)
    assert NIC in column(rows, "part") and AIF.NetworkAdapter in column(rows, "partClass")


def test_c3_meaning_of_values(graph):
    rows = ask(graph, "C3", SERVER)
    temp_max = AIFM["example-gpu-server-8g.gpu-loop-in.temp-max"]
    aspects = {r["aspect"] for r in rows if r["property"] == temp_max}
    assert aspects == {S223["Aspect-Maximum"], AIF["Aspect-Operating"], AIF["Aspect-Required"]}
    limit = AIFM["example-gpu-server-8g.gpu-loop-in.temp-high-limit"]
    assert {r["aspect"] for r in rows if r["property"] == limit} == {S223["Aspect-HighLimit"]}


def test_c4_document_and_page(graph):
    rows = ask(graph, "C4", SERVER)
    flow = [r for r in rows if r["property"] == AIFM["example-gpu-server-8g.gpu-loop-in.flow"]]
    assert flow and flow[0]["source"] == AIFS["example-gpu-server-8g-manual"] and str(flow[0]["selector"]) == "page=31"


def test_c5_not_stated(graph):
    rows = ask(graph, "C5", SWITCH)
    assert column(rows, "propertyClass") == {AIF.DCVoltage}
    assert column(rows, "connectionPointClass") == {AIF.PluggableCage}
    assert column(rows, "checked") == {AIFS["example-ib-switch-64-manual"], AIFS["example-ib-switch-64-datasheet"]}


def test_c6_conflicting_documents(graph):
    rows = ask(graph, "C6", CDU)
    assert len(rows) == 1
    assert {number(rows[0]["firstValue"]), number(rows[0]["secondValue"])} == {Decimal("600"), Decimal("580")}


def test_c7_qualifications(graph):
    rows = ask(graph, "C7", SWITCH)
    assert column(rows, "scope") == {AIF["QualificationScope-ComponentPairing"]}
    assert column(rows, "other") == {OPTIC}
    assert {str(f) for f in column(rows, "firmware")} == {"1.2.3"}


def test_n1_ports_of_a_device_and_its_adapter(graph):
    rows = ask(graph, "N1", SERVER)
    nic_port = AIFM["example-nic-x800.port-1"]
    assert {r["protocol"] for r in rows if r["port"] == nic_port and "protocol" in r} == {
        AIF["NetworkProtocol-InfiniBand"], AIF["NetworkProtocol-Ethernet"]}
    assert {number(r["rate"]) for r in rows if r["port"] == nic_port and "rate" in r} == {Decimal("800")}


def test_n2_switch_ports(graph):
    rows = ask(graph, "N2", SWITCH)
    assert column(rows, "protocol") == {AIF["NetworkProtocol-InfiniBand"]}
    assert column(rows, "generation") == {AIF["InfiniBandGeneration-NDR"]}
    assert {number(v) for v in column(rows, "rate")} == {Decimal("400")}


def test_n3_networks_a_device_needs(graph):
    rows = ask(graph, "N3", SERVER)
    assert S223["WiredEthernet-1000BASE-T"] in column(rows, "medium")
    assert AIF["NetworkProtocol-InfiniBand"] in column(rows, "protocol")


def test_o1_transceiver_plug(graph):
    rows = ask(graph, "O1", OPTIC)
    assert column(rows, "formFactor") == {AIF["PluggableFormFactor-OSFP"]}
    assert {number(v) for v in column(rows, "voltage")} == {Decimal("3.3")}
    assert {number(v) for v in column(rows, "rate")} == {Decimal("800")}


def test_o2_switch_cage_supply_voltage_not_stated(graph):
    rows = ask(graph, "O2", SWITCH)
    assert column(rows, "formFactor") == {AIF["PluggableFormFactor-OSFP"]}
    assert column(rows, "voltage") == set()
    assert column(rows, "notStated") == {AIFM["example-ib-switch-64.not-stated.cage-supply-voltage"]}


def test_q1_coupling_type_and_gender(graph):
    rows = ask(graph, "Q1", SERVER)
    assert column(rows, "couplingType") == {AIF["CouplingType-OCP-UQD08"]}
    assert column(rows, "gender") == {AIF["CouplingGender-Socket"]}


def test_q2_liquid_connections(graph):
    rows = ask(graph, "Q2", SERVER)
    assert {r["point"] for r in rows} == {AIFM["example-gpu-server-8g.gpu-loop-in"], AIFM["example-gpu-server-8g.gpu-loop-out"]}


def test_f1_accepted_coolant(graph):
    rows = ask(graph, "F1", SERVER)
    assert column(rows, "medium") == column(rows, "coolant") == {AIF["PropyleneGlycolSolution-25Percent"]}
    assert {number(r["concentration"]) for r in rows if r.get("constituent") == AIF["Constituent-PropyleneGlycol"]} == {Decimal("25.0")}


def test_f1_several_coolants_on_one_point(graph):
    rows = ask(graph, "F1", CDU)
    secondary = [r for r in rows if r["point"] == AIFM["example-cdu-l2l-500.tcs-return"]]
    assert column(secondary, "medium") == {S223["Fluid-Water"]}
    assert column(secondary, "coolant") == {AIF["PropyleneGlycolSolution-25Percent"], S223["Fluid-Water"]}


def test_k1_required_supply(graph):
    rows = ask(graph, "K1", SERVER)
    assert {(number(r["minimum"]), number(r["maximum"]), number(r["flow"])) for r in rows} == {
        (Decimal("25"), Decimal("45"), Decimal("15"))}


def test_k2_cdu_delivers(graph):
    rows = ask(graph, "K2", CDU)
    assert {number(v) for v in column(rows, "maximum")} == {Decimal("45")}
    assert {number(v) for v in column(rows, "flow")} == {Decimal("600"), Decimal("580")}
    assert {number(v) for v in column(rows, "capacity")} == {Decimal("500")}


def test_k3_loop_needed(graph):
    rows = ask(graph, "K3", SERVER)
    assert column(rows, "medium") == {AIF["PropyleneGlycolSolution-25Percent"]}
    assert column(rows, "role") == {S223["Role-Supply"]}


def test_p1_power_inlet(graph):
    rows = ask(graph, "P1", CDU)
    assert column(rows, "phases") == {S223["NumberOfElectricalPhases-ThreePhase"]}
    assert column(rows, "frequency") == {S223["Frequency-50Hz"], S223["Frequency-60Hz"]}
    assert {number(v) for v in column(rows, "voltage")} == {Decimal("380"), Decimal("415")}
    assert column(rows, "connector") == {AIF["PowerConnector-Hardwired"]}


def test_p2_power_outlet(graph):
    rows = ask(graph, "P2", GENSET)
    assert column(rows, "voltageClass") == {AIF.LineToLineVoltage}
    assert {number(v) for v in column(rows, "voltage")} == {Decimal("13.8")}


def test_p3_single_printed_frequency(graph):
    rows = ask(graph, "P3", GENSET)
    assert column(rows, "frequency") == {S223["Frequency-60Hz"]}
