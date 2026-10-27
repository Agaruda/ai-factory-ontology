# Modeling rules

Version 0.1, draft.

W3C Recommendations (RDF, RDFS, OWL 2, SHACL, SKOS) define how to state classes, properties and individuals. They do not say whether a given domain variant should be a subclass or a property value. The rules below combine three bases, in this order:

1. The two standards we extend: Brick 1.4.4 for what equipment is, ASHRAE 223 for how it connects.
2. W3C guidance on modeling patterns:
   - Data on the Web Best Practices (W3C Recommendation, 2017), Best Practice 15: reuse vocabularies, preferably standardized ones.
   - Representing Classes As Property Values on the Semantic Web (W3C Working Group Note, 2005).
   - Representing Specified Values in OWL: value partitions and value sets (W3C Working Group Note, 2005).
   - Defining N-ary Relations on the Semantic Web (W3C Working Group Note, 2006).
3. The purpose of the ontology: deciding whether two pieces of equipment are compatible at their connections.

## Rules

| Rule | Statement | Basis |
|---|---|---|
| R1 | Every equipment class is a subclass of the most specific Brick class that fits; otherwise of the Brick branch class (`brick:HVAC_Equipment`, `brick:Electrical_Equipment`, `brick:ICT_Equipment`). | decision: Brick for what equipment is |
| R2 | Reuse before inventing: when Brick or 223 already has a term or a pattern for the same thing, use it. | Data on the Web Best Practices, BP 15 |
| R3 | Make a new subclass only when (a) the kind has a different set of connection points or media, or (b) an industry product standard defines it as a separate equipment type. Otherwise the variant is an enumeration value of a property. Never turn two independent axes into a cross-product of classes. | Classes As Property Values note; 223 shapes are attached per class, so connection points decide the class |
| R4 | A finite named set of values defined by a standard or a product family (form factors, InfiniBand generations, ASHRAE water classes, battery chemistries, duty ratings, construction types) is a set of enumeration individuals, following 223's `EnumerationKind` pattern. A measurable value is a QUDT quantity with value or min/max. A named class with numeric meaning (W32) is an enumeration individual that carries its range. | Value partitions and value sets note (value sets); 223 |
| R5 | A relation that carries its own attributes (who qualified it, under which firmware, from which document) is an individual of a relation class. | N-ary Relations note, pattern 1 |
| R6 | One model number sold as one product is Equipment; what is inside it is a Component linked by `brick:hasPart`; a design-level grouping of several products is an `s223:System`; a whole site is a `brick:Site`. | Brick and 223 usage |
| R7 | Attach each value to the entity it describes: a port rate to the port, a rack total to the rack. Qualifiers of a value (rated, standby duty, operating or limit range) are 223 aspects on that value. | 223 `hasAspect` |
| R8 | Where Brick and 223 disagree: flows and connections follow 223 (roles on connection points), equipment identity follows Brick; a unit sold separately stays Equipment. | decision: Brick + 223 split |
| R9 | Scope: include a term when a compatibility check compares it, or when it names AI-factory equipment, a component, a connection or a medium. Leave out quality-control data and internals that never form an interface. Scope calls are made by the project lead. | decision: whole AI-factory domain |

### How R1, R2 and R8 combine for equipment classes

An equipment class needs a Brick parent (what it is) and a 223 parent (so it can have connection points). Where Brick and 223 both name the same kind of equipment (for example `brick:Ethernet_Switch` and `s223:EthernetSwitch`), we define one class that is a subclass of both rather than asking every product model to carry two types. That class adds nothing else to the meaning; it joins the two standards and is where our shapes attach. Where only one standard names the kind, the other parent is the closest broader class (`s223:Equipment`, or `brick:HVAC_Equipment`, `brick:Electrical_Equipment`, `brick:ICT_Equipment`).

## Decisions on the open questions from the domain inventory

The domain inventory (543 terms over compute and network, cooling and power, read from about 290 vendor documents) raised 30 modeling questions. Each is decided by the rules above; scope calls were made by the project lead.

### Compute and network

| # | Question | Decision | Rule |
|---|---|---|---|
| CN1 | IMEX channel/domain | Out of scope: a software construct with no physical interface. | R9, scope decision 2026-10-27 |
| CN2 | Qualification at five scopes | One relation class `Qualification` with a scope enumeration (component pairing, validated configuration, certified system, qualified catalog entry, endorsed design), the qualifying party, the items, firmware where stated, and the source document. | R5, R4 |
| CN3 | InfiniBand and NVLink | Follow 223's Ethernet pattern: new signal media (InfiniBand with a generation enumeration, NVLink) beside 223's Ethernet media; `InfiniBandSwitch` beside `EthernetSwitch` (different media). 223 allows one medium per connection point, so a port that runs either protocol takes the closest common medium and lists its supported protocols and rates as enumeration values. | R2, R3, R4 |
| CN4 | Director-class modular switch | Not a subclass: a form property (fixed / modular chassis); line cards are Components via `hasPart`. | R3, R6 |
| CN5 | Compute tray vs switch tray | Two classes: compute trays carry GPUs and network adapter ports, NVLink switch trays carry NVLink switch ports. Air or liquid cooling is not a class difference: both come in both forms, so a product states its `CoolingMethod`. | R3 (no cross-product) |
| CN6 | GPU baseboard vs superchip | Sibling Component classes under one parent `GPUModule`. | R3, R6 |
| CN7 | SuperNIC vs DPU | `DPU` is a subclass of `NetworkAdapter` (it adds a management port); SuperNIC is a function value of `NetworkAdapter`. | R3 |
| CN8 | Fiber type | 223's fiber cable classes (`s223:FiberOpticCable-OM4` ...) are connections, not equipment, so they cannot carry connection points. A fiber cable product is one `FiberCable` class with a `FiberGrade` enumeration (OM3, OM4, OM5, OS2) whose members map to the 223 classes with `skos:closeMatch`; a grade can then also qualify a reach value as an aspect. | R2, R3, R4 |
| CN9 | Per-unit vs aggregate quantities | Each value sits on the entity it describes (per port on the port, per GPU on the GPU, per rack on the rack). | R7 |
| CN10 | Pod, POD, AI factory | `ScalableUnit` and `Pod` as `s223:System` subclasses; an AI factory is a `brick:Site`. | R6 |

### Cooling

| # | Question | Decision | Rule |
|---|---|---|---|
| C1 | CDU primary/secondary side | 223 roles `s223:Role-Primary` / `s223:Role-Secondary` on the CDU's connection points. | R2 |
| C2 | Condenser, evaporator, economizer | Inside a chiller: 223 roles on its internal heat exchangers. Sold separately (remote air-cooled condenser): Equipment. | R8, R6 |
| C3 | PG25 | Follow 223's glycol pattern: a new medium for 25 % propylene glycol solution. A device that accepts a concentration range states it as a quantity range on its connection point. | R2, R4 |
| C4 | ASHRAE water classes | Enumeration individuals, each carrying its supply-temperature range. | R4 |
| C5 | ATD | A property of heat-exchanging equipment in general (CDU, plate heat exchanger, sidecar), not CDU only. | R7 |
| C6 | CDU axes | Liquid-to-liquid vs liquid-to-air are subclasses (facility-water connection vs air intake); in-rack / in-row / facility-scale is a property. | R3 |
| C7 | Quick-disconnect series, size, gender | Two enumeration properties on the coupling's connection point: the coupling type, which combines family and size because compatibility checks treat them together as the mating key (for example OCP UQD08, Danfoss FD83 1-inch), and the gender (plug, socket, or genderless for families whose two halves are identical). Mating across coupling types is not modeled; different types do not mate. | R4 |
| C8 | Rear-door heat exchanger, in-row cooler | Grouped with CRAH under one parent for units that cool air with a liquid loop. | R3, R1 |
| C9 | Coolant chemistry (pH, alkalinity, viscosity ...) | Leave out for now: quality-control data, not compared by any check. | R9, scope decision 2026-10-27 |
| C10 | Fan-coil wall vs CRAH | Same connection points: a CRAH with a form property, not a subclass. | R3 |

### Power

| # | Question | Decision | Rule |
|---|---|---|---|
| P1 | Redundancy such as "4 to make 3" | Two integer quantities (installed units, units needed) on a redundancy-group relation individual. | R5, R4 |
| P2 | DC battery bus | The DC electricity is a medium; the busbar terminal is a connection point with that medium. | R2 |
| P3 | Genset internals | The genset is one Equipment; engine and alternator are Components. Governor, AVR and exciter are left out. | R6, R9, scope decision 2026-10-27 |
| P4 | Standby / prime / continuous duty | An aspect of the rated-power value (each duty has its own rating). | R7 |
| P5 | BESS | Equipment when sold as one model (Brick `Battery_Energy_Storage_System`); a System when assembled from several products. | R2, R6 |
| P6 | Solid-state transformer | A subclass of `s223:ElectricEnergyConverter`, sibling of transformers (it has a DC output). | R2, R3 |
| P7 | Switchgear construction (metal-clad, gas-insulated ...) | Enumeration property, not subclasses. | R3, R4 |
| P8 | Primary/secondary for windings | Reuse 223 roles. | R2 |
| P9 | 800 VDC power rack, row power center, DC power block | Classes split by input and output media (LV AC in vs MV AC in, 800 VDC out); within one split, a property. | R3 |
| P10 | Panelboard, switchboard, floor PDU | Separate classes: separate product standards define them. | R3(b) |

## Cross-cutting patterns

| # | Topic | Decision | Basis |
|---|---|---|---|
| X1 | Product model vs installed unit | A product model is an individual typed with its equipment class and `ai-factory:ProductModel` (it stands for the specification every unit of the model shares, a deliberate simplification so Brick and 223 shapes apply to it directly); its connection points and specification values hang off it. An installed unit (a BOM row) is a separate individual of the same class linked by `hasModel`, and takes the model's specifications. Model number and manufacturer use the RealEstateCore terms Brick 1.4.4 bundles (`rec:modelNumber`, `rec:manufacturedBy`). Neither Brick nor 223 has a product-model entity. | R2, R6 |
| X2 | Requirement, capability, recommendation, operating and limit ranges | Values carry 223 aspects (`Aspect-Rated`, `-Nominal`, `-Maximum`, `-Minimum`, `-HighLimit`, `-LowLimit`); add the missing members `Aspect-Required`, `Aspect-Recommended`, `Aspect-Operating` to 223's aspect enumeration. | R2, R4, R7 |
| X3 | "Not stated by the vendor" | An explicit record: model, property, the documents checked. Under RDF's open-world reading a missing value means nothing, so absence alone cannot support NEEDS_INFO. | R5 |
| X4 | Provenance | `prov:wasDerivedFrom` (PROV-O, W3C Recommendation) to a W3C Web Annotation specific resource: the source document plus a fragment selector `page=N` conforming to RFC 3778 (PDF fragment identifiers), or a text position selector into the cached Markdown of a web page. No document text. | W3C PROV-O, W3C Web Annotation Data Model |
| X5 | Quantities | 223 properties with `s223:hasValue` and a QUDT unit; ranges as a minimum and a maximum property with the matching aspects. | R2 |
| X6 | Reference architectures | A `ReferenceArchitecture` individual carries its `gpuPlatform` (a `GPUPlatform` enumeration value) and `computeFabric` (a `NetworkProtocol` value), and links with `hasReferenceRole` to `ReferenceRole` individuals, each naming a `roleClass` and, where the class alone is too broad, a `roleFunction` (for example an Ethernet switch for out-of-band management). Every architecture and role carries provenance. A product states its platform with a `GPUPlatformProperty`. | R5, R4 |

Out of scope for now (2026-10-27): IMEX, coolant chemistry, genset governor, automatic voltage regulator and exciter.

The patterns are written out with examples in `CONVENTIONS.md`.
