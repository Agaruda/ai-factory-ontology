"""Cooling domain: liquid cooling at the rack and row, air cooling in the hall, and facility heat rejection.

Connection points come from common.py (LiquidInlet, LiquidOutlet, AirInlet, AirOutlet, PowerInlet,
DataPort) or straight from 223 (s223:InletConnectionPoint and s223:OutletConnectionPoint for refrigerant
lines, s223:BidirectionalConnectionPoint where fluid moves both ways). Which loop a liquid connection point
belongs to is a 223 role: Role-Primary / Role-Secondary on CDUs (decision C1), Role-Evaporator /
Role-Condenser on chillers (decision C2), Role-Supply / Role-Return for direction where a device has
more than one loop. See docs/MODELING.md, decisions C1 to C10.
"""

from .namespaces import AIF, BRICK, QK, S223, UNIT

WATER = S223["Fluid-Water"]  # covers chilled water, glycol solutions and the 25 percent PG medium
AIR = S223["Fluid-Air"]
REFRIGERANT = S223["Constituent-Refrigerant"]


def _liquid_pair(subject: str, medium=None, roles_in=(), roles_out=(), what: str = "liquid") -> list[dict]:
    """An inlet and an outlet for one liquid loop."""
    inlet = {"class": AIF.LiquidInlet, "min": 1,
             "message": f"{subject} has at least one {what} inlet."}
    outlet = {"class": AIF.LiquidOutlet, "min": 1,
              "message": f"{subject} has at least one {what} outlet."}
    if medium is not None:
        inlet["medium"] = outlet["medium"] = medium
    if roles_in:
        inlet["roles"] = list(roles_in)
    if roles_out:
        outlet["roles"] = list(roles_out)
    return [inlet, outlet]


def _air_pair(subject: str) -> list[dict]:
    """An air intake and an air discharge."""
    return [
        {"class": AIF.AirInlet, "medium": AIR, "min": 1,
         "message": f"{subject} has at least one air intake."},
        {"class": AIF.AirOutlet, "medium": AIR, "min": 1,
         "message": f"{subject} has at least one air discharge."},
    ]


# ---------------------------------------------------------------------------------------------
# Equipment

EQUIPMENT = {
    "CoolantDistributionUnit": {
        "label": "Coolant distribution unit",
        "definition": "Equipment that pumps coolant around a technology cooling loop serving liquid-cooled computing equipment and removes that loop's heat through an internal heat exchanger, keeping the loop separate from whatever carries the heat away.",
        "parents": [BRICK.HVAC_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.LiquidOutlet, "medium": WATER, "roles": [S223["Role-Secondary"], S223["Role-Supply"]], "min": 1,
             "message": "A coolant distribution unit has at least one secondary supply outlet that sends coolant to the technology cooling loop."},
            {"class": AIF.LiquidInlet, "medium": WATER, "roles": [S223["Role-Secondary"], S223["Role-Return"]], "min": 1,
             "message": "A coolant distribution unit has at least one secondary return inlet that takes warm coolant back from the technology cooling loop."},
        ],
        "subclasses": {
            "LiquidToLiquidCDU": {
                "label": "Liquid-to-liquid coolant distribution unit",
                "definition": "A coolant distribution unit that passes the heat of its technology cooling loop to a facility water loop through a liquid-to-liquid heat exchanger.",
                "connection_points": [
                    {"class": AIF.LiquidInlet, "medium": WATER, "roles": [S223["Role-Primary"], S223["Role-Supply"]], "min": 1,
                     "message": "A liquid-to-liquid coolant distribution unit has at least one primary supply inlet for facility water."},
                    {"class": AIF.LiquidOutlet, "medium": WATER, "roles": [S223["Role-Primary"], S223["Role-Return"]], "min": 1,
                     "message": "A liquid-to-liquid coolant distribution unit has at least one primary return outlet for facility water."},
                ],
            },
            "LiquidToAirCDU": {
                "label": "Liquid-to-air coolant distribution unit",
                "definition": "A coolant distribution unit that passes the heat of its technology cooling loop to the surrounding air through its own coils and fans, often standing as a sidecar beside the racks it serves where no facility water is available.",
                "connection_points": _air_pair("A liquid-to-air coolant distribution unit"),
            },
        },
    },
    "CoolantManifold": {
        "label": "Coolant manifold",
        "definition": "A header that splits one coolant line into many branch connections, or gathers many branches back into one line, for the trays and devices of a rack or a row.",
        "parents": [BRICK.HVAC_Equipment, S223.Equipment],
        "connection_points": _liquid_pair("A coolant manifold", what="coolant"),
    },
    "ImmersionTank": {
        "label": "Immersion tank",
        "definition": "A tank filled with dielectric liquid in which servers or other electronics are fully submerged so that the liquid takes their heat by direct contact.",
        "parents": [BRICK.Tank, S223.Equipment],
        "connection_points": _liquid_pair("An immersion tank", what="liquid"),
    },
    "LiquidCooledAirCooler": {
        "label": "Liquid-cooled air cooler",
        "definition": "Equipment that cools air passing over a coil fed by a facility or technology water loop, so that the heat taken from the air leaves in the liquid.",
        "parents": [BRICK.HVAC_Equipment, S223.Equipment],
        "connection_points": _liquid_pair("A liquid-cooled air cooler", medium=WATER, what="water")
        + _air_pair("A liquid-cooled air cooler"),
        "subclasses": {
            "CRAH": {
                "label": "Computer room air handler",
                "definition": "A liquid-cooled air cooler with fans that serves a whole data hall, drawing warm room air over a chilled-water coil and returning it cooled, with no compressor of its own.",
                "parents": [BRICK.CRAH, S223.AirHandlingUnit],
            },
            "InRowCooler": {
                "label": "In-row cooler",
                "definition": "A liquid-cooled air cooler with fans that stands in a row of racks, taking hot-aisle air and delivering cooled air to the neighbouring racks.",
                "parents": [S223.AirHandlingUnit],
            },
            "RearDoorHeatExchanger": {
                "label": "Rear-door heat exchanger",
                "definition": "A liquid-cooled air cooler built into or mounted as the rear door of a rack, cooling the rack's exhaust air before it reaches the room.",
                "subclasses": {
                    "ActiveRearDoorHeatExchanger": {
                        "label": "Active rear-door heat exchanger",
                        "definition": "A rear-door heat exchanger with powered fans of its own that pull the rack's exhaust air through its coil.",
                        "connection_points": [
                            {"class": AIF.PowerInlet, "min": 1,
                             "message": "An active rear-door heat exchanger has at least one power inlet for its fans."},
                        ],
                    },
                    "PassiveRearDoorHeatExchanger": {
                        "label": "Passive rear-door heat exchanger",
                        "definition": "A rear-door heat exchanger without fans or a power supply, relying on the airflow of the servers and switches in the rack to push air through its coil.",
                    },
                },
            },
        },
    },
    "CRAC": {
        "label": "Computer room air conditioner",
        "definition": "A room air cooling unit for a data hall that cools air with its own refrigerant compressor circuit rather than with a chilled-water loop.",
        "parents": [BRICK.CRAC, S223.AirHandlingUnit],
        "connection_points": _air_pair("A computer room air conditioner"),
    },
    "AirCooledCondenser": {
        "label": "Air-cooled condenser",
        "definition": "An outdoor coil with fans, sold separately from the unit holding the compressor, that condenses that unit's refrigerant by passing its heat to ambient air.",
        "parents": [BRICK.Condenser_Heat_Exchanger, S223.Equipment],
        "connection_points": [
            {"class": S223.InletConnectionPoint, "medium": REFRIGERANT, "min": 1,
             "message": "An air-cooled condenser has at least one refrigerant inlet."},
            {"class": S223.OutletConnectionPoint, "medium": REFRIGERANT, "min": 1,
             "message": "An air-cooled condenser has at least one refrigerant outlet."},
        ] + _air_pair("An air-cooled condenser"),
    },
    "Chiller": {
        "label": "Chiller",
        "definition": "A machine that cools a water or glycol loop with a refrigeration cycle and rejects the heat to air or to a condenser water loop.",
        "parents": [BRICK.Chiller, S223.Chiller],
        "connection_points": _liquid_pair("A chiller", medium=WATER, roles_in=[S223["Role-Evaporator"]],
                                          roles_out=[S223["Role-Evaporator"]], what="chilled-water"),
        "subclasses": {
            "AirCooledChiller": {
                "label": "Air-cooled chiller",
                "definition": "A chiller that rejects its condenser heat straight to outdoor air through its own coils and fans.",
                "parents": [BRICK.Air_Cooled_Chiller],
                "connection_points": _air_pair("An air-cooled chiller"),
            },
            "WaterCooledChiller": {
                "label": "Water-cooled chiller",
                "definition": "A chiller that rejects its condenser heat to a condenser water loop, which a cooling tower or dry cooler in turn cools.",
                "parents": [BRICK.Water_Cooled_Chiller],
                "connection_points": _liquid_pair("A water-cooled chiller", medium=WATER, roles_in=[S223["Role-Condenser"]],
                                                  roles_out=[S223["Role-Condenser"]], what="condenser water"),
            },
        },
    },
    "DryCooler": {
        "label": "Dry cooler",
        "definition": "An outdoor unit that cools a closed water or glycol loop with finned coils and fans, without evaporating any water.",
        "parents": [BRICK.Dry_Cooler, S223.Equipment],
        "connection_points": _liquid_pair("A dry cooler", medium=WATER, what="process fluid") + _air_pair("A dry cooler"),
        "subclasses": {
            "AdiabaticCooler": {
                "label": "Adiabatic cooler",
                "definition": "A dry cooler with wetted pads or sprays that pre-cool the incoming air by evaporation in hot weather, which needs a separate water supply besides the loop being cooled.",
                "connection_points": [
                    {"class": AIF.LiquidInlet, "medium": WATER, "min": 2,
                     "message": "An adiabatic cooler has an inlet for the process fluid and a separate water inlet for its pre-cooling pads or sprays."},
                ],
            },
        },
    },
    "CoolingTower": {
        "label": "Cooling tower",
        "definition": "A heat rejection unit that cools water toward the outdoor wet-bulb temperature by evaporating part of it into a stream of air.",
        "parents": [BRICK.Cooling_Tower, S223.CoolingTower],
        "connection_points": _liquid_pair("A cooling tower", medium=WATER, what="water"),
    },
    "LiquidToLiquidHeatExchanger": {
        "label": "Liquid-to-liquid heat exchanger",
        "definition": "A heat exchanger that moves heat from one liquid stream to another through a wall, without the two liquids mixing.",
        "parents": [BRICK.Heat_Exchanger, S223.HydronicHeatExchanger],
        "connection_points": [
            {"class": AIF.LiquidInlet, "min": 2,
             "message": "A liquid-to-liquid heat exchanger has an inlet on each of its two sides."},
            {"class": AIF.LiquidOutlet, "min": 2,
             "message": "A liquid-to-liquid heat exchanger has an outlet on each of its two sides."},
        ],
    },
    "Pump": {
        "label": "Pump",
        "definition": "A machine that drives a liquid around a loop by drawing it in at an inlet and pushing it out at an outlet under higher pressure.",
        "parents": [BRICK.Pump, S223.Pump],
        "connection_points": _liquid_pair("A pump"),
    },
    "ExpansionTank": {
        "label": "Expansion tank",
        "definition": "A tank on a closed liquid loop that takes up the change in liquid volume as temperature varies, keeping the loop pressure within limits.",
        "parents": [BRICK.Thermal_Expansion_Tank, S223.Equipment],
        "connection_points": [
            {"class": S223.BidirectionalConnectionPoint, "medium": WATER, "min": 1,
             "message": "An expansion tank has at least one connection through which loop liquid flows in and out."},
        ],
    },
    "PressurizationUnit": {
        "label": "Pressurization unit",
        "definition": "A packaged set of pumps, usually with a duty and a standby pump and a feed tank, that keeps the static pressure of a closed liquid loop by topping it up.",
        "parents": [BRICK.HVAC_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.LiquidInlet, "medium": WATER, "min": 1,
             "message": "A pressurization unit has at least one inlet for make-up water."},
            {"class": AIF.LiquidOutlet, "medium": WATER, "min": 1,
             "message": "A pressurization unit has at least one outlet that feeds the loop it keeps pressurized."},
        ],
    },
    "ThermalEnergyStorageTank": {
        "label": "Thermal energy storage tank",
        "definition": "An insulated tank of chilled or process water held in reserve so that cooling continues through load peaks or a short loss of chiller capacity.",
        "parents": [BRICK.Thermal_Energy_Storage_Tank, S223.ThermalEnergyStorageUnit],
        "connection_points": _liquid_pair("A thermal energy storage tank", medium=WATER, what="water"),
    },
    "Valve": {
        "label": "Valve",
        "definition": "A device in a liquid loop that stops, regulates, diverts or releases flow by opening or closing a passage.",
        "parents": [BRICK.HVAC_Valve, S223.Valve],
        "connection_points": [
            {"class": AIF.LiquidInlet, "min": 1, "message": "A valve has at least one liquid inlet."},
        ],
    },
    "LiquidFilter": {
        "label": "Liquid filter",
        "definition": "A strainer or filter element in a liquid loop that stops particles above a rated size before they reach pumps, heat exchangers or cold plates.",
        "parents": [BRICK.Filter, S223.Filter],
        "connection_points": _liquid_pair("A liquid filter"),
    },
    "FlowMeter": {
        "label": "Flow meter",
        "definition": "A device that measures the volume flow rate of liquid in a loop, for example by an induced magnetic field or by ultrasound.",
        "parents": [BRICK.Sensor_Equipment, S223.Equipment],
        "close_match": [S223.FlowSensor],
    },
    "LeakDetector": {
        "label": "Leak detector",
        "definition": "A sensing cable or spot sensor with its monitor that detects escaped coolant under racks, along pipes or inside a cooling unit and raises an alarm.",
        "parents": [BRICK.Leak_Detector_Equipment, S223.Equipment],
    },
}

# ---------------------------------------------------------------------------------------------
# Components: fitted inside or onto another product and linked with brick:hasPart.

COMPONENTS = {
    "ColdPlate": {
        "label": "Cold plate",
        "definition": "A metal plate with internal coolant channels mounted on a processor, accelerator or switch chip so that coolant flowing through it takes the chip's heat.",
        "parents": [BRICK.Heat_Exchanger, S223.Equipment],
        "connection_points": _liquid_pair("A cold plate", what="coolant"),
    },
    "QuickDisconnectCoupling": {
        "label": "Quick-disconnect coupling",
        "definition": "A self-sealing coupling half, or a pair of halves, that joins or separates a liquid line by hand or by sliding a tray into a rack, with little or no spillage.",
        "parents": [BRICK.HVAC_Equipment, S223.Equipment],
        "connection_points": [
            {"class": S223.BidirectionalConnectionPoint, "min": 1,
             "message": "A quick-disconnect coupling has a mating end, recorded as a connection point that carries the coupling type and gender."},
        ],
    },
    "CDUModule": {
        "label": "Coolant distribution unit module",
        "definition": "A field-replaceable section of a modular coolant distribution unit that is built and serviced as one assembly.",
        "parents": [BRICK.HVAC_Equipment, S223.Equipment],
        "subclasses": {
            "CDUPumpModule": {
                "label": "Coolant distribution unit pump module",
                "definition": "A coolant distribution unit module holding one or more circulation pumps for the technology cooling loop, often with its own strainer and flow meter.",
                "parents": [BRICK.Pump, S223.Pump],
                "connection_points": _liquid_pair("A coolant distribution unit pump module", medium=WATER,
                                                  roles_in=[S223["Role-Secondary"]], roles_out=[S223["Role-Secondary"]],
                                                  what="secondary coolant"),
            },
            "CDUControlModule": {
                "label": "Coolant distribution unit control module",
                "definition": "A coolant distribution unit module holding the controllers that run the pumps and valves of one or more pump modules and report to the building or data center management system.",
                "parents": [BRICK.Controller, S223.Controller],
                "connection_points": [
                    {"class": AIF.DataPort, "min": 1,
                     "message": "A coolant distribution unit control module has at least one data port for monitoring and control."},
                ],
            },
            "CDUHydronicsModule": {
                "label": "Coolant distribution unit hydronics module",
                "definition": "A coolant distribution unit module holding the expansion tank, make-up reservoir and fill pump that keep the technology cooling loop full and pressurized.",
                "connection_points": [
                    {"class": S223.BidirectionalConnectionPoint, "medium": WATER, "roles": [S223["Role-Secondary"]], "min": 1,
                     "message": "A coolant distribution unit hydronics module has at least one connection to the secondary loop it keeps full."},
                ],
            },
        },
    },
    "Fan": {
        "label": "Fan",
        "definition": "A motor-driven rotor that moves air through the coil or fill of a cooling unit, such as a computer room air handler, dry cooler or cooling tower.",
        "parents": [BRICK.Fan, S223.Fan],
        "connection_points": _air_pair("A fan"),
    },
}

# ---------------------------------------------------------------------------------------------
# Enumerations

ENUMERATIONS = {
    "CoolingPlacement": {
        "label": "Cooling equipment placement",
        "definition": "Where a coolant distribution unit or coolant manifold sits relative to the racks it serves.",
        "values": {
            "InRack": {"label": "In rack", "definition": "Mounted inside one rack and serving only that rack."},
            "InRow": {"label": "In row", "definition": "Standing in a row of racks, between them or as a sidecar beside one rack, and serving one or more nearby racks."},
            "Facility": {"label": "Facility", "definition": "Installed in a mechanical room, service gallery or plant area and serving many rows or a whole data hall."},
        },
    },
    "CouplingType": {
        "label": "Coupling type",
        "definition": "The mating interface of a quick-disconnect coupling, combining its series and size, so that two halves can mate only when they share the same value.",
        "values": {
            "OCP-UQD02": {"label": "OCP UQD02", "definition": "The Open Compute Project Universal Quick Disconnect (UQD) at dash size 02, a 1/8 inch nominal bore, whose halves mate across makers."},
            "OCP-UQD04": {"label": "OCP UQD04", "definition": "The Open Compute Project Universal Quick Disconnect (UQD) at dash size 04, a 1/4 inch nominal bore, whose halves mate across makers."},
            "OCP-UQD06": {"label": "OCP UQD06", "definition": "The Open Compute Project Universal Quick Disconnect (UQD) at dash size 06, a 3/8 inch nominal bore, whose halves mate across makers."},
            "OCP-UQD08": {"label": "OCP UQD08", "definition": "The Open Compute Project Universal Quick Disconnect (UQD) at dash size 08, a 1/2 inch nominal bore, whose halves mate across makers."},
            "OCP-UQDB04": {"label": "OCP UQDB04", "definition": "The Open Compute Project blind-mate Universal Quick Disconnect (UQDB) at dash size 04, built with a lead-in so that it couples as a tray slides into the rack."},
            "OCP-BMQC": {"label": "OCP BMQC", "definition": "The Open Compute Project Open Rack V3 blind-mate quick connector (BMQC), a single-size plug and socket that couple as a tray slides into the rack."},
            "DanfossFD83-1in": {"label": "Danfoss Hansen FD83 1 inch", "definition": "The Danfoss Hansen FD83 series coupling with a 1 inch body, made of two identical halves rather than a plug and a socket."},
            "DanfossFD83-2in": {"label": "Danfoss Hansen FD83 2 inch", "definition": "The Danfoss Hansen FD83 series coupling with a 2 inch body, made of two identical halves rather than a plug and a socket."},
            "StaubliSCG03": {"label": "Staubli SCG03", "definition": "The Staubli SCG series coupling with a 3 mm nominal diameter."},
            "StaubliSCG06": {"label": "Staubli SCG06", "definition": "The Staubli SCG series coupling with a 6 mm nominal diameter."},
            "StaubliSCG09": {"label": "Staubli SCG09", "definition": "The Staubli SCG series coupling with a 9 mm nominal diameter."},
            "StaubliSCG12": {"label": "Staubli SCG12", "definition": "The Staubli SCG series coupling with a 12 mm nominal diameter."},
            "NittoKohkiCZL-1": {"label": "Nitto Kohki CZL size 1", "definition": "The Nitto Kohki CZL series hand-mate non-spill coupling in size 1."},
            "NittoKohkiCZL-2": {"label": "Nitto Kohki CZL size 2", "definition": "The Nitto Kohki CZL series hand-mate non-spill coupling in size 2."},
            "NittoKohkiCZLBM-1": {"label": "Nitto Kohki CZLBM size 1", "definition": "The Nitto Kohki CZLBM series blind-mate non-spill coupling in size 1."},
            "NittoKohkiCZLBM-2": {"label": "Nitto Kohki CZLBM size 2", "definition": "The Nitto Kohki CZLBM series blind-mate non-spill coupling in size 2."},
        },
    },
    "CRAHForm": {
        "label": "Computer room air handler form",
        "definition": "The physical forms in which computer room air handlers are built.",
        "values": {
            "Perimeter": {"label": "Perimeter unit", "definition": "A floor-standing cabinet placed along the edge of the data hall or in a service gallery."},
            "FanCoilWall": {"label": "Fan coil wall", "definition": "A wall of coils and fans built into the boundary between a data hall and a service corridor, cooling hall air across its whole face."},
        },
    },
    "ImmersionPhase": {
        "label": "Immersion phase",
        "definition": "Whether the dielectric liquid of an immersion tank stays liquid or boils as it takes heat.",
        "values": {
            "SinglePhase": {"label": "Single phase", "definition": "The dielectric liquid stays liquid and is pumped through a heat exchanger to give up its heat."},
            "TwoPhase": {"label": "Two phase", "definition": "The dielectric liquid boils on the hot parts and condenses again on a cooled coil inside the tank."},
        },
    },
    "CoolingTowerCircuit": {
        "label": "Cooling tower circuit",
        "definition": "Whether the fluid a cooling tower cools touches the air directly or stays inside a closed coil.",
        "values": {
            "Open": {"label": "Open", "definition": "The water being cooled runs over the fill and is in direct contact with the air."},
            "ClosedCircuit": {"label": "Closed circuit", "definition": "The fluid being cooled stays inside a coil that is wetted and cooled from outside, so it never touches the air or the spray water."},
        },
    },
    "HeatExchangerConstruction": {
        "label": "Heat exchanger construction",
        "definition": "How the heat transfer surface of a liquid-to-liquid heat exchanger is built.",
        "values": {
            "GasketedPlate": {"label": "Gasketed plate", "definition": "Corrugated plates sealed with gaskets and clamped in a frame, so the pack can be opened for cleaning or extended."},
            "BrazedPlate": {"label": "Brazed plate", "definition": "Plates brazed together into a sealed pack that cannot be opened."},
            "ShellAndTube": {"label": "Shell and tube", "definition": "A bundle of tubes inside a cylindrical shell, with one fluid in the tubes and the other around them."},
        },
    },
    "ValveFunction": {
        "label": "Valve function",
        "definition": "What a valve in a liquid loop is used for.",
        "values": {
            "Isolation": {"label": "Isolation", "definition": "Shuts off part of a loop so it can be serviced without draining the rest."},
            "Control": {"label": "Control", "definition": "Opens and closes under a control signal to hold a temperature, pressure or flow setpoint."},
            "PressureIndependentControl": {"label": "Pressure-independent control", "definition": "A control valve with a built-in regulator, so the flow it passes depends only on its opening and not on pressure changes elsewhere in the loop."},
            "Balancing": {"label": "Balancing", "definition": "Set during commissioning to share flow among parallel branches."},
            "Bypass": {"label": "Bypass", "definition": "Lets flow pass around a coil, filter or other device."},
            "PressureRelief": {"label": "Pressure relief", "definition": "Opens by itself to release liquid when the loop pressure exceeds its set limit."},
            "AirVent": {"label": "Air vent", "definition": "Lets trapped air out of a high point of a liquid loop by itself."},
        },
    },
}

# ---------------------------------------------------------------------------------------------
# Property classes

PROPERTIES = {
    "CoolingPlacementProperty": {
        "label": "Cooling placement property",
        "definition": "An enumerated property naming where a coolant distribution unit or coolant manifold sits relative to the racks it serves.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CoolingPlacement",
    },
    "CouplingTypeProperty": {
        "label": "Coupling type property",
        "definition": "An enumerated property naming the series and size of the quick-disconnect coupling at a liquid connection point.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CouplingType",
    },
    "CRAHFormProperty": {
        "label": "Computer room air handler form property",
        "definition": "An enumerated property naming the physical form of a computer room air handler.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CRAHForm",
    },
    "ImmersionPhaseProperty": {
        "label": "Immersion phase property",
        "definition": "An enumerated property naming whether an immersion tank works with a single-phase or a two-phase dielectric liquid.",
        "parent": S223.EnumerableProperty,
        "enumeration": "ImmersionPhase",
    },
    "CoolingTowerCircuitProperty": {
        "label": "Cooling tower circuit property",
        "definition": "An enumerated property naming whether a cooling tower is open or closed circuit.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CoolingTowerCircuit",
    },
    "HeatExchangerConstructionProperty": {
        "label": "Heat exchanger construction property",
        "definition": "An enumerated property naming how a liquid-to-liquid heat exchanger is built.",
        "parent": S223.EnumerableProperty,
        "enumeration": "HeatExchangerConstruction",
    },
    "ValveFunctionProperty": {
        "label": "Valve function property",
        "definition": "An enumerated property naming what a valve is used for.",
        "parent": S223.EnumerableProperty,
        "enumeration": "ValveFunction",
    },
    "FiltrationRating": {
        "label": "Filtration rating",
        "definition": "The particle size a filter or strainer is rated to stop, or the finest filtration a device needs on the loop that feeds it.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Length,
        "units": [UNIT.MicroM],
    },
    "AvailableExternalPressure": {
        "label": "Available external pressure",
        "definition": "The pressure difference a pump or coolant distribution unit can still deliver across the external loop at a stated flow, after its own internal losses.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Pressure,
        "units": [UNIT.KiloPA, UNIT.BAR, UNIT.PSI, UNIT.M_H2O, UNIT.FT_H2O],
    },
}
