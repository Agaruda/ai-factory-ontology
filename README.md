# AI Factory Ontology

An extension of [Brick](https://brickschema.org/) 1.4.4 and [ASHRAE Standard 223](https://open223.info/) for AI data centers: GPU servers and rack-scale systems, the network that connects them, and the liquid-cooling and power equipment around them.

**Status:** 0.4.0, draft. The namespace `https://w3id.org/ai-factory#` is provisional and not yet registered.

## What it covers

| Domain | Examples |
|---|---|
| Compute and network | servers and compute trays, rack-scale systems, InfiniBand, Ethernet and NVLink switches, network adapters, optical transceivers and cables |
| Cooling | coolant distribution units, manifolds and quick-disconnect couplings, chillers, cooling towers, dry coolers, CRAH units, rear-door heat exchangers |
| Power | generator sets, medium- and low-voltage switchgear, transformers, transfer switches, UPS, busways, PDUs, power shelves |

Equipment classes take their identity from Brick and their connections from 223: every class has connection points with a medium (coolant, air, alternating or direct current, network signals), and values such as flow, temperature, voltage or data rate sit on the connection point they describe, with 223 aspects saying whether a value is a rating, a requirement or a limit. A product model is an individual of its class, so the same structure describes any vendor's product. Every value can point to the document and page it came from.

## Layout

| Path | Contents |
|---|---|
| `schema/definitions/` | the schema as Python data, the way Brick keeps its definitions; edit these, never the generated files |
| `schema/ai-factory.ttl` | the generated ontology: classes, properties, enumerations, media |
| `schema/ai-factory-shapes.ttl` | generated SHACL shapes: which connection points and values each class needs |
| `schema/vendor/` | pinned copies of the standards it extends, with their licenses |
| `pipeline/` | `build_schema.py` (definitions to Turtle), `format_ttl.py` (fixed Turtle layout) |
| `docs/MODELING.md` | the modeling rules and the decisions made with them |
| `docs/CONVENTIONS.md` | how to write the schema and data that uses it: identifiers, connection points, values, provenance |
| `tests/fixtures/` | fictional example product models |
| `tests/competency/` | the competency questions the ontology must answer, as SPARQL |

## Use

```sh
uv sync                                          # Python 3.12 and uv
uv run python pipeline/build_schema.py           # regenerate the ontology and shapes from the definitions
uv run python pipeline/format_ttl.py <files>     # write Turtle in the fixed layout
uv run pytest                                    # tests; add -m slow for ASHRAE 223's own shapes (a few minutes)
```

The generated files load with the pinned Brick and 223 in any RDF or SHACL tool; no code from this repository is needed to read them.

## Contributing

English only, in code, documents, labels and definitions. Definitions are written in our own words: no text copied from vendor documents (`docs/CONVENTIONS.md`, section 11).

## License

Apache License 2.0 (`LICENSE`). The pinned standards under `schema/vendor/` keep their own licenses (`schema/vendor/README.md`).
