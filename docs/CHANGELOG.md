# Changelog

## 0.2.0 (draft)

- Terms for gaps found while modeling vendor datasheets (`docs/MODELING.md`, decisions G1 to G14): units QUDT lacks (rack unit, open rack unit, gigabaud, terabyte per second, megatransfer per second) and the build support for them; rack space and optical power level; management protocols, copper data connectors, pipe joints, lane modulation, 80 PLUS levels and earthing systems; more add-in card outlines; supported GPU platform; motherboard, server chassis and riser card components; coolant products with generic glycol solution media; EIA-232 and EIA-422 signals; microsecond transfer times and UPS bypass transfers.
- The example GPU server states its rack space and its management port's connector and protocol.

## 0.1.0 (draft)

- First version of the AI Factory Ontology: an extension of Brick 1.4.4 and ASHRAE 223 for AI data centers, covering compute and network, cooling and power equipment.
- Schema generated from Python definitions in `schema/definitions/` by `pipeline/build_schema.py`, with SHACL shapes for the connection points each class needs.
- Cross-cutting patterns: product models, 223 aspects with Required, Recommended and Operating, not-stated records, qualifications, redundancy groups, reference architectures and GPU platforms, provenance by document and page.
- Modeling rules and decisions (`docs/MODELING.md`) and conventions (`docs/CONVENTIONS.md`).
- Fictional example models and 21 competency questions with tests.
