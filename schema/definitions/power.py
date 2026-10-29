"""Power domain: from medium-voltage supply and on-site generation down to the rack busbar and power supply units.

Equipment classes join a Brick class (what it is) and a 223 class (so it can have connection points), as
docs/MODELING.md describes. Connection points, AC media, voltage property classes and the power connector
enumeration come from common.py; redundancy (N+1, "4 to make 3") uses core.py's RedundancyGroup (decisions P1 and G15).
A battery energy storage system assembled from several products is not a class here: it is a
brick:Battery_Energy_Storage_System, which Brick defines as a system (decision P5).

Rack PDUs and electricity meters take plain s223:Equipment as their 223 parent, with a closeMatch to the 223
class: product data cannot meet 223's one-inlet rule for electricity outlets or its contained-sensor rule for
meters. A rack PDU whose outlets need line-to-neutral voltage records a three-phase-with-neutral medium
(common.py AC-3PhN-*) on its inlet. Fuel inlets take the fuel media of common.py and 223 (diesel fuel,
natural gas, biogas, hydrogen); the class shapes only require a fluid, since one class burns several fuels.
"""

from .namespaces import AIF, BRICK, QK, S223, UNIT

AC = S223["Electricity-AC"]
DC = S223["Electricity-DC"]
ELECTRICITY = S223["Constituent-Electricity"]
FUEL = S223["Mix-Fluid"]

# ---------------------------------------------------------------------------------------------
# Connection points that common.py does not cover.

CONNECTION_POINTS = {
    "BidirectionalPowerPort": {
        "label": "Bidirectional power port",
        "definition": "A point through which electrical power flows either into or out of a device, such as a battery terminal or the grid terminal of a battery inverter.",
        "parents": [S223.BidirectionalConnectionPoint],
    },
    "FuelInlet": {
        "label": "Fuel inlet",
        "definition": "A point where a generator set or fuel cell takes in its fuel, such as diesel fuel, natural gas, biogas or hydrogen, through a fuel line or gas supply connection.",
        "parents": [S223.InletConnectionPoint],
    },
}

# ---------------------------------------------------------------------------------------------
# Equipment: one model number sold as one product (rule R6).

EQUIPMENT = {
    # -- Medium- and low-voltage distribution -----------------------------------------------------
    "MediumVoltageSwitchgear": {
        "label": "Medium-voltage switchgear",
        "definition": "A metal-enclosed lineup of breakers, disconnects and busbars, built to a standard such as IEC 62271-200 or IEEE C37.20.2, that receives alternating current above 1 kV from a utility or generator and switches it to transformers and other loads.",
        "parents": [BRICK.Switchgear, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "A medium-voltage switchgear has at least one alternating-current power inlet for an incoming feeder."},
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "A medium-voltage switchgear has at least one alternating-current power outlet for an outgoing feeder."},
        ],
    },
    "LowVoltageSwitchboard": {
        "label": "Low-voltage switchboard or switchgear",
        "definition": "A floor-standing assembly of circuit breakers and busbars at 1 kV or below, built to a switchboard or low-voltage switchgear standard such as UL 891, UL 1558 or IEC 61439-2, that distributes power from a transformer, generator or uninterruptible power supply to downstream equipment.",
        "parents": [BRICK.Switchgear, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A low-voltage switchboard has at least one power inlet for its incoming supply."},
            {"class": AIF.PowerOutlet, "min": 1,
             "message": "A low-voltage switchboard has at least one power outlet for an outgoing feeder."},
        ],
    },
    "Panelboard": {
        "label": "Panelboard",
        "definition": "A board of branch-circuit breakers on a common bus, built to a panelboard standard such as UL 67, that splits one feeder into branch circuits, either on its own or inside a power distribution unit or remote power panel.",
        "parents": [BRICK.Breaker_Panel, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A panelboard has at least one power inlet for its feeder."},
            {"class": AIF.PowerOutlet, "min": 1,
             "message": "A panelboard has at least one power outlet for a branch circuit."},
        ],
    },
    "RemotePowerPanel": {
        "label": "Remote power panel",
        "definition": "A floor-standing cabinet in the data hall that holds one or more panelboards without a transformer and breaks an upstream feeder out into branch circuits or power whips for nearby racks.",
        "parents": [BRICK.Breaker_Panel, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A remote power panel has at least one power inlet for its upstream feeder."},
            {"class": AIF.PowerOutlet, "min": 1,
             "message": "A remote power panel has at least one power outlet for a branch circuit."},
        ],
    },
    "FloorPDU": {
        "label": "Floor power distribution unit",
        "definition": "A floor-standing cabinet in the data hall that takes a bulk alternating-current feed, usually through an isolation transformer that changes its voltage, and distributes it through panelboards to branch circuits for a row of racks.",
        "parents": [BRICK.Breaker_Panel, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "A floor power distribution unit has at least one alternating-current power inlet for its bulk feed."},
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "A floor power distribution unit has at least one alternating-current power outlet for a branch circuit."},
        ],
    },
    "Busway": {
        "label": "Busway",
        "definition": "A prefabricated enclosed run of conductor bars, also called bus duct or busbar trunking, that carries power along a row or riser and lets tap-off units plug in at intervals to feed loads.",
        "parents": [BRICK.Electrical_Equipment, S223.Equipment],
        "narrow_match": [BRICK.Bus_Riser],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A busway has at least one power inlet where its feeder is terminated."},
            {"class": AIF.PowerOutlet, "min": 1,
             "message": "A busway has at least one power outlet where a tap-off unit plugs in."},
        ],
    },
    "BuswayTapOffUnit": {
        "label": "Busway tap-off unit",
        "definition": "A plug-in unit that clamps onto a busway, takes power from its bars through its own breaker or fuse, and delivers it to a rack or power distribution unit through receptacles or a cable.",
        "parents": [BRICK.Electrical_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A busway tap-off unit has at least one power inlet that plugs into the busway."},
            {"class": AIF.PowerOutlet, "min": 1,
             "message": "A busway tap-off unit has at least one power outlet to the load it feeds."},
        ],
    },
    "RackPDU": {
        "label": "Rack power distribution unit",
        "definition": "A strip of receptacles mounted in or on a rack that takes one feed and distributes it to the power cords of the equipment in that rack, often with metering or switching per outlet.",
        "parents": [BRICK.PlugStrip, S223.Equipment],
        "close_match": [S223.ElectricityOutlet],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "A rack power distribution unit has an alternating-current power inlet for its feed, with a neutral when its outlets take line-to-neutral voltage."},
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "A rack power distribution unit has at least one alternating-current receptacle."},
        ],
    },
    "TransferSwitch": {
        "label": "Transfer switch",
        "definition": "A switching device that connects a load to one of two or more power sources and moves the load from one source to another.",
        "parents": [BRICK.Transfer_Switch, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 2,
             "message": "A transfer switch has at least two alternating-current power inlets, one for each source."},
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "A transfer switch has at least one alternating-current power outlet to its load."},
        ],
        "subclasses": {
            "AutomaticTransferSwitch": {
                "label": "Automatic transfer switch",
                "definition": "A transfer switch with mechanical contacts that senses a failure of its preferred source and moves the load to the alternate source by itself.",
                "parents": [BRICK.Automatic_Transfer_Switch],
            },
            "StaticTransferSwitch": {
                "label": "Static transfer switch",
                "definition": "A transfer switch that moves a load between two live sources with semiconductor switches and no moving contacts, within a few milliseconds.",
                "parents": [BRICK.Static_Transfer_Switch],
            },
        },
    },
    # -- Medium-voltage motor supply for mechanical plant -------------------------------------------
    "MediumVoltageMotorControlCenter": {
        "label": "Medium-voltage motor control center",
        "definition": "A lineup of medium-voltage motor starters on a shared bus, each with its contactor, fuses and protection, built to a standard such as IEC 62271-106 or UL 347, that starts and protects large motors such as chiller compressors and pumps.",
        "parents": [BRICK.Motor_Control_Center, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "A medium-voltage motor control center has at least one alternating-current power inlet for its bus."},
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "A medium-voltage motor control center has at least one alternating-current power outlet to a motor."},
        ],
    },
    "MediumVoltageVariableFrequencyDrive": {
        "label": "Medium-voltage variable frequency drive",
        "definition": "A power converter, built to a standard such as IEC 61800-4, that turns fixed-frequency alternating current above 1 kV into variable-frequency output to control the speed of a large motor such as a chiller compressor.",
        "parents": [BRICK.Variable_Frequency_Drive, S223.VariableFrequencyDrive],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "A medium-voltage variable frequency drive has at least one alternating-current power inlet."},
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "A medium-voltage variable frequency drive has at least one alternating-current power outlet to its motor."},
        ],
    },
    # -- Voltage conversion -----------------------------------------------------------------------
    "Transformer": {
        "label": "Transformer",
        "definition": "A static device with magnetically coupled windings that changes alternating-current voltage between its primary and secondary sides at the same frequency.",
        "parents": [BRICK.Transformer, S223.ElectricEnergyTransformer],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "roles": [S223["Role-Primary"]], "min": 1,
             "message": "A transformer has an alternating-current power inlet on its primary side."},
            {"class": AIF.PowerOutlet, "medium": AC, "roles": [S223["Role-Secondary"]], "min": 1,
             "message": "A transformer has an alternating-current power outlet on its secondary side."},
        ],
    },
    "SolidStateTransformer": {
        "label": "Solid-state transformer",
        "definition": "A power-electronic converter that takes medium-voltage alternating current and delivers a direct-current bus, such as 800 V, through high-frequency isolation instead of a line-frequency transformer and rectifier, including facility-scale direct-current power blocks.",
        "parents": [BRICK.Transformer, S223.ElectricEnergyConverter],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "A solid-state transformer has a medium-voltage alternating-current power inlet."},
            {"class": AIF.PowerOutlet, "medium": DC, "min": 1,
             "message": "A solid-state transformer has at least one direct-current power outlet."},
        ],
    },
    "DCPowerRack": {
        "label": "DC power rack",
        "definition": "A standalone rack or row-level power center that converts low-voltage alternating current from the facility into a direct-current bus, typically 800 V, and feeds it to the compute racks of one or more rows.",
        "parents": [BRICK.Electrical_Equipment, S223.ElectricEnergyConverter],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "A DC power rack has at least one alternating-current power inlet from the facility."},
            {"class": AIF.PowerOutlet, "medium": DC, "min": 1,
             "message": "A DC power rack has at least one direct-current power outlet to the racks it feeds."},
        ],
    },
    "PowerShelf": {
        "label": "Power shelf",
        "definition": "A rack-mounted shelf of hot-swappable power supply units that converts the rack's alternating-current or high-voltage direct-current feed into the low-voltage direct current that the rack busbar carries to compute and switch trays.",
        "parents": [BRICK.Electrical_Equipment, S223.ElectricEnergyConverter],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A power shelf has at least one power inlet for the rack feed."},
            {"class": AIF.PowerOutlet, "medium": DC, "min": 1,
             "message": "A power shelf has a direct-current power outlet to the rack busbar."},
        ],
    },
    "RackBusbar": {
        "label": "Rack busbar",
        "definition": "A vertical conductor assembly at the rear of a rack that carries direct current from power shelves or a power rack to the compute and switch trays that clip onto it.",
        "parents": [BRICK.Electrical_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": DC, "min": 1,
             "message": "A rack busbar has at least one direct-current power inlet from a power shelf or power rack."},
            {"class": AIF.PowerOutlet, "medium": DC, "min": 1,
             "message": "A rack busbar has at least one direct-current power outlet where a tray clips on."},
        ],
    },
    # -- Generation -------------------------------------------------------------------------------
    "GeneratorSet": {
        "label": "Generator set",
        "definition": "A packaged unit in which a combustion engine drives an alternator to produce alternating-current power on site, for standby or continuous supply.",
        "parents": [BRICK.Electrical_Equipment, S223.Generator],
        "connection_points": [
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "A generator set has at least one alternating-current power outlet."},
            {"class": AIF.FuelInlet, "medium": FUEL, "min": 1,
             "message": "A generator set has at least one fuel inlet for diesel fuel, natural gas or another fuel."},
        ],
    },
    "FuelCellPowerModule": {
        "label": "Fuel cell power module",
        "definition": "A packaged power unit that converts a fuel such as natural gas or hydrogen into electricity by an electrochemical reaction without combustion, with its own power conditioning.",
        "parents": [BRICK.Electrical_Equipment, S223.Generator],
        "connection_points": [
            {"class": AIF.PowerOutlet, "min": 1,
             "message": "A fuel cell power module has at least one power outlet."},
            {"class": AIF.FuelInlet, "medium": FUEL, "min": 1,
             "message": "A fuel cell power module has at least one fuel inlet for natural gas, biogas, hydrogen or another fuel."},
        ],
    },
    # -- Stored energy ----------------------------------------------------------------------------
    "UPS": {
        "label": "Uninterruptible power supply",
        "definition": "A power conditioning unit that feeds its load from the incoming alternating-current supply in normal operation and from a battery or other energy store without interruption when that supply fails.",
        "parents": [BRICK.Electrical_Equipment, S223.ElectricEnergyConverter],
        "connection_points": [
            {"class": AIF.PowerInlet, "medium": AC, "min": 1,
             "message": "An uninterruptible power supply has at least one alternating-current power inlet."},
            {"class": AIF.PowerOutlet, "medium": AC, "min": 1,
             "message": "An uninterruptible power supply has at least one alternating-current power outlet to its load."},
            {"class": AIF.BidirectionalPowerPort, "medium": DC, "min": 1,
             "message": "An uninterruptible power supply has a direct-current port to its battery."},
        ],
    },
    "BatteryCabinet": {
        "label": "Battery cabinet",
        "definition": "A cabinet or open rack of rechargeable battery modules with its own disconnect and monitoring, sold as one unit to store direct-current energy for an uninterruptible power supply, an inverter or a direct-current bus.",
        "parents": [BRICK.Battery, S223.Battery],
        "connection_points": [
            {"class": AIF.BidirectionalPowerPort, "medium": DC, "min": 1,
             "message": "A battery cabinet has at least one direct-current port through which it is charged and discharged."},
        ],
    },
    "BatteryEnergyStorageSystem": {
        "label": "Battery energy storage system",
        "definition": "A battery storage plant sold as one model, such as a containerized unit, that holds battery modules, thermal management and controls and exchanges energy with the grid or a facility bus through alternating-current or direct-current terminals.",
        "parents": [BRICK.Energy_Storage, S223.Battery],
        "close_match": [BRICK.Battery_Energy_Storage_System],
        "connection_points": [
            {"class": AIF.BidirectionalPowerPort, "medium": ELECTRICITY, "min": 1,
             "message": "A battery energy storage system has at least one power port through which it is charged and discharged."},
        ],
    },
    "BatteryInverter": {
        "label": "Battery inverter",
        "definition": "A bidirectional power conversion system that charges a battery from an alternating-current bus and discharges it back, converting between the direct current of the battery and alternating current.",
        "parents": [BRICK.Inverter, S223.ElectricEnergyInverter],
        "connection_points": [
            {"class": AIF.BidirectionalPowerPort, "medium": DC, "min": 1,
             "message": "A battery inverter has at least one direct-current port on its battery side."},
            {"class": AIF.BidirectionalPowerPort, "medium": AC, "min": 1,
             "message": "A battery inverter has at least one alternating-current port on its grid side."},
        ],
    },
}

# ---------------------------------------------------------------------------------------------
# Components: installed inside equipment and linked to it with brick:hasPart (rule R6).

COMPONENTS = {
    "PowerSupplyUnit": {
        "label": "Power supply unit",
        "definition": "A replaceable converter module that turns alternating or direct current from its inlet into the direct-current voltage used by a server, a switch or a rack busbar.",
        "parents": [BRICK.Electrical_Equipment, S223.ElectricEnergyConverter],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A power supply unit has at least one power inlet."},
            {"class": AIF.PowerOutlet, "medium": DC, "min": 1,
             "message": "A power supply unit has at least one direct-current power outlet."},
        ],
    },
    "BatteryBackupUnit": {
        "label": "Battery backup unit",
        "definition": "A battery module fitted in a power shelf or rack that carries the rack load for seconds to minutes and smooths fast load swings before they reach the facility supply.",
        "parents": [BRICK.Battery, S223.Battery],
    },
    "BatteryModule": {
        "label": "Battery module",
        "definition": "A group of battery cells joined in series and parallel with their own monitoring, forming the replaceable building block of a battery cabinet or energy storage system.",
        "parents": [BRICK.Battery, S223.Battery],
    },
    "BatteryCell": {
        "label": "Battery cell",
        "definition": "The smallest sealed electrochemical unit of a battery, combined with other cells into a module.",
        "parents": [BRICK.Battery, S223.Battery],
    },
    "Engine": {
        "label": "Engine",
        "definition": "The reciprocating combustion engine of a generator set, which burns diesel or gas fuel to turn the alternator shaft.",
        "parents": [BRICK.Motor, S223.Equipment],
    },
    "Alternator": {
        "label": "Alternator",
        "definition": "The rotating electrical machine of a generator set that turns the shaft power of the engine into alternating-current output.",
        "parents": [BRICK.Electrical_Equipment, S223.Generator],
    },
    "CircuitBreaker": {
        "label": "Circuit breaker",
        "definition": "A switching device that carries current in normal service, opens the circuit by itself on overcurrent or a fault, and can be closed again after it trips.",
        "parents": [BRICK.Circuit_Breaker, S223.ElectricityBreaker],
    },
    "Fuse": {
        "label": "Fuse",
        "definition": "A protective device whose element melts and opens the circuit when current exceeds its rating, and which is replaced after it operates.",
        "parents": [BRICK.Electrical_Equipment, S223.Equipment],
    },
    "DisconnectSwitch": {
        "label": "Disconnect switch",
        "definition": "A manually operated switch that opens a circuit to isolate equipment for maintenance with a visible or lockable break, without being designed to interrupt fault current.",
        "parents": [BRICK.Disconnect_Switch, S223.Equipment],
    },
    "ProtectiveRelay": {
        "label": "Protective relay",
        "definition": "A device that watches the current, voltage or other electrical quantities of a circuit and commands a breaker or contactor to open when it detects a fault or overload.",
        "parents": [BRICK.Relay, S223.Equipment],
    },
    "ElectricityMeter": {
        "label": "Electricity meter",
        "definition": "A device installed in switchgear, panels or power distribution units that measures voltage, current, power and energy at a point in the power chain and reports them.",
        "parents": [BRICK.Electrical_Meter, S223.Equipment],
        "close_match": [S223.ElectricityMeter],
    },
}

# ---------------------------------------------------------------------------------------------
# Enumerations (rule R4).

ENUMERATIONS = {
    "BatteryChemistry": {
        "label": "Battery chemistry",
        "definition": "The electrochemical cell technologies of rechargeable batteries.",
        "values": {
            "VRLA": {"label": "Valve-regulated lead-acid", "definition": "Sealed lead-acid cells with absorbed glass mat or gel electrolyte and a pressure relief valve."},
            "FloodedLeadAcid": {"label": "Flooded lead-acid", "definition": "Vented lead-acid cells with free liquid electrolyte that has to be topped up."},
            "LithiumIon": {"label": "Lithium-ion", "definition": "Lithium-ion cells whose cathode material is not stated."},
            "LFP": {"label": "Lithium iron phosphate", "definition": "Lithium-ion cells with a lithium iron phosphate cathode."},
            "NMC": {"label": "Lithium nickel manganese cobalt oxide", "definition": "Lithium-ion cells with a nickel manganese cobalt oxide cathode."},
            "NiCd": {"label": "Nickel-cadmium", "definition": "Alkaline cells with nickel oxide hydroxide and cadmium electrodes."},
            "NiZn": {"label": "Nickel-zinc", "definition": "Alkaline cells with nickel oxide hydroxide and zinc electrodes."},
        },
    },
    "GeneratorSetDutyRating": {
        "label": "Generator set duty rating",
        "definition": "The duty classes of ISO 8528-1 and vendor practice under which a generator set states a rated power, used as an aspect of that rated-power value.",
        "values": {
            "Standby": {"label": "Emergency standby", "definition": "Power available for the length of a utility outage at variable load, with limited yearly running hours and no overload allowance."},
            "Prime": {"label": "Prime", "definition": "Power available for unlimited hours at variable load, with a limit on the average load over a run period."},
            "LimitedTime": {"label": "Limited-time running", "definition": "Power available at constant load for a limited number of hours per year."},
            "Continuous": {"label": "Continuous", "definition": "Power available for unlimited hours at constant load."},
            "DataCenterPower": {"label": "Data center power", "definition": "Power available for unlimited hours at constant or varying load in a data center application, the data center power class of ISO 8528-1."},
            "DataCenterContinuous": {"label": "Data center continuous", "definition": "Power a vendor states under the name data center continuous for running a generator set in a data center, kept apart from data center power until a document shows the two are the same rating."},
        },
    },
    "SwitchgearConstruction": {
        "label": "Switchgear construction",
        "definition": "The ways a medium-voltage switchgear assembly encloses and separates its switching devices, busbars and cable compartments.",
        "values": {
            "MetalClad": {"label": "Metal-clad", "definition": "Withdrawable breakers in grounded metal compartments that separate each breaker, bus and cable section from the others."},
            "MetalEnclosed": {"label": "Metal-enclosed", "definition": "Switching devices in a common grounded metal enclosure without full separation between compartments, often with load-interrupter switches."},
            "RingMainUnit": {"label": "Ring main unit", "definition": "A compact sealed unit of load-break switches and a protected feeder that connects a transformer to a looped medium-voltage cable ring."},
        },
    },
    "SwitchgearInsulation": {
        "label": "Switchgear insulation",
        "definition": "The insulating medium between the live parts of medium-voltage switchgear.",
        "values": {
            "AirInsulated": {"label": "Air-insulated", "definition": "Live parts insulated by air at atmospheric pressure."},
            "GasInsulated": {"label": "Gas-insulated", "definition": "Live parts sealed in a tank filled with an insulating gas such as sulfur hexafluoride or a replacement gas mixture."},
            "SolidInsulated": {"label": "Solid-insulated", "definition": "Live parts encapsulated in solid insulation such as epoxy resin."},
        },
    },
    "TransformerConstruction": {
        "label": "Transformer construction",
        "definition": "The ways a power transformer insulates and cools its windings.",
        "values": {
            "VPI": {"label": "Vacuum pressure impregnated dry-type", "definition": "Dry-type windings impregnated with varnish under vacuum and pressure and cooled by air."},
            "VPE": {"label": "Vacuum pressure encapsulated dry-type", "definition": "Dry-type windings encapsulated in silicone resin under vacuum and pressure and cooled by air."},
            "CastResin": {"label": "Cast resin dry-type", "definition": "Dry-type windings cast in solid epoxy resin and cooled by air."},
            "LiquidFilled": {"label": "Liquid-filled", "definition": "Windings immersed in a tank of mineral oil or ester fluid that insulates and cools them."},
        },
    },
    "TransferTransition": {
        "label": "Transfer transition",
        "definition": "How a transfer switch, or the bypass of an uninterruptible power supply, moves its load from one source to the other.",
        "values": {
            "Open": {"label": "Open transition", "definition": "The switch breaks the connection to one source before it makes the connection to the other."},
            "Delayed": {"label": "Delayed transition", "definition": "An open transition that keeps the load disconnected for a set time so that residual motor and transformer voltages decay before reconnection."},
            "Closed": {"label": "Closed transition", "definition": "The switch briefly connects both sources in parallel so that the load sees no interruption."},
        },
    },
    "CircuitBreakerType": {
        "label": "Circuit breaker type",
        "definition": "The construction and interrupting technology of circuit breakers.",
        "values": {
            "Air": {"label": "Air circuit breaker", "definition": "A large low-voltage power breaker, often withdrawable, that interrupts the arc in air."},
            "MoldedCase": {"label": "Molded-case circuit breaker", "definition": "A low-voltage breaker with its mechanism and trip unit in a molded insulating housing."},
            "InsulatedCase": {"label": "Insulated-case circuit breaker", "definition": "A low-voltage power breaker in an insulating housing with features of air circuit breakers, such as stored-energy closing."},
            "Miniature": {"label": "Miniature circuit breaker", "definition": "A small modular low-voltage breaker for branch circuits, usually mounted on a rail."},
            "Vacuum": {"label": "Vacuum circuit breaker", "definition": "A breaker, usually for medium voltage, whose contacts open inside sealed vacuum interrupters."},
            "SolidState": {"label": "Solid-state circuit breaker", "definition": "A breaker that interrupts current with semiconductor switches instead of mechanical contacts, used mainly on direct-current buses."},
        },
    },
    "BreakerContinuousRating": {
        "label": "Breaker continuous rating",
        "definition": "Whether a circuit breaker in its enclosure may carry its full rated current continuously or only a reduced share of it.",
        "values": {
            "80Percent": {"label": "80 percent rated", "definition": "A standard breaker whose continuous load may be at most 80 percent of its rated current."},
            "100Percent": {"label": "100 percent rated", "definition": "A breaker listed to carry its full rated current continuously in its stated enclosure."},
        },
    },
    "FuelCellType": {
        "label": "Fuel cell type",
        "definition": "The electrolyte technologies of fuel cell power modules.",
        "values": {
            "SOFC": {"label": "Solid oxide fuel cell", "definition": "A high-temperature fuel cell with a ceramic electrolyte that can run on natural gas."},
            "PEMFC": {"label": "Proton exchange membrane fuel cell", "definition": "A low-temperature fuel cell with a polymer membrane electrolyte that runs on hydrogen."},
            "MCFC": {"label": "Molten carbonate fuel cell", "definition": "A high-temperature fuel cell with a molten carbonate salt electrolyte."},
            "PAFC": {"label": "Phosphoric acid fuel cell", "definition": "A medium-temperature fuel cell with a liquid phosphoric acid electrolyte."},
        },
    },
    "PowerSupplyEfficiencyGrade": {
        "label": "Power supply efficiency grade",
        "definition": "The levels of the 80 PLUS program, which certifies the efficiency of power supplies at set fractions of their rated load.",
        "values": {
            "80PLUS": {"label": "80 PLUS", "definition": "The base level of the 80 PLUS program."},
            "80PLUS-Bronze": {"label": "80 PLUS Bronze", "definition": "The 80 PLUS Bronze level, above the base level and below Silver."},
            "80PLUS-Silver": {"label": "80 PLUS Silver", "definition": "The 80 PLUS Silver level, above Bronze and below Gold."},
            "80PLUS-Gold": {"label": "80 PLUS Gold", "definition": "The 80 PLUS Gold level, above Silver and below Platinum."},
            "80PLUS-Platinum": {"label": "80 PLUS Platinum", "definition": "The 80 PLUS Platinum level, above Gold and below Titanium."},
            "80PLUS-Titanium": {"label": "80 PLUS Titanium", "definition": "The 80 PLUS Titanium level, the highest of the program, which also tests efficiency at a tenth of rated load."},
        },
    },
    "EarthingSystem": {
        "label": "Earthing system",
        "definition": "The earthing arrangements of IEC 60364 for low-voltage AC supplies, which say how the source and the exposed metal parts are connected to earth.",
        "values": {
            "TN-S": {"label": "TN-S", "definition": "The source is earthed and separate neutral and protective conductors run throughout."},
            "TN-C": {"label": "TN-C", "definition": "The source is earthed and one combined neutral and protective conductor runs throughout."},
            "TN-C-S": {"label": "TN-C-S", "definition": "The source is earthed and a combined neutral and protective conductor is split into separate ones part way along."},
            "TT": {"label": "TT", "definition": "The source is earthed and the exposed metal parts are earthed through a separate electrode of the installation."},
            "IT": {"label": "IT", "definition": "The source is isolated from earth or earthed through a high impedance, and the exposed metal parts are earthed."},
        },
    },
}

# ---------------------------------------------------------------------------------------------
# Property classes: only where the quantity kind alone does not say what a value means, or to fix an
# enumeration kind. Ratings such as rated power, current and energy use the quantity kind with 223 aspects.

PROPERTIES = {
    "InterruptingRating": {
        "label": "Interrupting rating",
        "definition": "The largest fault current a circuit breaker or fuse can interrupt safely at a stated voltage.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.ElectricCurrent,
        "units": [UNIT.A, UNIT.KiloA],
    },
    "ShortCircuitCurrentRating": {
        "label": "Short-circuit current rating",
        "definition": "The largest prospective fault current that an assembly, busway or transfer switch withstands, either for a stated time or when protected by a stated upstream device.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.ElectricCurrent,
        "units": [UNIT.A, UNIT.KiloA],
    },
    "BasicImpulseLevel": {
        "label": "Basic impulse level",
        "definition": "The peak voltage of a standard lightning impulse that the insulation of medium-voltage equipment withstands.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Voltage,
        "units": [UNIT.KiloV],
    },
    "TransferTime": {
        "label": "Transfer time",
        "definition": "The time a transfer switch or an uninterruptible power supply takes to move its load from one source to another.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Time,
        "units": [UNIT.MicroSEC, UNIT.MilliSEC, UNIT.SEC],
    },
    "HoldUpTime": {
        "label": "Hold-up time",
        "definition": "The time a power supply unit keeps its direct-current output within limits after its input power is lost.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Time,
        "units": [UNIT.MilliSEC],
    },
    "BackupRuntime": {
        "label": "Backup runtime",
        "definition": "The time a battery, a battery backup unit or an uninterruptible power supply can carry a stated load from stored energy alone.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Time,
        "units": [UNIT.SEC, UNIT.MIN, UNIT.HR],
    },
    "OverloadCapacity": {
        "label": "Overload capacity",
        "definition": "The load a device can carry above its rating for a stated duration, given as a percentage of its rated output.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.DimensionlessRatio,
        "units": [UNIT.PERCENT],
    },
    "BatteryChemistryProperty": {
        "label": "Battery chemistry property",
        "definition": "An enumerated property naming the cell chemistry of a battery cabinet, battery module, battery cell or battery backup unit.",
        "parent": S223.EnumerableProperty,
        "enumeration": "BatteryChemistry",
    },
    "SwitchgearConstructionProperty": {
        "label": "Switchgear construction property",
        "definition": "An enumerated property naming the construction of a medium-voltage switchgear.",
        "parent": S223.EnumerableProperty,
        "enumeration": "SwitchgearConstruction",
    },
    "SwitchgearInsulationProperty": {
        "label": "Switchgear insulation property",
        "definition": "An enumerated property naming the insulating medium of a medium-voltage switchgear.",
        "parent": S223.EnumerableProperty,
        "enumeration": "SwitchgearInsulation",
    },
    "TransformerConstructionProperty": {
        "label": "Transformer construction property",
        "definition": "An enumerated property naming how a transformer insulates and cools its windings.",
        "parent": S223.EnumerableProperty,
        "enumeration": "TransformerConstruction",
    },
    "TransferTransitionProperty": {
        "label": "Transfer transition property",
        "definition": "An enumerated property naming a transition a transfer switch or the bypass of an uninterruptible power supply supports.",
        "parent": S223.EnumerableProperty,
        "enumeration": "TransferTransition",
    },
    "CircuitBreakerTypeProperty": {
        "label": "Circuit breaker type property",
        "definition": "An enumerated property naming the construction and interrupting technology of a circuit breaker.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CircuitBreakerType",
    },
    "BreakerContinuousRatingProperty": {
        "label": "Breaker continuous rating property",
        "definition": "An enumerated property naming whether a circuit breaker is rated for continuous load at 80 or 100 percent of its rated current.",
        "parent": S223.EnumerableProperty,
        "enumeration": "BreakerContinuousRating",
    },
    "FuelCellTypeProperty": {
        "label": "Fuel cell type property",
        "definition": "An enumerated property naming the electrolyte technology of a fuel cell power module.",
        "parent": S223.EnumerableProperty,
        "enumeration": "FuelCellType",
    },
    "PowerSupplyEfficiencyGradeProperty": {
        "label": "Power supply efficiency grade property",
        "definition": "An enumerated property naming the 80 PLUS level a power supply is certified to.",
        "parent": S223.EnumerableProperty,
        "enumeration": "PowerSupplyEfficiencyGrade",
    },
    "EarthingSystemProperty": {
        "label": "Earthing system property",
        "definition": "An enumerated property naming the earthing arrangement of the AC supply that a power connection point delivers or requires.",
        "parent": S223.EnumerableProperty,
        "enumeration": "EarthingSystem",
    },
}
