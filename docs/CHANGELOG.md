# Changelog

## 0.4.0 (draft)

- A coolant property for liquid connection points (decision G21): one `CoolantProperty` per coolant a point takes, each with its own provenance, valued with the coolant media and checked by shapes (a coolant medium, on a connection point, and the point's medium or a narrower one). The point keeps one medium, the common kind of its coolants.
- The example CDU's secondary loop takes two coolants; competency question F1 lists the coolants a point names, and a test checks that coolants that do not fit their point are reported.
- The project version is 0.4.0.

## 0.3.0 (draft)

- Feature statements: descriptive statements about a product model as W3C Web Annotations with the describing motivation, never property values, with shapes that check their target, English body and provenance (`docs/MODELING.md` X7, `docs/CONVENTIONS.md` section 9). Sections 9 to 12 of `docs/CONVENTIONS.md` become 10 to 13.
- Terms for further gaps (decisions G15 to G20): redundancy schemes and the member class of a redundancy group; part numbers through 223's catalog-number aspect, with no new term; a refrigerant property and the refrigerants R-454B and R-1233zd; the GB200 NVL4 platform and InfiniBand SDR; generic QSFP and Modbus values above the specific ones; a flow coefficient quantity kind with Kv and Cv units; AC media that state the phases but no frequency, above the frequency-specific media.
- Build support for enumeration values under a broader value, media with several parents, quantity kinds in QUDT's pattern, and property classes whose enumeration kind comes from 223.
- The redundancy group definition covers schemes as well as counts.
- The example CDU carries a feature statement; a test checks that a malformed one is reported.
- The project version in `pyproject.toml` is 0.3.0 (it still read 0.1.0).

## 0.2.0 (draft)

- Terms for gaps found while modeling vendor datasheets (`docs/MODELING.md`, decisions G1 to G14): units QUDT lacks (rack unit, open rack unit, gigabaud, terabyte per second, megatransfer per second) and the build support for them; rack space and optical power level; management protocols, copper data connectors, pipe joints, lane modulation, 80 PLUS levels and earthing systems; more add-in card outlines; supported GPU platform; motherboard, server chassis and riser card components; coolant products with generic glycol solution media; EIA-232 and EIA-422 signals; microsecond transfer times and UPS bypass transfers.
- The example GPU server states its rack space and its management port's connector and protocol.

## 0.1.0 (draft)

- First version of the AI Factory Ontology: an extension of Brick 1.4.4 and ASHRAE 223 for AI data centers, covering compute and network, cooling and power equipment.
- Schema generated from Python definitions in `schema/definitions/` by `pipeline/build_schema.py`, with SHACL shapes for the connection points each class needs.
- Cross-cutting patterns: product models, 223 aspects with Required, Recommended and Operating, not-stated records, qualifications, redundancy groups, reference architectures and GPU platforms, provenance by document and page.
- Modeling rules and decisions (`docs/MODELING.md`) and conventions (`docs/CONVENTIONS.md`).
- Fictional example models and 21 competency questions with tests.
