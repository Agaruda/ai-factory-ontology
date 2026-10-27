# Changelog

## 0.1.0 (draft)

- First version of the AI Factory Ontology: an extension of Brick 1.4.4 and ASHRAE 223 for AI data centers, covering compute and network, cooling and power equipment.
- Schema generated from Python definitions in `schema/definitions/` by `pipeline/build_schema.py`, with SHACL shapes for the connection points each class needs.
- Cross-cutting patterns: product models, 223 aspects with Required, Recommended and Operating, not-stated records, qualifications, redundancy groups, reference architectures and GPU platforms, provenance by document and page.
- Modeling rules and decisions (`docs/MODELING.md`) and conventions (`docs/CONVENTIONS.md`).
- Fictional example models and 21 competency questions with tests.
