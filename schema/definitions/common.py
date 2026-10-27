"""Connection points, media, property classes and enumerations shared by the compute, network, cooling and power domains.

Values themselves are 223 properties (s223:QuantifiableProperty with a quantity kind and unit, or
s223:EnumerableProperty with an enumeration kind). A property class is defined here only when the quantity
kind alone does not say what the value means (line-to-line vs line-to-neutral voltage, cooling capacity,
approach temperature difference) or when an enumerated value needs a fixed enumeration kind.
"""

from .namespaces import AIF, QK, S223, UNIT

# ---------------------------------------------------------------------------------------------
# Connection points (docs/CONVENTIONS.md section 6). Medium and role come from 223.

CONNECTION_POINTS = {
    "PowerInlet": {
        "label": "Power inlet",
        "definition": "A point where a device takes in electrical power, such as an appliance inlet, a terminal block or a busbar connection.",
        "parents": [S223.InletConnectionPoint],
    },
    "PowerOutlet": {
        "label": "Power outlet",
        "definition": "A point where a device delivers electrical power to another device, such as a receptacle, an output terminal or a busway tap.",
        "parents": [S223.OutletConnectionPoint],
    },
    "LiquidInlet": {
        "label": "Liquid inlet",
        "definition": "A point where a liquid such as coolant or facility water enters a device.",
        "parents": [S223.InletConnectionPoint],
    },
    "LiquidOutlet": {
        "label": "Liquid outlet",
        "definition": "A point where a liquid such as coolant or facility water leaves a device.",
        "parents": [S223.OutletConnectionPoint],
    },
    "AirInlet": {
        "label": "Air inlet",
        "definition": "A point where air enters a device, such as the intake face of a server or the return of an air handler.",
        "parents": [S223.InletConnectionPoint],
    },
    "AirOutlet": {
        "label": "Air outlet",
        "definition": "A point where air leaves a device, such as the exhaust face of a server or the supply of an air handler.",
        "parents": [S223.OutletConnectionPoint],
    },
    "DataPort": {
        "label": "Data port",
        "definition": "A point where a device sends and receives data over a wired or optical link.",
        "parents": [S223.BidirectionalConnectionPoint],
    },
    "PluggableCage": {
        "label": "Pluggable cage",
        "definition": "A data port built as a receptacle that accepts a pluggable transceiver or a cable plug of a given form factor.",
        "parents": [AIF.DataPort],
    },
    "PluggablePlug": {
        "label": "Pluggable plug",
        "definition": "The end of a transceiver or cable assembly that inserts into a pluggable cage.",
        "parents": [AIF.DataPort],
    },
    "FiberPort": {
        "label": "Fiber port",
        "definition": "An optical connector on a transceiver, patch panel or fiber cable that joins optical fibers.",
        "parents": [AIF.DataPort],
    },
    "ManagementPort": {
        "label": "Management port",
        "definition": "A data port reserved for out-of-band management of a device, typically a copper Ethernet port to its management controller.",
        "parents": [AIF.DataPort],
    },
}

# ---------------------------------------------------------------------------------------------
# Media missing from 223 (each a class and an instance of itself, as 223 defines media).

MEDIA = {
    "Signal-InfiniBand": {
        "label": "InfiniBand electrical signal",
        "definition": "Electrical signalling that carries the InfiniBand protocol between a host interface and a pluggable module or copper cable.",
        "parent": S223["Electricity-Signal"],
    },
    "Signal-FiberInfiniBand": {
        "label": "InfiniBand optical signal",
        "definition": "Light in an optical fiber that carries the InfiniBand protocol between two optical transceivers.",
        "parent": S223["Infrared-Signal"],
    },
    "Signal-NVLink": {
        "label": "NVLink signal",
        "definition": "Electrical signalling of NVIDIA NVLink, the scale-up link that joins GPUs to each other and to NVLink switches.",
        "parent": S223["Electricity-Signal"],
    },
    "Signal-PCIe": {
        "label": "PCI Express signal",
        "definition": "Electrical signalling of PCI Express, the expansion bus between a host and add-in cards such as network adapters.",
        "parent": S223["Electricity-Signal"],
    },
    "AC-1Ph-50Hz": {
        "label": "Single-phase AC at 50 Hz",
        "definition": "Single-phase alternating current at 50 Hz, with the voltage given separately as a property of the connection point.",
        "parent": S223["Electricity-AC"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-50Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-SinglePhase"]),
        ],
    },
    "AC-1Ph-60Hz": {
        "label": "Single-phase AC at 60 Hz",
        "definition": "Single-phase alternating current at 60 Hz, with the voltage given separately as a property of the connection point.",
        "parent": S223["Electricity-AC"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-60Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-SinglePhase"]),
        ],
    },
    "AC-1Ph-50Hz-60Hz": {
        "label": "Single-phase AC at 50 or 60 Hz",
        "definition": "Single-phase alternating current that a connection point accepts or delivers at either 50 Hz or 60 Hz.",
        "parent": S223["Electricity-AC"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-50Hz"]),
            (S223.hasFrequency, S223["Frequency-60Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-SinglePhase"]),
        ],
    },
    "AC-3Ph-50Hz": {
        "label": "Three-phase AC at 50 Hz",
        "definition": "Three-phase alternating current at 50 Hz, with the voltage given separately as a property of the connection point.",
        "parent": S223["Electricity-AC"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-50Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-ThreePhase"]),
        ],
    },
    "AC-3Ph-60Hz": {
        "label": "Three-phase AC at 60 Hz",
        "definition": "Three-phase alternating current at 60 Hz, with the voltage given separately as a property of the connection point.",
        "parent": S223["Electricity-AC"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-60Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-ThreePhase"]),
        ],
    },
    "AC-3Ph-50Hz-60Hz": {
        "label": "Three-phase AC at 50 or 60 Hz",
        "definition": "Three-phase alternating current that a connection point accepts or delivers at either 50 Hz or 60 Hz.",
        "parent": S223["Electricity-AC"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-50Hz"]),
            (S223.hasFrequency, S223["Frequency-60Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-ThreePhase"]),
        ],
    },
    "PropyleneGlycolSolution-25Percent": {
        "label": "25 percent propylene glycol solution",
        "definition": "A water solution with 25 percent propylene glycol by volume, the usual coolant of direct-to-chip liquid cooling loops.",
        "parent": S223["Water-GlycolSolution"],
        "composed_of": [
            {"label": "Propylene glycol concentration", "value": "25.0", "of_constituent": AIF["Constituent-PropyleneGlycol"],
             "quantity_kind": QK.VolumeFraction, "unit": UNIT.PERCENT},
            {"label": "Water concentration", "value": "75.0", "of_constituent": S223["Constituent-H2O"],
             "quantity_kind": QK.VolumeFraction, "unit": UNIT.PERCENT},
        ],
    },
    "Constituent-PropyleneGlycol": {
        "label": "Propylene glycol",
        "definition": "Propylene glycol as a constituent of a coolant mixture.",
        "parent": S223["Constituent-Glycol"],
    },
    "Constituent-EthyleneGlycol": {
        "label": "Ethylene glycol",
        "definition": "Ethylene glycol as a constituent of a coolant mixture.",
        "parent": S223["Constituent-Glycol"],
    },
    "Fluid-DielectricLiquid": {
        "label": "Dielectric liquid",
        "definition": "An electrically insulating liquid in which electronics are immersed so that it removes their heat by direct contact.",
        "parent": S223["Mix-Fluid"],
    },
    "Fluid-DieselFuel": {
        "label": "Diesel fuel",
        "definition": "Diesel fuel oil as burned by the engine of a generator set.",
        "parent": S223["Fluid-Oil"],
    },
    "Fluid-Hydrogen": {
        "label": "Hydrogen",
        "definition": "Hydrogen gas as the fuel of a fuel cell or a hydrogen-capable engine.",
        "parent": S223["Mix-Fluid"],
    },
    "Fluid-Biogas": {
        "label": "Biogas",
        "definition": "Gas produced from organic matter, used as an alternative fuel for engines and fuel cells.",
        "parent": S223["Mix-Fluid"],
    },
    "AC-3PhN-50Hz": {
        "label": "Three-phase AC with neutral at 50 Hz",
        "definition": "Three-phase alternating current at 50 Hz in which a neutral conductor is also connected, so both line-to-line and line-to-neutral voltages are available.",
        "parent": AIF["AC-3Ph-50Hz"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-50Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-ThreePhase"]),
        ],
    },
    "AC-3PhN-60Hz": {
        "label": "Three-phase AC with neutral at 60 Hz",
        "definition": "Three-phase alternating current at 60 Hz in which a neutral conductor is also connected, so both line-to-line and line-to-neutral voltages are available.",
        "parent": AIF["AC-3Ph-60Hz"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-60Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-ThreePhase"]),
        ],
    },
    "AC-3PhN-50Hz-60Hz": {
        "label": "Three-phase AC with neutral at 50 or 60 Hz",
        "definition": "Three-phase alternating current at either 50 Hz or 60 Hz in which a neutral conductor is also connected.",
        "parent": AIF["AC-3Ph-50Hz-60Hz"],
        "triples": [
            (S223.hasFrequency, S223["Frequency-50Hz"]),
            (S223.hasFrequency, S223["Frequency-60Hz"]),
            (S223.hasNumberOfElectricalPhases, S223["NumberOfElectricalPhases-ThreePhase"]),
        ],
    },
}

# ---------------------------------------------------------------------------------------------
# Enumerations shared across domains.

ENUMERATIONS = {
    "NetworkProtocol": {
        "label": "Network protocol",
        "definition": "The link protocols a data port or cable can carry.",
        "values": {
            "InfiniBand": {"label": "InfiniBand", "definition": "The InfiniBand link protocol used for high-performance compute fabrics."},
            "Ethernet": {"label": "Ethernet", "definition": "The Ethernet link protocol defined by IEEE 802.3."},
            "NVLink": {"label": "NVLink", "definition": "The NVIDIA NVLink protocol for scale-up links between GPUs and NVLink switches."},
        },
    },
    "InfiniBandGeneration": {
        "label": "InfiniBand generation",
        "definition": "The InfiniBand signalling generations, each with its own per-lane rate.",
        "values": {
            "FDR": {"label": "FDR", "definition": "InfiniBand Fourteen Data Rate, 56 Gb/s on a four-lane port."},
            "EDR": {"label": "EDR", "definition": "InfiniBand Enhanced Data Rate, 100 Gb/s on a four-lane port."},
            "HDR": {"label": "HDR", "definition": "InfiniBand High Data Rate, 200 Gb/s on a four-lane port."},
            "HDR100": {"label": "HDR100", "definition": "InfiniBand HDR signalling on a two-lane port, 100 Gb/s."},
            "NDR": {"label": "NDR", "definition": "InfiniBand Next Data Rate, 400 Gb/s on a four-lane port."},
            "NDR200": {"label": "NDR200", "definition": "InfiniBand NDR signalling on a two-lane port, 200 Gb/s."},
            "XDR": {"label": "XDR", "definition": "InfiniBand eXtended Data Rate, 800 Gb/s on a four-lane port."},
        },
    },
    "PluggableFormFactor": {
        "label": "Pluggable form factor",
        "definition": "The mechanical and electrical formats of pluggable cages, transceivers and cable plugs.",
        "values": {
            "SFP": {"label": "SFP", "definition": "Small form-factor pluggable with one electrical lane up to about 1 Gb/s."},
            "SFP+": {"label": "SFP+", "definition": "Small form-factor pluggable with one electrical lane up to 10 Gb/s."},
            "QSFP+": {"label": "QSFP+", "definition": "Quad small form-factor pluggable with four lanes up to 10 Gb/s each."},
            "SFP28": {"label": "SFP28", "definition": "Small form-factor pluggable with one electrical lane up to 25 Gb/s."},
            "SFP56": {"label": "SFP56", "definition": "Small form-factor pluggable with one electrical lane up to 50 Gb/s."},
            "QSFP28": {"label": "QSFP28", "definition": "Quad small form-factor pluggable with four lanes up to 25 Gb/s each."},
            "QSFP56": {"label": "QSFP56", "definition": "Quad small form-factor pluggable with four lanes up to 50 Gb/s each."},
            "QSFP112": {"label": "QSFP112", "definition": "Quad small form-factor pluggable with four lanes up to 100 Gb/s each."},
            "QSFP-DD": {"label": "QSFP-DD", "definition": "Double-density quad small form-factor pluggable with eight electrical lanes."},
            "OSFP": {"label": "OSFP", "definition": "Octal small form-factor pluggable with eight lanes and an integrated finned heat sink on the module."},
            "OSFP-RHS": {"label": "OSFP-RHS", "definition": "Flat-top octal small form-factor pluggable whose heat is removed by a heat sink riding on the cage."},
        },
    },
    "FiberConnector": {
        "label": "Fiber connector",
        "definition": "The optical connector types on transceivers and fiber cables.",
        "values": {
            "LC-Duplex": {"label": "Duplex LC", "definition": "A pair of LC optical connectors carrying one transmit and one receive fiber."},
            "MPO-12": {"label": "MPO-12", "definition": "A multi-fiber push-on connector with up to twelve fibers in one row."},
            "MPO-16": {"label": "MPO-16", "definition": "A multi-fiber push-on connector with sixteen fibers in one row."},
        },
    },
    "PowerConnector": {
        "label": "Power connector",
        "definition": "The connector and terminal types at power inlets and outlets.",
        "values": {
            "IEC60320-C13": {"label": "IEC 60320 C13", "definition": "The IEC 60320 C13 cord connector, rated around 10 A, mating with a C14 inlet."},
            "IEC60320-C14": {"label": "IEC 60320 C14", "definition": "The IEC 60320 C14 appliance inlet or outlet that mates with a C13 connector."},
            "IEC60320-C19": {"label": "IEC 60320 C19", "definition": "The IEC 60320 C19 cord connector, rated around 16 A, mating with a C20 inlet."},
            "IEC60320-C20": {"label": "IEC 60320 C20", "definition": "The IEC 60320 C20 appliance inlet or outlet that mates with a C19 connector."},
            "IEC60320-C15": {"label": "IEC 60320 C15", "definition": "The high-temperature variant of the C13 cord connector, mating with a C16 inlet."},
            "IEC60320-C21": {"label": "IEC 60320 C21", "definition": "The high-temperature variant of the C19 cord connector, mating with a C22 inlet."},
            "NEMA-L6-30": {"label": "NEMA L6-30", "definition": "The NEMA locking plug and receptacle for 250 V, 30 A, two poles and ground."},
            "NEMA-L21-30": {"label": "NEMA L21-30", "definition": "The NEMA locking plug and receptacle for three-phase 120/208 V, 30 A, with neutral and ground."},
            "IEC60309": {"label": "IEC 60309", "definition": "An industrial plug and socket of the IEC 60309 family, with its pin layout and rating given separately."},
            "Hardwired": {"label": "Hardwired terminals", "definition": "Cable terminals or lugs inside the equipment instead of a plug and socket."},
            "RackBusbarClip": {"label": "Rack busbar clip", "definition": "A blind-mate clip that connects a tray or power shelf to a vertical rack busbar."},
            "BuswayTapOff": {"label": "Busway tap-off", "definition": "A plug-in tap-off unit that takes power from a busway run."},
        },
    },
    "CouplingGender": {
        "label": "Coupling gender",
        "definition": "Which half of a quick-disconnect coupling pair a connection point is.",
        "values": {
            "Plug": {"label": "Plug", "definition": "The male half of a quick-disconnect coupling."},
            "Socket": {"label": "Socket", "definition": "The female half of a quick-disconnect coupling."},
            "Genderless": {"label": "Genderless", "definition": "A coupling half that mates with an identical half of the same coupling type, so the pair has no male and female side."},
        },
    },
    "CoolingMethod": {
        "label": "Cooling method",
        "definition": "How a piece of IT equipment gets rid of its heat.",
        "values": {
            "AirCooled": {"label": "Air cooled", "definition": "All heat leaves the equipment in the air drawn through it by fans."},
            "LiquidCooled": {"label": "Liquid cooled", "definition": "Most or all heat leaves the equipment in a liquid loop through cold plates, with little or none left to the air."},
            "LiquidAssistedAirCooled": {"label": "Liquid-assisted air cooled", "definition": "Heat is moved by liquid inside the equipment to a radiator, from which fans carry it away in the air."},
            "Immersion": {"label": "Immersion", "definition": "The equipment sits in a dielectric liquid that removes its heat by direct contact."},
        },
    },
    "LiquidCoolingWaterClass": {
        "label": "Liquid cooling water class",
        "definition": "The ASHRAE TC 9.9 classes of facility water supply temperature for liquid-cooled IT equipment.",
        "values": {
            "W17": {"label": "W17", "definition": "Facility water supplied at up to 17 degrees Celsius."},
            "W27": {"label": "W27", "definition": "Facility water supplied at up to 27 degrees Celsius."},
            "W32": {"label": "W32", "definition": "Facility water supplied at up to 32 degrees Celsius."},
            "W40": {"label": "W40", "definition": "Facility water supplied at up to 40 degrees Celsius."},
            "W45": {"label": "W45", "definition": "Facility water supplied at up to 45 degrees Celsius."},
            "W+": {"label": "W+", "definition": "Facility water supplied above 45 degrees Celsius."},
        },
    },
}

# ---------------------------------------------------------------------------------------------
# Property classes.

PROPERTIES = {
    "LineToLineVoltage": {
        "label": "Line-to-line voltage",
        "definition": "The AC voltage measured between two phase conductors.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Voltage,
        "units": [UNIT.V, UNIT.KiloV],
    },
    "LineToNeutralVoltage": {
        "label": "Line-to-neutral voltage",
        "definition": "The AC voltage measured between a phase conductor and neutral.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Voltage,
        "units": [UNIT.V, UNIT.KiloV],
    },
    "DCVoltage": {
        "label": "DC voltage",
        "definition": "The voltage of a direct-current supply or input.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Voltage,
        "units": [UNIT.V, UNIT.KiloV],
    },
    "PortDataRate": {
        "label": "Port data rate",
        "definition": "The data rate one data port carries in one direction.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.DataRate,
        "units": [UNIT["GigaBIT-PER-SEC"], UNIT["TeraBIT-PER-SEC"]],
    },
    "CoolingCapacity": {
        "label": "Cooling capacity",
        "definition": "The rate of heat a cooling device can remove under stated conditions.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.HeatFlowRate,
        "units": [UNIT.W, UNIT.KiloW, UNIT.MegaW],
    },
    "HeatLoad": {
        "label": "Heat load",
        "definition": "The rate of heat a device gives off, either to a liquid loop or to the air, that cooling must remove.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.HeatFlowRate,
        "units": [UNIT.W, UNIT.KiloW, UNIT.MegaW],
    },
    "ApproachTemperatureDifference": {
        "label": "Approach temperature difference",
        "definition": "The difference between the temperature a heat exchanger delivers on one side and the incoming temperature on the other side, used to rate CDU capacity.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.TemperatureDifference,
        "units": [UNIT.K, UNIT.DEG_C],
    },
    "ConnectionPointCount": {
        "label": "Connection point count",
        "definition": "The number of identical connection points that one connection point record stands for, such as the receptacles of one type on a power distribution unit.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Count,
        "units": [UNIT.NUM],
    },
    "PressureDrop": {
        "label": "Pressure drop",
        "definition": "The loss of fluid pressure across a device or connection at a stated flow.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Pressure,
        "units": [UNIT.KiloPA, UNIT.BAR, UNIT.PSI],
    },
    "NetworkProtocolProperty": {
        "label": "Network protocol property",
        "definition": "An enumerated property naming a protocol a data port or cable carries.",
        "parent": S223.EnumerableProperty,
        "enumeration": "NetworkProtocol",
    },
    "InfiniBandGenerationProperty": {
        "label": "InfiniBand generation property",
        "definition": "An enumerated property naming an InfiniBand generation a data port supports.",
        "parent": S223.EnumerableProperty,
        "enumeration": "InfiniBandGeneration",
    },
    "PluggableFormFactorProperty": {
        "label": "Pluggable form factor property",
        "definition": "An enumerated property naming the form factor of a pluggable cage or plug.",
        "parent": S223.EnumerableProperty,
        "enumeration": "PluggableFormFactor",
    },
    "FiberConnectorProperty": {
        "label": "Fiber connector property",
        "definition": "An enumerated property naming the optical connector of a fiber port.",
        "parent": S223.EnumerableProperty,
        "enumeration": "FiberConnector",
    },
    "PowerConnectorProperty": {
        "label": "Power connector property",
        "definition": "An enumerated property naming the connector or terminal type of a power inlet or outlet.",
        "parent": S223.EnumerableProperty,
        "enumeration": "PowerConnector",
    },
    "CouplingGenderProperty": {
        "label": "Coupling gender property",
        "definition": "An enumerated property naming which half of a quick-disconnect pair a liquid connection point is.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CouplingGender",
    },
    "CoolingMethodProperty": {
        "label": "Cooling method property",
        "definition": "An enumerated property naming how a piece of IT equipment rejects its heat.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CoolingMethod",
    },
    "Width": {
        "label": "Width",
        "definition": "The outer width of a piece of equipment as installed, side to side.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Width,
        "units": [UNIT.MilliM, UNIT.M, UNIT.IN],
    },
    "Depth": {
        "label": "Depth",
        "definition": "The outer depth of a piece of equipment as installed, front to back.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Depth,
        "units": [UNIT.MilliM, UNIT.M, UNIT.IN],
    },
    "Height": {
        "label": "Height",
        "definition": "The outer height of a piece of equipment as installed.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Height,
        "units": [UNIT.MilliM, UNIT.M, UNIT.IN],
    },
    "LiquidCoolingWaterClassProperty": {
        "label": "Liquid cooling water class property",
        "definition": "An enumerated property naming the ASHRAE water class a liquid-cooled device is designed for.",
        "parent": S223.EnumerableProperty,
        "enumeration": "LiquidCoolingWaterClass",
    },
}
