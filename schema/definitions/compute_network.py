"""Compute and network domain: racks and rack-scale systems, servers and trays, switches, network adapters,
transceivers, cables, the processors and modules inside them, and the system classes that group them.

Classes follow docs/MODELING.md: a subclass only where the connection points or media differ (R3) or a
decision names it (CN4 to CN10); variants with the same connection points are enumeration values. Connection
points, media and the shared enumerations (protocol, InfiniBand generation, pluggable form factor, fiber
connector) come from common.py. A port that runs more than one protocol takes the closest common medium,
s223:Electricity-Signal for electrical lanes or s223:Infrared-Signal for light, and lists its protocols and
rates as enumeration values (CN3).
"""

from .namespaces import AIF, BRICK, QK, S223, UNIT

# Media used in the connection point requirements below.
ELECTRICAL_SIGNAL = S223["Electricity-Signal"]  # any electrical data signal: Ethernet, InfiniBand, NVLink
PCIE_SIGNAL = AIF["Signal-PCIe"]
OPTICAL_SIGNAL = S223["Infrared-Signal"]  # light in a fiber: Ethernet or InfiniBand
WIRED_ETHERNET = S223["Signal-WiredEthernet"]
DC_POWER = S223["Electricity-DC"]

# ---------------------------------------------------------------------------------------------
# Equipment: one model number sold as one product (R6).

EQUIPMENT = {
    "ICTRack": {
        "label": "Information and communications technology rack",
        "definition": "A frame or enclosure, sized in rack units, into which servers, switches and other information and communications technology (ICT) equipment are mounted.",
        "parents": [BRICK.ICT_Rack, S223.Equipment],
        "subclasses": {
            "RackScaleSystem": {
                "label": "Rack-scale system",
                "definition": "A rack sold as one integrated product together with its compute or switch trays, power shelves, busbar and any coolant manifolds, so that it is installed and connected to facility power, cooling and networks as one unit.",
                "connection_points": [
                    {"class": AIF.PowerInlet, "min": 1,
                     "message": "A rack-scale system takes facility power at one or more power inlets."},
                ],
            },
        },
    },
    "Server": {
        "label": "Server",
        "definition": "A rack-mounted computer that runs workloads or services for other machines over a network.",
        "parents": [BRICK.Server, S223.ServerComputer],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A server takes power at one or more power inlets."},
            {"class": AIF.ManagementPort, "medium": WIRED_ETHERNET, "min": 1,
             "message": "A server has a copper Ethernet management port to its management controller."},
        ],
        "subclasses": {
            "ComputeTray": {
                "label": "Compute tray",
                "definition": "A server built as a tray to a shared mechanical design, which slides into a rack-scale system and draws power from the rack busbar.",
                "connection_points": [
                    {"class": AIF.PowerInlet, "medium": DC_POWER, "min": 1,
                     "message": "A compute tray takes direct-current power from the rack busbar."},
                    {"class": AIF.PluggableCage, "medium": ELECTRICAL_SIGNAL, "min": 1,
                     "message": "A compute tray has pluggable cages on its network adapters for the scale-out and storage networks."},
                ],
            },
        },
    },
    "NetworkSwitch": {
        "label": "Network switch",
        "definition": "A device that forwards data between its ports to join servers, adapters and other switches into one network.",
        "parents": [BRICK.Data_Network_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.PowerInlet, "min": 1,
             "message": "A network switch takes power at one or more power inlets."},
            {"class": AIF.ManagementPort, "medium": WIRED_ETHERNET, "min": 1,
             "message": "A network switch has a copper Ethernet management port."},
        ],
        "subclasses": {
            "EthernetSwitch": {
                "label": "Ethernet switch",
                "definition": "A network switch that forwards Ethernet frames between its ports.",
                "parents": [BRICK.Ethernet_Switch, S223.EthernetSwitch],
            },
            "InfiniBandSwitch": {
                "label": "InfiniBand switch",
                "definition": "A network switch that forwards InfiniBand traffic between host channel adapters and other switches, with routes set by a subnet manager.",
            },
            "NVLinkSwitchTray": {
                "label": "NVLink switch tray",
                "definition": "A tray of a rack-scale system that holds NVLink switch chips and joins the graphics processing units of all compute trays in the rack into one NVLink domain.",
                "connection_points": [
                    {"class": AIF.DataPort, "medium": AIF["Signal-NVLink"], "min": 1,
                     "message": "An NVLink switch tray has NVLink ports that join it to the rack interconnect."},
                    {"class": AIF.PowerInlet, "medium": DC_POWER, "min": 1,
                     "message": "An NVLink switch tray takes direct-current power from the rack busbar."},
                ],
            },
        },
    },
    "NetworkAdapter": {
        "label": "Network adapter",
        "definition": "An add-in card or board that connects a host to a network through its ports and handles link protocol and transport offloads for that host.",
        "parents": [BRICK.Data_Network_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.CardHostConnector, "medium": PCIE_SIGNAL, "min": 1,
             "message": "A network adapter plugs into an expansion slot of its host through a host connector."},
            {"class": AIF.DataPort, "medium": ELECTRICAL_SIGNAL, "min": 1,
             "message": "A network adapter has at least one electrical network port, usually a pluggable cage."},
        ],
        "subclasses": {
            "DPU": {
                "label": "Data processing unit",
                "definition": "A network adapter with its own general-purpose processor cores and memory that runs networking, storage or security software apart from the host processors, and that is managed through its own management port.",
                "connection_points": [
                    {"class": AIF.ManagementPort, "medium": WIRED_ETHERNET, "min": 1,
                     "message": "A data processing unit has its own copper Ethernet management port."},
                ],
            },
        },
    },
    "OpticalTransceiver": {
        "label": "Optical transceiver",
        "definition": "A pluggable module that converts the electrical lanes of a pluggable cage into light on one or more optical fiber connectors, and light back into electrical lanes.",
        "parents": [BRICK.Data_Network_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.PluggablePlug, "medium": ELECTRICAL_SIGNAL, "min": 1,
             "message": "An optical transceiver has a pluggable plug that inserts into a pluggable cage."},
            {"class": AIF.FiberPort, "medium": OPTICAL_SIGNAL, "min": 1,
             "message": "An optical transceiver has at least one fiber port for optical connectors."},
        ],
    },
    "NetworkCable": {
        "label": "Network cable",
        "definition": "A cable product sold under one part number that carries data between the ports of network equipment.",
        "parents": [BRICK.Data_Network_Equipment, S223.Equipment],
        "subclasses": {
            "PluggableCableAssembly": {
                "label": "Pluggable cable assembly",
                "definition": "A network cable whose ends are fixed pluggable plugs that go straight into pluggable cages, built with copper conductors or with optics sealed into its ends, including breakout versions with one plug at one end and several at the other.",
                "connection_points": [
                    {"class": AIF.PluggablePlug, "medium": ELECTRICAL_SIGNAL, "min": 2,
                     "message": "A pluggable cable assembly has a pluggable plug at each end."},
                ],
            },
            "FiberCable": {
                "label": "Fiber cable",
                "definition": "A passive network cable of optical fiber with optical connectors at its ends, used to join the fiber ports of transceivers, patch panels and co-packaged optics switches.",
                "close_match": [S223.FiberOpticCable],
                "connection_points": [
                    {"class": AIF.FiberPort, "medium": OPTICAL_SIGNAL, "min": 2,
                     "message": "A fiber cable has an optical connector at each end."},
                ],
                # Its fiber grade is a FiberGradeProperty value (decision CN8): the grades share connection points.
            },
        },
    },
    "PatchPanel": {
        "label": "Patch panel",
        "definition": "A rack-mounted panel of fixed connector ports where structured cabling runs are cross-connected to equipment cables.",
        "parents": [BRICK.Data_Network_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.DataPort, "min": 2,
             "message": "A patch panel has connector ports on which cables meet."},
        ],
    },
}

# ---------------------------------------------------------------------------------------------
# Systems: design-level groupings of several products (R6, decision CN10). An AI factory as a whole is a
# brick:Site and needs no class.

SYSTEMS = {
    "NetworkPlane": {
        "label": "Network plane",
        "definition": "A set of switches, adapter ports and cables that forms one network of a cluster, kept apart from the other networks and carrying one class of traffic, such as the compute fabric, the storage fabric or the out-of-band management network.",
        "parents": [BRICK.Collection, S223.System],
    },
    "ScalableUnit": {
        "label": "Scalable unit",
        "definition": "A repeatable building block of a cluster design, made of a fixed number of graphics processing unit (GPU) servers or rack-scale systems with the leaf switches and cables that connect them, so that a cluster grows one unit at a time.",
        "parents": [BRICK.Collection, S223.System],
    },
    "Pod": {
        "label": "Pod",
        "definition": "A cluster design assembled from one or more scalable units, or from several kinds of rack-scale systems, together with the shared storage, management and fabric equipment they need to work as one artificial intelligence (AI) computer.",
        "parents": [BRICK.Collection, S223.System],
    },
}

# ---------------------------------------------------------------------------------------------
# Components: what is installed inside equipment, linked with brick:hasPart (R6).

COMPONENTS = {
    "GPU": {
        "label": "Graphics processing unit",
        "definition": "A graphics processing unit (GPU) package that performs the parallel computation of artificial intelligence training and inference, mounted on a GPU module or an add-in card.",
        "parents": [BRICK.ICT_Hardware, S223.Equipment],
    },
    "CPU": {
        "label": "Central processing unit",
        "definition": "A central processing unit (CPU) package that runs the operating system and general-purpose work of a server, tray or superchip.",
        "parents": [BRICK.ICT_Hardware, S223.Equipment],
    },
    "GPUModule": {
        "label": "Graphics processing unit module",
        "definition": "A replaceable assembly that carries one or more graphics processing units with their high-speed links and power delivery and is installed as one unit in a server or compute tray.",
        "parents": [BRICK.ICT_Hardware, S223.Equipment],
        "subclasses": {
            "GPUBaseboard": {
                "label": "Graphics processing unit baseboard",
                "definition": "A graphics processing unit (GPU) module that carries four or eight socketed GPUs joined by NVLink on one board, installed as a single unit in a GPU server.",
            },
            "Superchip": {
                "label": "Superchip",
                "definition": "A graphics processing unit (GPU) module that joins a central processing unit and one or more GPUs through a coherent chip-to-chip link on one board, used in the compute trays of rack-scale systems.",
            },
        },
    },
    "LineCard": {
        "label": "Line card",
        "definition": "A replaceable board in a modular switch chassis that carries some of the chassis ports or part of its internal switching fabric.",
        "parents": [BRICK.Data_Network_Equipment, S223.Equipment],
    },
    "ManagementController": {
        "label": "Management controller",
        "definition": "A service processor on its own chip, card or module, such as a baseboard management controller (BMC), that monitors and controls a server, tray, switch or chassis and gives out-of-band access to it apart from the main processors.",
        "parents": [BRICK.Controller, S223.Controller],
    },
    "InterconnectCartridge": {
        "label": "Interconnect cartridge",
        "definition": "A cable assembly fixed at the rear of a rack-scale system that joins the blind-mate connectors of its compute and switch trays into the scale-up interconnect of the rack.",
        "parents": [BRICK.Data_Network_Equipment, S223.Equipment],
        "connection_points": [
            {"class": AIF.DataPort, "min": 2,
             "message": "An interconnect cartridge has blind-mate connectors that mate with the trays of the rack."},
        ],
    },
    "Motherboard": {
        "label": "Motherboard",
        "definition": "The main circuit board of a server or tray, carrying its processor sockets, memory slots and expansion slots, when it is named as a part with its own model number.",
        "parents": [BRICK.ICT_Hardware, S223.Equipment],
    },
    "ServerChassis": {
        "label": "Server chassis",
        "definition": "The enclosure of a server with its fans and its drive and power supply bays, when it is named as a part with its own model number to which a motherboard and processors are added.",
        "parents": [BRICK.ICT_Hardware, S223.Equipment],
    },
    "RiserCard": {
        "label": "Riser card",
        "definition": "A circuit board that plugs into an expansion slot of a motherboard and provides one or more expansion slots in another position or orientation.",
        "parents": [BRICK.ICT_Hardware, S223.Equipment],
        "connection_points": [
            {"class": AIF.CardHostConnector,
             "message": "A riser card plugs into an expansion slot of its motherboard."},
            {"class": AIF.ExpansionSlot,
             "message": "A riser card provides at least one expansion slot."},
        ],
    },
}

# ---------------------------------------------------------------------------------------------
# Connection points that common.py does not cover: the host interface of add-in cards.

CONNECTION_POINTS = {
    "ExpansionSlot": {
        "label": "Expansion slot",
        "definition": "A receptacle on a server or tray board, such as a PCI Express (PCIe) slot, an Open Compute Project network interface card (OCP NIC 3.0) bay or a mezzanine connector, that accepts an add-in card and links it to the host.",
        "parents": [S223.BidirectionalConnectionPoint],
    },
    "CardHostConnector": {
        "label": "Card host connector",
        "definition": "The connector by which an add-in card such as a network adapter plugs into an expansion slot of its host, usually a card edge.",
        "parents": [S223.BidirectionalConnectionPoint],
    },
}

# ---------------------------------------------------------------------------------------------
# Enumerations (R4).

ENUMERATIONS = {
    "GPUPlatform": {
        "label": "GPU platform",
        "definition": "NVIDIA GPU platforms that servers and rack-scale systems from several vendors are built on.",
        "values": {
            "HGX-H100": {"label": "HGX H100", "definition": "The NVIDIA HGX baseboard platform with eight H100 GPUs."},
            "HGX-H200": {"label": "HGX H200", "definition": "The NVIDIA HGX baseboard platform with eight H200 GPUs."},
            "HGX-B200": {"label": "HGX B200", "definition": "The NVIDIA HGX baseboard platform with eight B200 GPUs."},
            "HGX-B300": {"label": "HGX B300", "definition": "The NVIDIA HGX baseboard platform with eight B300 GPUs."},
            "GB200-NVL72": {"label": "GB200 NVL72", "definition": "The NVIDIA rack-scale platform joining 72 Blackwell GPUs and 36 Grace CPUs in one NVLink domain."},
            "GB300-NVL72": {"label": "GB300 NVL72", "definition": "The NVIDIA rack-scale platform joining 72 Blackwell Ultra GPUs and 36 Grace CPUs in one NVLink domain."},
            "VeraRubin-NVL72": {"label": "Vera Rubin NVL72", "definition": "The NVIDIA rack-scale platform built on Vera CPUs and Rubin GPUs in one NVLink domain."},
        },
    },
    "ServerFunction": {
        "label": "Server function",
        "definition": "The main job a server is built or deployed for.",
        "values": {
            "AcceleratedCompute": {"label": "Accelerated compute", "definition": "Runs artificial intelligence training or inference on the graphics processing units the server contains."},
            "CPUCompute": {"label": "Central processing unit compute", "definition": "Runs workloads on central processing units only, such as simulation or agent sandboxes."},
            "ControlPlane": {"label": "Control plane", "definition": "Runs cluster management, provisioning, scheduling or user login services for the other nodes."},
            "Storage": {"label": "Storage", "definition": "Serves files, objects or blocks from its own drives to other nodes over the network."},
            "FabricManagement": {"label": "Fabric management", "definition": "Runs software that discovers, configures and monitors a whole InfiniBand or Ethernet fabric from outside the switches."},
        },
    },
    "NetworkAdapterFunction": {
        "label": "Network adapter function",
        "definition": "The intended use of a network adapter, which sets the offloads it is built for.",
        "values": {
            "NIC": {"label": "Network interface card", "definition": "A conventional adapter for general server networking."},
            "SuperNIC": {"label": "SuperNIC", "definition": "An adapter tuned for the scale-out fabric of a graphics processing unit cluster, with remote direct memory access, congestion control and telemetry offloads."},
        },
    },
    "AddInCardFormFactor": {
        "label": "Add-in card form factor",
        "definition": "The mechanical outlines of add-in cards and of the expansion slots that accept them.",
        "values": {
            "PCIe-HHHL": {"label": "PCI Express half height, half length", "definition": "A PCI Express (PCIe) add-in card of half height and half length."},
            "PCIe-FHHL": {"label": "PCI Express full height, half length", "definition": "A PCI Express add-in card of full height and half length."},
            "PCIe-FHFL": {"label": "PCI Express full height, full length", "definition": "A PCI Express add-in card of full height and full length."},
            "OCP3-SFF": {"label": "Open Compute Project network interface card 3.0, small form factor", "definition": "The small card outline of the Open Compute Project network interface card (OCP NIC) 3.0 specification, inserted from the outside of a server."},
            "OCP3-LFF": {"label": "Open Compute Project network interface card 3.0, large form factor", "definition": "The large card outline of the Open Compute Project network interface card (OCP NIC) 3.0 specification."},
            "Mezzanine": {"label": "Mezzanine card", "definition": "A card that plugs into a board-specific mezzanine connector of a compute board instead of a standard slot."},
            "OCP3-TSFF": {"label": "Open Compute Project network interface card 3.0, tall small form factor", "definition": "The taller variant of the small card outline of the Open Compute Project network interface card (OCP NIC) 3.0 specification, with room for a larger heat sink."},
            "M.2-2242": {"label": "M.2 2242", "definition": "An M.2 module 22 millimeters wide and 42 millimeters long."},
            "M.2-2280": {"label": "M.2 2280", "definition": "An M.2 module 22 millimeters wide and 80 millimeters long."},
            "M.2-22110": {"label": "M.2 22110", "definition": "An M.2 module 22 millimeters wide and 110 millimeters long."},
        },
    },
    "PCIeGeneration": {
        "label": "PCI Express generation",
        "definition": "The PCI Express (PCIe) revisions, each with its own transfer rate per lane.",
        "values": {
            "Gen3": {"label": "PCI Express 3.0", "definition": "PCI Express 3.0, at 8 gigatransfers per second per lane."},
            "Gen4": {"label": "PCI Express 4.0", "definition": "PCI Express 4.0, at 16 gigatransfers per second per lane."},
            "Gen5": {"label": "PCI Express 5.0", "definition": "PCI Express 5.0, at 32 gigatransfers per second per lane."},
            "Gen6": {"label": "PCI Express 6.0", "definition": "PCI Express 6.0, at 64 gigatransfers per second per lane."},
        },
    },
    "SwitchChassisForm": {
        "label": "Switch chassis form",
        "definition": "Whether a switch is built as one fixed unit or as a chassis of replaceable line cards.",
        "values": {
            "Fixed": {"label": "Fixed", "definition": "All ports and switching silicon are built into one unit that is replaced as a whole."},
            "Modular": {"label": "Modular chassis", "definition": "Ports and switching fabric sit on line cards that are installed and replaced separately in a chassis."},
        },
    },
    "SwitchManagementMode": {
        "label": "Switch management mode",
        "definition": "Whether a switch runs its own management software and subnet manager or depends on an external fabric manager.",
        "values": {
            "InternallyManaged": {"label": "Internally managed", "definition": "The switch runs its own operating system and can host the subnet manager of its fabric."},
            "ExternallyManaged": {"label": "Externally managed", "definition": "The switch has no onboard subnet manager and is configured and monitored by an external fabric manager."},
        },
    },
    "ChassisAirflowDirection": {
        "label": "Chassis airflow direction",
        "definition": "The direction in which the fans of rack equipment move air, relative to its port side and its power-supply side.",
        "values": {
            "PowerToConnector": {"label": "Power side to connector side", "definition": "Air enters at the power-supply side and leaves at the port side, also written P2C."},
            "ConnectorToPower": {"label": "Connector side to power side", "definition": "Air enters at the port side and leaves at the power-supply side, also written C2P."},
        },
    },
    "CableAssemblyTechnology": {
        "label": "Cable assembly technology",
        "definition": "How a pluggable cable assembly carries signals between its plugs.",
        "values": {
            "DAC": {"label": "Direct-attach copper", "definition": "Passive twinaxial copper conductors with no signal-conditioning electronics in the plugs."},
            "ACC": {"label": "Active copper", "definition": "Twinaxial copper conductors with signal-conditioning electronics in the plugs to extend their reach."},
            "AOC": {"label": "Active optical", "definition": "Optical fiber with lasers and photodetectors sealed into the plugs, so the link is optical without separate transceivers."},
        },
    },
    "OpticalReachClass": {
        "label": "Optical reach class",
        "definition": "The codes that the physical layer names of the IEEE 802.3 Ethernet standard and the optical multi-source agreements use for an optical interface, combining reach, fiber type and number of optical lanes, which have to match at both ends of a link.",
        "values": {
            "SR4": {"label": "SR4", "definition": "Short reach (SR) over four pairs of multimode fibers at 850 nanometers."},
            "SR8": {"label": "SR8", "definition": "Short reach over eight pairs of multimode fibers at 850 nanometers."},
            "DR1": {"label": "DR1", "definition": "Data-center reach (DR) of 500 meters over one pair of single-mode fibers at 1310 nanometers."},
            "DR4": {"label": "DR4", "definition": "Data-center reach of 500 meters over four pairs of single-mode fibers at 1310 nanometers."},
            "DR8": {"label": "DR8", "definition": "Data-center reach of 500 meters over eight pairs of single-mode fibers at 1310 nanometers."},
            "FR4": {"label": "FR4", "definition": "Reach of 2 kilometers over one pair of single-mode fibers that carries four wavelengths."},
            "LR4": {"label": "LR4", "definition": "Long reach (LR) of 10 kilometers over one pair of single-mode fibers that carries four wavelengths."},
        },
    },
    "FiberGrade": {
        "label": "Fiber grade",
        "definition": "The ISO/IEC 11801 categories of optical fiber, which set the reach a fiber cable supports at a given rate.",
        "values": {
            "OM3": {"label": "OM3", "definition": "Laser-optimized multimode fiber of category OM3.",
                    "close_match": [S223["FiberOpticCable-OM3"]]},
            "OM4": {"label": "OM4", "definition": "Laser-optimized multimode fiber of category OM4, with a higher modal bandwidth than OM3.",
                    "close_match": [S223["FiberOpticCable-OM4"]]},
            "OM5": {"label": "OM5", "definition": "Wideband multimode fiber of category OM5, specified for several wavelengths between 850 and 950 nanometers.",
                    "close_match": [S223["FiberOpticCable-OM5"]]},
            "OS2": {"label": "OS2", "definition": "Low-water-peak single-mode fiber of category OS2.",
                    "close_match": [S223["FiberOpticCable-OS2"]]},
        },
    },
    "FiberPolish": {
        "label": "Fiber end-face polish",
        "definition": "The finish of the fiber end faces inside an optical connector, which has to be the same on both mating halves.",
        "values": {
            "APC": {"label": "Angled physical contact", "definition": "End faces polished at an angle of about eight degrees, usually in a green connector body."},
            "UPC": {"label": "Ultra physical contact", "definition": "End faces polished flat with a slight dome, usually in a blue or aqua connector body."},
        },
    },
    "FiberPolarity": {
        "label": "Fiber polarity",
        "definition": "How a multi-fiber cable maps the fiber positions at one end to those at the other end, following the polarity methods of the Telecommunications Industry Association TIA-568 cabling standard.",
        "values": {
            "TypeA": {"label": "Type A, straight", "definition": "Each fiber position at one end goes to the same position at the other end."},
            "TypeB": {"label": "Type B, reversed", "definition": "The order of fiber positions is reversed from end to end, so the transmit lanes of one transceiver meet the receive lanes of the other."},
            "TypeC": {"label": "Type C, pair-flipped", "definition": "The two fibers of each adjacent pair swap places from end to end."},
        },
    },
    "EthernetRate": {
        "label": "Ethernet rate",
        "definition": "The data rates of Ethernet under the Institute of Electrical and Electronics Engineers (IEEE) 802.3 standard that a port, adapter or cable supports.",
        "values": {
            "1GbE": {"label": "1 gigabit Ethernet", "definition": "Ethernet at 1 gigabit per second."},
            "10GbE": {"label": "10 gigabit Ethernet", "definition": "Ethernet at 10 gigabits per second."},
            "25GbE": {"label": "25 gigabit Ethernet", "definition": "Ethernet at 25 gigabits per second."},
            "40GbE": {"label": "40 gigabit Ethernet", "definition": "Ethernet at 40 gigabits per second."},
            "50GbE": {"label": "50 gigabit Ethernet", "definition": "Ethernet at 50 gigabits per second."},
            "100GbE": {"label": "100 gigabit Ethernet", "definition": "Ethernet at 100 gigabits per second."},
            "200GbE": {"label": "200 gigabit Ethernet", "definition": "Ethernet at 200 gigabits per second."},
            "400GbE": {"label": "400 gigabit Ethernet", "definition": "Ethernet at 400 gigabits per second."},
            "800GbE": {"label": "800 gigabit Ethernet", "definition": "Ethernet at 800 gigabits per second."},
            "1.6TbE": {"label": "1.6 terabit Ethernet", "definition": "Ethernet at 1.6 terabits per second."},
        },
    },
    "NVLinkGeneration": {
        "label": "NVLink generation",
        "definition": "The generations of NVIDIA NVLink, which have to match between the graphics processing units (GPUs) and NVLink switches of one domain.",
        "values": {
            "NVLink4": {"label": "NVLink 4", "definition": "The fourth NVLink generation, used with Hopper graphics processing units."},
            "NVLink5": {"label": "NVLink 5", "definition": "The fifth NVLink generation, used with Blackwell graphics processing units."},
            "NVLink6": {"label": "NVLink 6", "definition": "The sixth NVLink generation, used with Rubin graphics processing units."},
        },
    },
    "NetworkPlaneFunction": {
        "label": "Network plane function",
        "definition": "The class of traffic that a network plane, or a switch or port serving it, carries in a cluster.",
        "values": {
            "ScaleUp": {"label": "Scale-up", "definition": "Links among the graphics processing units of one NVLink domain, within a rack or across a few racks."},
            "ComputeFabric": {"label": "Compute fabric", "definition": "East-west traffic between the graphics processing units of different servers or racks, also called scale-out."},
            "StorageFabric": {"label": "Storage fabric", "definition": "Traffic between compute nodes and shared high-performance storage."},
            "InBandManagement": {"label": "In-band management", "definition": "Provisioning, job control, user access and user storage traffic on a routed Ethernet network."},
            "OutOfBandManagement": {"label": "Out-of-band management", "definition": "Traffic to the management controllers and management ports of every device, kept apart from all other networks."},
            "FrontEnd": {"label": "Front end", "definition": "North-south traffic between the cluster and the networks outside it, such as the customer edge or the internet."},
        },
    },
    "FabricTier": {
        "label": "Fabric tier",
        "definition": "The level a switch occupies in a leaf-spine network fabric.",
        "values": {
            "Leaf": {"label": "Leaf", "definition": "Connects directly to the ports of servers, storage or other end devices."},
            "Spine": {"label": "Spine", "definition": "Connects leaf switches to one another and carries no end-device links."},
            "Core": {"label": "Core", "definition": "Connects spine switches or spine groups across several scalable units, also called super-spine."},
        },
    },
    "RackMountingStandard": {
        "label": "Rack mounting standard",
        "definition": "The mechanical standards that set the mounting width and rail pattern of racks and of the equipment mounted in them.",
        "values": {
            "EIA-310": {"label": "EIA-310 19-inch", "definition": "The Electronic Industries Alliance EIA-310 standard for 19-inch wide mounting in rack units of 44.45 millimeters."},
            "ORv3": {"label": "Open Rack V3", "definition": "The Open Compute Project Open Rack version 3 standard, with 21-inch wide equipment bays and a rear power busbar."},
            "MGX": {"label": "MGX rack", "definition": "The NVIDIA MGX rack specification published through the Open Compute Project, based on Open Rack V3 and adapted to also hold 19-inch equipment."},
        },
    },
    "LaneModulation": {
        "label": "Lane modulation",
        "definition": "The ways the signal on one electrical or optical lane of a data link encodes its bits.",
        "values": {
            "NRZ": {"label": "NRZ", "definition": "Non-return-to-zero signalling with two amplitude levels, carrying one bit per symbol."},
            "PAM4": {"label": "PAM4", "definition": "Four-level pulse amplitude modulation, carrying two bits per symbol."},
        },
    },
}

# ---------------------------------------------------------------------------------------------
# Property classes: one per enumeration kind above, plus quantities whose kind alone does not say what they mean.

PROPERTIES = {
    "GPUPlatformProperty": {
        "label": "GPU platform property",
        "definition": "An enumerated property naming the GPU platform a server or rack-scale system is built on.",
        "parent": S223.EnumerableProperty,
        "enumeration": "GPUPlatform",
    },
    "ServerFunctionProperty": {
        "label": "Server function property",
        "definition": "An enumerated property naming the main job of a server.",
        "parent": S223.EnumerableProperty,
        "enumeration": "ServerFunction",
    },
    "NetworkAdapterFunctionProperty": {
        "label": "Network adapter function property",
        "definition": "An enumerated property naming the intended use of a network adapter.",
        "parent": S223.EnumerableProperty,
        "enumeration": "NetworkAdapterFunction",
    },
    "AddInCardFormFactorProperty": {
        "label": "Add-in card form factor property",
        "definition": "An enumerated property naming the outline of an add-in card, on its host connector, or the outlines an expansion slot accepts.",
        "parent": S223.EnumerableProperty,
        "enumeration": "AddInCardFormFactor",
    },
    "PCIeGenerationProperty": {
        "label": "PCI Express generation property",
        "definition": "An enumerated property naming a PCI Express generation that a host connector or expansion slot supports.",
        "parent": S223.EnumerableProperty,
        "enumeration": "PCIeGeneration",
    },
    "SwitchChassisFormProperty": {
        "label": "Switch chassis form property",
        "definition": "An enumerated property naming whether a switch is fixed or a modular chassis.",
        "parent": S223.EnumerableProperty,
        "enumeration": "SwitchChassisForm",
    },
    "SwitchManagementModeProperty": {
        "label": "Switch management mode property",
        "definition": "An enumerated property naming whether a switch is managed internally or by an external fabric manager.",
        "parent": S223.EnumerableProperty,
        "enumeration": "SwitchManagementMode",
    },
    "ChassisAirflowDirectionProperty": {
        "label": "Chassis airflow direction property",
        "definition": "An enumerated property naming the direction in which a piece of rack equipment moves cooling air.",
        "parent": S223.EnumerableProperty,
        "enumeration": "ChassisAirflowDirection",
    },
    "CableAssemblyTechnologyProperty": {
        "label": "Cable assembly technology property",
        "definition": "An enumerated property naming whether a pluggable cable assembly is passive copper, active copper or active optical.",
        "parent": S223.EnumerableProperty,
        "enumeration": "CableAssemblyTechnology",
    },
    "OpticalReachClassProperty": {
        "label": "Optical reach class property",
        "definition": "An enumerated property naming the optical reach class of a fiber port.",
        "parent": S223.EnumerableProperty,
        "enumeration": "OpticalReachClass",
    },
    "FiberGradeProperty": {
        "label": "Fiber grade property",
        "definition": "An enumerated property naming the grade of optical fiber in a fiber cable or that a fiber port is rated for.",
        "parent": S223.EnumerableProperty,
        "enumeration": "FiberGrade",
    },
    "FiberPolishProperty": {
        "label": "Fiber end-face polish property",
        "definition": "An enumerated property naming the end-face polish of the optical connector at a fiber port.",
        "parent": S223.EnumerableProperty,
        "enumeration": "FiberPolish",
    },
    "FiberPolarityProperty": {
        "label": "Fiber polarity property",
        "definition": "An enumerated property naming the polarity method of a multi-fiber cable.",
        "parent": S223.EnumerableProperty,
        "enumeration": "FiberPolarity",
    },
    "EthernetRateProperty": {
        "label": "Ethernet rate property",
        "definition": "An enumerated property naming an Ethernet rate that a data port or cable supports.",
        "parent": S223.EnumerableProperty,
        "enumeration": "EthernetRate",
    },
    "NVLinkGenerationProperty": {
        "label": "NVLink generation property",
        "definition": "An enumerated property naming the NVLink generation of a port, module or tray.",
        "parent": S223.EnumerableProperty,
        "enumeration": "NVLinkGeneration",
    },
    "NetworkPlaneFunctionProperty": {
        "label": "Network plane function property",
        "definition": "An enumerated property naming the class of traffic a network plane, switch or port serves.",
        "parent": S223.EnumerableProperty,
        "enumeration": "NetworkPlaneFunction",
    },
    "FabricTierProperty": {
        "label": "Fabric tier property",
        "definition": "An enumerated property naming the tier a switch occupies in a leaf-spine fabric.",
        "parent": S223.EnumerableProperty,
        "enumeration": "FabricTier",
    },
    "RackMountingStandardProperty": {
        "label": "Rack mounting standard property",
        "definition": "An enumerated property naming the mounting standard a rack provides or a piece of equipment needs.",
        "parent": S223.EnumerableProperty,
        "enumeration": "RackMountingStandard",
    },
    "LaneCount": {
        "label": "Lane count",
        "definition": "The number of electrical or optical lanes that a host connector, expansion slot, port or plug uses.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Count,
        "units": [UNIT.NUM],
    },
    "PortSplitCount": {
        "label": "Port split count",
        "definition": "The number of separate logical ports into which one physical port can be configured, for use with breakout cables.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Count,
        "units": [UNIT.NUM],
    },
    "LinkReach": {
        "label": "Link reach",
        "definition": "The length of cable or fiber over which a port, transceiver or cable end is specified to work at its rated data rate, with the fiber grade given as an aspect where it matters.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Length,
        "units": [UNIT.M, UNIT.KiloM],
    },
    "CableLength": {
        "label": "Cable length",
        "definition": "The length of a cable assembly or fiber cable from end to end.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Length,
        "units": [UNIT.M, UNIT.CentiM, UNIT.FT],
    },
    "RackLoadCapacity": {
        "label": "Rack load capacity",
        "definition": "The largest mass of installed equipment that a rack is rated to carry, either standing in place or while being moved, as stated in the condition of the value.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Mass,
        "units": [UNIT.KiloGM, UNIT.LB],
    },
    "SupportedGPUPlatformProperty": {
        "label": "Supported GPU platform property",
        "definition": "An enumerated property naming a GPU platform that the vendor states a product not built on it is designed to serve, such as a coolant distribution unit sized for a rack-scale system.",
        "parent": S223.EnumerableProperty,
        "enumeration": "GPUPlatform",
    },
    "LaneModulationProperty": {
        "label": "Lane modulation property",
        "definition": "An enumerated property naming the modulation of the electrical or optical lanes of a data port.",
        "parent": S223.EnumerableProperty,
        "enumeration": "LaneModulation",
    },
    "OpticalPowerLevel": {
        "label": "Optical power level",
        "definition": "The optical power a transmitter launches or a receiver accepts, given as a level relative to one milliwatt.",
        "parent": S223.QuantifiableProperty,
        "quantity_kind": QK.Log10Ratio,
        "units": [UNIT["DeciB-MilliW"]],
    },
}
