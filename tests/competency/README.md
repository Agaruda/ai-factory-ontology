# Competency questions

The questions the ontology must answer, drawn from the kinds of compatibility check an equipment review makes (connections, coolant, cooling, power, network, optics). Each has a SPARQL query `<id>.rq` run against the example models in `tests/fixtures/` by `tests/test_competency.py`.

## Common

| Id | Question |
|---|---|
| C1 | What kind of equipment is a product model? |
| C2 | Which component models does a product model state it contains? |
| C3 | Is a value a requirement, a capability, a recommendation or a limit, and is a range an operating range or a limit range? |
| C4 | Which document and page does a value come from? |
| C5 | Which items do a model's documents not state, and which documents were checked? |
| C6 | Do two documents give different values for the same item of the same model? |
| C7 | Which qualifications name a model, issued by whom and covering what? |

## Network

| Id | Question |
|---|---|
| N1 | Which protocols and per-port data rates do the data ports of a device, or of the network adapter it contains, support? |
| N2 | Which protocols and per-port data rates do the ports of a switch support? |
| N3 | Which networks does a device need to be connected to? |

## Optics

| Id | Question |
|---|---|
| O1 | What form factor, protocols and data rate does a transceiver or cable plug have, and what supply voltage does it need? |
| O2 | What form factor and protocols does a switch cage accept, and what supply voltage does it provide? |

## Quick-disconnect couplings

| Id | Question |
|---|---|
| Q1 | What coupling type (family and size) and gender does a liquid connection point have? |
| Q2 | Which coupling does each liquid connection of a device use? |

## Coolant

| Id | Question |
|---|---|
| F1 | Which coolants does a device accept, by kind and concentration? |

## Cooling

| Id | Question |
|---|---|
| K1 | What supply temperature range and flow per unit does a liquid-cooled device need? |
| K2 | What supply temperature range, flow and cooling capacity can a CDU or chiller deliver per unit? |
| K3 | Which loop does a device need its coolant from (for example a CDU secondary loop or facility water)? |

## Power

| Id | Question |
|---|---|
| P1 | What voltage, phases, frequency and connector does a power inlet accept? |
| P2 | What voltage, phases, frequency and outlet type does a power outlet deliver? |
| P3 | Which frequencies does a device accept, where a single printed frequency means that frequency only? |
