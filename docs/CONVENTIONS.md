# Data conventions

Version 0.1, draft. How to write the schema and any data that uses it; `tests/` checks what can be checked.

## 1. Standards

| Standard | Used for |
|---|---|
| RDF 1.1, Turtle | all ontology files |
| RDFS, OWL 2 | classes, properties, subclass links; no OWL reasoning is required to use the data |
| SHACL (Core and SHACL-SPARQL) | structure checks |
| SKOS | definitions (`skos:definition`) and term mappings (`skos:exactMatch`, `skos:closeMatch`) |
| PROV-O | where a value came from (`prov:wasDerivedFrom`) |
| Web Annotation Data Model | which part of a document (`oa:SpecificResource`, selectors) |
| QUDT 3.5.3 | units and quantity kinds |
| Brick 1.4.4 | equipment classes, `brick:feeds`, `brick:hasPart`; RealEstateCore terms Brick bundles (`rec:modelNumber`, `rec:manufacturedBy`) |
| ASHRAE 223 (open223 `6fdc11c`) | connection points, connections, media, roles, aspects, properties |

Pinned copies are in `schema/vendor/`. Reuse a term from these standards before defining a new one (`docs/MODELING.md`, rule R2).

## 2. Identifiers

| What | Namespace | Prefix | Example |
|---|---|---|---|
| Schema terms (classes, properties, enumeration values, shapes) | `https://w3id.org/ai-factory#` | `ai-factory:` | `ai-factory:CoolantDistributionUnit` |
| Product models and their parts (connection points, property values) | `https://w3id.org/ai-factory/model/` | `ai-factory-model:` | `ai-factory-model:kentec-cdu-lx480t`, `ai-factory-model:kentec-cdu-lx480t.tcs-supply` |
| Sources | `https://w3id.org/ai-factory/source/` | `ai-factory-source:` | `ai-factory-source:kentec-cdu-lx480t-datasheet` |
| Organizations | `https://w3id.org/ai-factory/org/` | `ai-factory-org:` | `ai-factory-org:kentec` |

- A prefix is only an abbreviation, as Turtle and SPARQL define it (`@prefix ai-factory: <https://w3id.org/ai-factory#> .`); the full IRI is the identifier. Before release we also check the prefixes against prefix.cc for clashes.
- The namespace is provisional: it is not registered with w3id.org yet. Before release we confirm the name with the w3id.org maintainers; if it changes, every file changes in one commit.
- Model, source and organization identifiers are lowercase slugs: vendor, then product, words joined by hyphens, ASCII only. A slug never changes once released; a renamed product keeps its slug and gains a label.
- Parts of a model use the model slug, a dot, and a local name: `ai-factory-model:<model>.<part>`. Local names are lowercase with hyphens.
- Installed units described at run time (for example the rows of a bill of materials) use `urn:ai-factory-bom:<bill>:<row-id>` and are not stored with product data.

## 3. Names, labels and definitions

- Classes: UpperCamelCase (`LiquidToLiquidCDU`). Properties: lowerCamelCase (`hasModel`). Enumeration values follow 223's style, kind then value: `ai-factory:PluggableFormFactor-OSFP`, `ai-factory:InfiniBandGeneration-NDR`.
- Spell abbreviations as the industry writes them inside the name (`CDU`, `UPS`, `PDU`), and spell them out in the label and definition.
- Every schema term has `rdfs:label` and `skos:definition`, both English (`@en`). A definition is one sentence in our own words. The same sentence is also written as `rdfs:comment`, which is where ASHRAE 223 tools look for it.
- Schema terms are written as Python data in `schema/definitions/` and generated into Turtle by `pipeline/build_schema.py`; the generated files are never edited by hand.
- Every product model has `rdfs:label` (the vendor's product name), `rec:modelNumber` and `rec:manufacturedBy`.
- Every new class or property that has a counterpart in Brick or 223 at a coarser level is a subclass or subproperty of it; a counterpart at the same level is reused, not redefined. Mappings to other vocabularies use SKOS mapping properties.

## 4. Files and layout

| File | Contents |
|---|---|
| `schema/ai-factory.ttl` | classes, properties, enumeration values |
| `schema/ai-factory-shapes.ttl` | structure checks: which connection points and values each class needs |
| `<model-slug>.ttl` (product data) | one product model with its connection points, values, provenance, not-stated records and feature statements |

- Turtle files are written by `pipeline/format_ttl.py` (rdflib `longturtle`: sorted subjects, one predicate per line, fixed prefix block, canonical blank-node labels). Do not hand-format; tests reject files that change when reformatted.
- Prefixes are declared once in `schema/definitions/namespaces.py` and used everywhere; a file uses only declared prefixes.

## 5. Product models and installed units

A product model is an individual typed with its equipment class and with `ai-factory:ProductModel`. It stands for the specification every unit of that model shares. Its connection points and property values hang off it.

```turtle
ai-factory-model:kentec-cdu-lx480t a ai-factory:LiquidToLiquidCDU, ai-factory:ProductModel ;
    rdfs:label "CDU-LX480T"@en ;
    rec:modelNumber "CDU-LX480T" ;
    rec:manufacturedBy ai-factory-org:kentec ;
    s223:hasConnectionPoint ai-factory-model:kentec-cdu-lx480t.tcs-supply .
```

An installed unit (a BOM row) is a separate individual of the same class, linked with `ai-factory:hasModel`, and takes the model's specifications. Installed units exist only in BOM graphs at run time.

A component that a product's documents name as fitted (for example a network adapter built into a server) is linked with `brick:hasPart` from the product model to the component's product model.

A part number or ordering code under which the model, or one variant of it, is ordered follows 223's pattern for catalog numbers: an `s223:Property` whose `s223:hasValue` is the code as a string, with `s223:hasAspect s223:Aspect-CatalogNumber`, attached to the model with `s223:hasProperty` and carrying provenance (section 7). For a variant, an `ai-factory:condition` says which variant, in our own words. `rec:modelNumber` stays the model number.

Redundancy of a model's internal units (pumps, power supplies, fans) is an `ai-factory:RedundancyGroup` linked from the model with `ai-factory:hasRedundancyGroup`:

- the units are named by `ai-factory:memberModel`, or by `ai-factory:memberClass` (for example `ai-factory:Pump`) when they have no model of their own; a group that names neither covers the model's units as a whole;
- a scheme printed as a formula (N, N+1, N+N, 2N ...) is `ai-factory:redundancyScheme` with a `RedundancyScheme` value;
- printed counts are `ai-factory:requiredCount` and `ai-factory:installedCount`: "4+1" is 4 required of 5 installed;
- the group carries provenance (section 7);
- a count of units with their rating ("8 x 33 kW") states no redundancy and is not recorded as a redundancy group.

## 6. Connection points, media and values

- Connection points follow 223: an `s223:InletConnectionPoint`, `s223:OutletConnectionPoint` or `s223:BidirectionalConnectionPoint` subclass, exactly one medium (`s223:hasMedium`), and a role where one applies (`s223:hasRole s223:Role-Supply`, `s223:Role-Primary` ...).
- A port that runs more than one protocol takes the closest medium that covers all of them and lists the protocols and rates as enumeration values.
- Values are 223 properties: an `s223:QuantifiableProperty` with `s223:hasValue`, `qudt:hasUnit` and `qudt:hasQuantityKind`, attached with `s223:hasProperty` to the connection point or equipment it describes.
- Units come from QUDT. Where QUDT has none, the schema defines one in QUDT's pattern (`qudt:Unit` with its quantity kinds, symbol and conversion multiplier), named `ai-factory:Unit-<name>`: rack unit, open rack unit, gigabaud, terabyte per second, megatransfer per second, and the Kv and Cv flow coefficients. Where QUDT also lacks the quantity kind, the schema defines it the same way, named `ai-factory:QuantityKind-<name>`: `ai-factory:QuantityKind-FlowCoefficient`.
- What a value means is stated with 223 aspects (`s223:hasAspect`): `s223:Aspect-Rated`, `-Nominal`, `-Maximum`, `-Minimum`, `-HighLimit`, `-LowLimit`, plus ours: `ai-factory:Aspect-Required` (the vendor states it as a need), `ai-factory:Aspect-Recommended`, `ai-factory:Aspect-Operating` (normal operating range, as opposed to a limit range).
- A range is two properties, one with `s223:Aspect-Minimum` and one with `s223:Aspect-Maximum`, sharing the other aspects.
- One connection point record may stand for several identical points (the 48 RJ45 ports of a switch, the 12 C19 receptacles of a PDU): an `ai-factory:ConnectionPointCount` property on it gives the number. A record without one stands for one point.
- A condition printed with a value (for example "at 45 °C coolant") is an `ai-factory:condition` on the property, written in our own words.
- An AC medium names its phases and frequency (`ai-factory:AC-3Ph-50Hz`). When the documents give the phases but no frequency, the medium names the phases only (`ai-factory:AC-1Ph`, `ai-factory:AC-3Ph`, `ai-factory:AC-3PhN`); its frequency is 223's generic `s223:Numerical-Frequency`, as on `s223:Electricity-AC`.
- The coolants a liquid connection point takes are `ai-factory:CoolantProperty` values on the point, one per coolant, each with its provenance; the point's one medium is the most specific medium all of them are or are a kind of (water and 25 percent propylene glycol give `s223:Fluid-Water`). A point that states no coolant has its medium only; `s223:Fluid-Water` alone then means water or an aqueous solution, not plain water.
- A refrigerant is one of 223's refrigerant media (`s223:Refrigerant-R-134A` ...) or one the schema adds in 223's pattern (`ai-factory:Refrigerant-R-454B`). Where refrigerant lines leave the product, the refrigerant is the medium of those connection points; a circuit sealed inside the product is stated with an `ai-factory:RefrigerantProperty` on the model.
- A value the vendor prints as text, not a number (a connector type, a protocol), is an enumeration value from `ai-factory.ttl`. Some enumerations have a generic value above specific ones (`ai-factory:PluggableFormFactor-QSFP` above `-QSFP28`, `ai-factory:ManagementProtocol-Modbus` above `-ModbusRTU`); it is used only when the documents do not say which specific value applies. If no value fits, the value is not recorded and the gap is reported: a property value is never free text. Descriptive text that no structured term holds goes only into a feature statement (section 9).

```turtle
ai-factory-model:kentec-cdu-lx480t.tcs-supply a ai-factory:LiquidOutlet ;
    s223:hasMedium ai-factory:PropyleneGlycolSolution-25Percent ;
    s223:hasRole s223:Role-Secondary, s223:Role-Supply ;
    s223:hasProperty ai-factory-model:kentec-cdu-lx480t.tcs-supply.flow-max .

ai-factory-model:kentec-cdu-lx480t.tcs-supply.flow-max a s223:QuantifiableProperty ;
    qudt:hasQuantityKind quantitykind:VolumeFlowRate ;
    qudt:hasUnit unit:L-PER-MIN ;
    s223:hasValue 480 ;
    s223:hasAspect s223:Aspect-Maximum ;
    prov:wasDerivedFrom [
        a oa:SpecificResource ;
        oa:hasSource ai-factory-source:kentec-cdu-lx480t-datasheet ;
        oa:hasSelector [ a oa:FragmentSelector ;
                         dcterms:conformsTo <http://tools.ietf.org/rfc/rfc3778> ;
                         rdf:value "page=2" ] ] .
```

The example shows the pattern; its numbers and page are placeholders, not data.

## 7. Provenance

- Every property value and every link between models carries `prov:wasDerivedFrom` with one or more `oa:SpecificResource` nodes.
- PDF: `oa:FragmentSelector` with `dcterms:conformsTo <http://tools.ietf.org/rfc/rfc3778>` and `rdf:value "page=N"`, where N is the PDF page index starting at 1, not the number printed on the page.
- Web page or JSON list: `oa:TextPositionSelector` with `oa:start` and `oa:end`, character offsets into the cached Markdown of that source, plus `ai-factory:section` naming the heading in our own words. The cache is pinned by the source's sha256.
- When two documents disagree, both values are recorded, each with its own provenance. Nothing is averaged or chosen at this stage.
- A value derived by combining statements (for example a rack total computed from per-tray values) is marked `ai-factory:basis ai-factory:Basis-Derived` with `ai-factory:reasoning` in our own words; a value read directly is `ai-factory:Basis-Stated`.

## 8. Not stated by the vendor

Absence of a value means nothing in RDF. When a model's documents were read and none states an item a compatibility check needs, an explicit record says so:

```turtle
[] a ai-factory:NotStatedRecord ;
    ai-factory:aboutModel ai-factory-model:nvidia-sn5600 ;
    ai-factory:aboutQuantityKind quantitykind:Voltage ;
    ai-factory:aboutConnectionPointClass ai-factory:PluggableCage ;
    ai-factory:checkedSource ai-factory-source:nvidia-sn5600-user-manual, ai-factory-source:nvidia-sn5600-datasheet .
```

## 9. Feature statements

A descriptive statement about a product model that no structured term holds, such as that its pumps can be replaced while it runs, is a W3C Web Annotation that describes the model. It is never a property value.

```turtle
ai-factory-model:example-cdu-l2l-500.feature-1 a oa:Annotation ;
    oa:motivatedBy oa:describing ;
    oa:hasTarget ai-factory-model:example-cdu-l2l-500 ;
    oa:hasBody [ a oa:TextualBody ;
                 rdf:value "Each of its two circulation pumps can be replaced while the other keeps the unit running."@en ] ;
    prov:wasDerivedFrom [
        a oa:SpecificResource ;
        oa:hasSource ai-factory-source:example-cdu-l2l-500-datasheet ;
        oa:hasSelector [ a oa:FragmentSelector ;
                         dcterms:conformsTo <http://tools.ietf.org/rfc/rfc3778> ;
                         rdf:value "page=1" ] ] .
```

- The identifier is the model's, a dot, `feature-` and a number counted from 1: `ai-factory-model:<model>.feature-<n>`.
- One statement per annotation: exactly one `oa:TextualBody` whose `rdf:value` is English (`@en`).
- The text is written in our own words (section 11). Numbers and units, product names and part numbers are written as printed.
- Every statement carries provenance as in section 7.
- A value that a structured term can hold is recorded with that term; a statement does not replace it.
- No compatibility check reads feature statements.
- `ai-factory-shapes.ttl` checks that every annotation with the describing motivation targets one product model, has one English textual body and cites its source.

## 10. Sources

A source document is an `ai-factory:Source` individual with an English label and `ai-factory:sha256`, the checksum of the original file. Provenance (section 7) points to it. The documents themselves are not part of the ontology.

## 11. Text policy

- The repository holds no sentence copied from a vendor document: not in definitions, labels, conditions, feature statements, notes, documentation or commit messages.
- Allowed: product names, model and part numbers, numbers with units, names of standards, and single technical terms.
- A text that repeats 10 or more consecutive words of a vendor document counts as copied.

## 12. Language and commits

- English only, everywhere in the repository.

## 13. What must pass

| Check | Tool |
|---|---|
| The generated files match `schema/definitions/` | `pipeline/build_schema.py --check` |
| Every IRI a definition points to exists in the pinned standards or the schema | `pipeline/build_schema.py` |
| Every Turtle file parses, together with the pinned standards | rdflib |
| `ai-factory-shapes.ttl` holds for the example models | pySHACL |
| The example models' connection points satisfy 223's own shapes | pySHACL with `ashrae-223.ttl` |
| Every competency question in `tests/competency/` is answered on the example models | SPARQL |
| Files are formatter-stable | `pipeline/format_ttl.py --check` |
