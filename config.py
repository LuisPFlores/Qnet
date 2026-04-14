import os
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "qnet.db")

# ── OpenAI ─────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ── Flask ──────────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "qnet-dev-secret-key-change-in-prod")
DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

# ── Collector defaults ─────────────────────────────────────────────────
MAX_RESULTS_PER_SOURCE = int(os.getenv("MAX_RESULTS_PER_SOURCE", "20"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# ── arXiv ──────────────────────────────────────────────────────────────
ARXIV_QUERY = 'all:"quantum network" OR all:"quantum internet" OR all:"quantum key distribution"'
ARXIV_MAX_RESULTS = MAX_RESULTS_PER_SOURCE

# ── IEEE Xplore ────────────────────────────────────────────────────────
IEEE_API_KEY = os.getenv("IEEE_API_KEY", "")

# ── Company sources (quantum networking technology providers) ──────────
COMPANY_SOURCES = [
    {
        "name": "ID Quantique",
        "url": "https://www.idquantique.com/resource-centre/news/",
        "description": "Swiss quantum-safe security company, QKD systems",
    },
    {
        "name": "Toshiba Quantum Technology",
        "url": "https://www.toshiba.eu/quantum/news/",
        "description": "QKD systems and quantum networking research",
    },
    {
        "name": "Qubitekk",
        "url": "https://qubitekk.com/news/",
        "description": "Quantum networking hardware and entanglement sources",
    },
    {
        "name": "QuTech",
        "url": "https://qutech.nl/newsroom/",
        "description": "Quantum internet research and development",
    },
    {
        "name": "Aliro Quantum",
        "url": "https://www.aliroquantum.com/blog",
        "description": "Quantum network simulation and orchestration software",
    },
    {
        "name": "PsiQuantum",
        "url": "https://www.psiquantum.com/news",
        "description": "Photonic quantum computing and networking",
    },
    {
        "name": "Xanadu",
        "url": "https://xanadu.ai/blog",
        "description": "Photonic quantum computing, PennyLane framework",
    },
]

# ── University research groups (quantum networking) ───────────────────
UNIVERSITY_SOURCES = [
    {
        "name": "MIT – QPAI (Quantum Photonics & AI)",
        "country": "USA",
        "url": "https://qp.mit.edu",
        "department": "Research Laboratory of Electronics / EECS",
        "key_researchers": "Dirk Englund",
        "focus_areas": "Quantum repeaters, entanglement distribution, quantum photonics",
    },
    {
        "name": "University of Chicago – Quantum Communication",
        "country": "USA",
        "url": "https://quantum.uchicago.edu/research-areas/quantum-communication",
        "department": "Chicago Quantum Institute / Pritzker School of Molecular Engineering",
        "key_researchers": "David Awschalom, Hannes Bernien, Tian Zhong",
        "focus_areas": "Quantum internet testbeds, quantum memory, quantum networking",
    },
    {
        "name": "Caltech – Quantum Networks",
        "country": "USA",
        "url": "https://iqim.caltech.edu/",
        "department": "IQIM",
        "key_researchers": "Jeff Kimble, Manuel Endres",
        "focus_areas": "Quantum optics, quantum information",
    },
    {
        "name": "Harvard – Quantum Networks",
        "country": "USA",
        "url": "https://lukin.physics.harvard.edu/",
        "department": "Physics",
        "key_researchers": "Mikhail Lukin",
        "focus_areas": "Quantum repeaters, diamond NV centers",
    },
    {
        "name": "TU Delft – QuTech",
        "country": "Netherlands",
        "url": "https://qutech.nl/research/quantum-internet/",
        "department": "QuTech",
        "key_researchers": "Stephanie Wehner, Ronald Hanson",
        "focus_areas": "Quantum internet, network protocols, NV-center entanglement",
    },
    {
        "name": "University of Bristol – Quantum Engineering",
        "country": "UK",
        "url": "https://www.bristol.ac.uk/quantum-engineering/",
        "department": "Quantum Engineering Technology Labs",
        "key_researchers": "John Rarity, Anthony Sherfield",
        "focus_areas": "Photonic quantum networks, integrated photonics",
    },
    {
        "name": "TU Munich – Quantum Networks",
        "country": "Germany",
        "url": "https://www.mpe.mpg.de/quantum-networks",
        "department": "Max Planck Institute / TUM",
        "key_researchers": "Harald Weinfurter, Gerhard Rempe",
        "focus_areas": "Photonic quantum links, atom-photon entanglement",
    },
    {
        "name": "USTC – Quantum Information",
        "country": "China",
        "url": "https://quantum.ustc.edu.cn/web/en",
        "department": "CAS Center for Excellence in Quantum Information",
        "key_researchers": "Jian-Wei Pan, Chao-Yang Lu",
        "focus_areas": "Satellite QKD, quantum repeaters, Micius satellite",
    },
    {
        "name": "Tsinghua University – Center for Quantum Information",
        "country": "China",
        "url": "https://iiis.tsinghua.edu.cn/en/CQI/Introduction.htm",
        "department": "IIIS – Center for Quantum Information",
        "key_researchers": "Luming Duan",
        "focus_areas": "Quantum communication, quantum computing, ion trap quantum simulation",
    },
    {
        "name": "University of Tokyo – Quantum Networks",
        "country": "Japan",
        "url": "https://www.qi.t.u-tokyo.ac.jp/",
        "department": "Quantum Information Science",
        "key_researchers": "Akira Furusawa",
        "focus_areas": "Continuous-variable quantum teleportation, optical networks",
    },
    {
        "name": "National University of Singapore – CQT",
        "country": "Singapore",
        "url": "https://www.quantumlah.org/",
        "department": "Centre for Quantum Technologies",
        "key_researchers": "Alexander Ling, Valerio Scarani",
        "focus_areas": "Satellite QKD, quantum networking protocols",
    },
    {
        "name": "University of Waterloo – IQC",
        "country": "Canada",
        "url": "https://uwaterloo.ca/institute-for-quantum-computing/",
        "department": "Institute for Quantum Computing",
        "key_researchers": "Thomas Jennewein, Norbert Lutkenhaus",
        "focus_areas": "QKD, quantum networking, quantum repeaters",
    },
    {
        "name": "University of Innsbruck – Distributed Quantum Systems",
        "country": "Austria",
        "url": "https://www.uibk.ac.at/en/exphys/research/dqs/",
        "department": "Institute for Experimental Physics",
        "key_researchers": "Rainer Blatt, Ben Lanyon",
        "focus_areas": "Ion trap networks, long-distance entanglement, distributed quantum sensing",
    },
    {
        "name": "Sorbonne Université – LIP6 Quantum",
        "country": "France",
        "url": "https://www.lip6.fr/recherche/team.php?acronyme=QI",
        "department": "LIP6 – Quantum Information",
        "key_researchers": "Eleni Diamanti",
        "focus_areas": "QKD, quantum networking protocols, quantum cryptography",
    },
    {
        "name": "University of Science and Technology – KIST",
        "country": "South Korea",
        "url": "https://www.kist.re.kr/eng/main/main.do",
        "department": "Center for Quantum Information",
        "key_researchers": "Sang-Wook Han",
        "focus_areas": "QKD networks, quantum communication infrastructure",
    },
]

# ── Search terms for collectors ────────────────────────────────────────
QUANTUM_NETWORK_KEYWORDS = [
    "quantum network",
    "quantum internet",
    "quantum key distribution",
    "QKD",
    "quantum repeater",
    "entanglement distribution",
    "quantum communication",
    "quantum teleportation",
    "quantum memory",
    "quantum routing",
    "quantum network simulator",
]

# ── Quantum network simulators ────────────────────────────────────────
SIMULATOR_SOURCES = [
    {
        "name": "NetSquid",
        "description": "Discrete-event quantum network simulator developed by QuTech (TU Delft + TNO). Models physical-layer quantum processes including decoherence, gate errors, and channel noise with high fidelity using ket vectors, stabiliser states, and density matrices.",
        "github_url": "",  # closed-source core
        "docs_url": "https://netsquid.org/",
        "language": "Python 3 (C/Cython backend)",
        "dependencies": "Requires free registration at forum.netsquid.org",
        "install_command": "pip3 install --extra-index-url https://pypi.netsquid.org netsquid",
        "license": "Proprietary (free for non-commercial use)",
        "status": "active",
        "scenarios": "Physical-layer simulation, Decoherence modeling, Quantum repeater design, Modular quantum computing, Quantum internet protocols",
        "paper_reference": "Coopmans et al., 'NetSquid, a discrete-event simulation platform for quantum networks', Commun Phys 4, 164 (2021). DOI: 10.1038/s42005-021-00647-8",
        "example_code": """import netsquid as ns
from netsquid.components import QuantumChannel

class PingPongProtocol(ns.protocols.NodeProtocol):
    def run(self):
        port = self.node.ports['qubitIO']
        while True:
            yield self.await_port_input(port)
            qubit = port.rx_input().items[0]
            observable = ns.X if self.node.name == 'Bob' else ns.Z
            outcome, _ = ns.qubits.measure(qubit, observable)
            print(f'{ns.sim_time()}: {self.node.name} measured '
                  f'{outcome} in {observable.name} basis')
            port.tx_output(qubit)

network = ns.nodes.Network('PingPongNetwork', nodes=['Alice', 'Bob'])
network.add_connection('Alice', 'Bob',
    channel_to=QuantumChannel('A2B', delay=10),
    channel_from=QuantumChannel('B2A', delay=10),
    port_name_node1='qubitIO', port_name_node2='qubitIO')
proto_a = PingPongProtocol(network.nodes['Alice']).start()
proto_b = PingPongProtocol(network.nodes['Bob']).start()
qubit = ns.qubits.qubitapi.create_qubits(1)
network.nodes['Alice'].ports['qubitIO'].tx_output(qubit)
ns.sim_run(duration=50)""",
    },
    {
        "name": "SeQUeNCe",
        "description": "Customizable discrete-event simulator for quantum networks with five modular layers: Hardware, Entanglement Management, Resource Management, Network Management, and Application. Actively maintained with Jupyter notebook demos.",
        "github_url": "https://github.com/sequence-toolbox/SeQUeNCe",
        "docs_url": "https://sequence-toolbox.github.io/SeQUeNCe/",
        "language": "Python 3.11+",
        "dependencies": "QuTiP, NumPy, pip or uv",
        "install_command": "pip install sequence",
        "license": "Open Source",
        "status": "active",
        "scenarios": "Full-stack quantum networking, Entanglement management, Quantum memory modeling, Network topology design, Resource allocation",
        "paper_reference": "Wu et al., 'SeQUeNCe: a customizable discrete-event simulator of quantum networks', Quantum Science and Technology, 2021. DOI: 10.1088/2058-9565/ac22f6",
        "example_code": """from sequence.kernel.timeline import Timeline
from sequence.topology.node import QuantumRouter
from sequence.topology.topology import Topology

# Create a simulation timeline (10 seconds, picosecond resolution)
tl = Timeline(10e12)

# Build a simple linear network: Alice -- Router -- Bob
topo = Topology("simple_network", tl)
topo.add_node("alice", QuantumRouter)
topo.add_node("router", QuantumRouter)
topo.add_node("bob", QuantumRouter)
topo.add_quantum_channel("alice", "router", distance=1e3)
topo.add_quantum_channel("router", "bob", distance=1e3)
topo.add_classical_channel("alice", "router", distance=1e3)
topo.add_classical_channel("router", "bob", distance=1e3)

# Initialize and run the simulation
tl.init()
tl.run()
print("Simulation complete")""",
    },
    {
        "name": "QuNetSim",
        "description": "Python framework for simulating quantum networks at the protocol level. Designed for testing quantum communication protocols like teleportation, superdense coding, and QKD under various network conditions. Supported by the Unitary Fund.",
        "github_url": "https://github.com/tqsd/QuNetSim",
        "docs_url": "https://tqsd.github.io/QuNetSim/",
        "language": "Python 3",
        "dependencies": "NumPy, see requirements.txt",
        "install_command": "pip install qunetsim",
        "license": "MIT",
        "status": "stalled",
        "scenarios": "QKD protocols, Quantum teleportation, Superdense coding, EPR pair distribution, Protocol testing",
        "paper_reference": "DiAdamo et al., 'QuNetSim: A Software Framework for Quantum Networks', IEEE Transactions on Quantum Engineering, 2021. DOI: 10.1109/TQE.2021.3092395",
        "example_code": """from qunetsim.components import Host, Network

network = Network.get_instance()
network.start()

alice = Host('Alice')
bob = Host('Bob')

alice.add_connection(bob.host_id)
bob.add_connection(alice.host_id)

alice.start()
bob.start()

network.add_hosts([alice, bob])

# Generate and share an EPR pair
alice.send_epr(bob.host_id, await_ack=True)
q_alice = alice.get_epr(bob.host_id)
q_bob = bob.get_epr(alice.host_id)

print("EPR is in state: %d, %d" % (q_alice.measure(), q_bob.measure()))
network.stop(True)""",
    },
    {
        "name": "SimulaQron",
        "description": "Application-level quantum network simulator from QuTech. Simulates quantum network nodes for developing quantum internet applications. Since v4.0, serves as a backend for NetQASM (the quantum network assembly language).",
        "github_url": "https://github.com/SoftwareQuTech/SimulaQron",
        "docs_url": "https://softwarequtech.github.io/SimulaQron/html/index.html",
        "language": "Python 3",
        "dependencies": "Twisted, NumPy, Cython, NetQASM (v4.0+)",
        "install_command": "pip3 install simulaqron",
        "license": "BSD 3-Clause",
        "status": "stalled",
        "scenarios": "Quantum internet applications, QKD protocol development, NetQASM backend, Quantum network programming",
        "paper_reference": "Dahlberg et al., 'SimulaQron -- A simulator for developing quantum internet software', Quantum Science and Technology, 2018.",
        "example_code": """# Start SimulaQron nodes (in terminal)
# simulaqron set max-qubits 20
# simulaqron start --nodes Alice,Bob

# Then run a NetQASM application:
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection

def alice_main():
    with NetQASMConnection("Alice") as alice:
        epr_socket = EPRSocket("Bob")
        alice.context.connect(epr_socket)
        q = epr_socket.create_keep()[0]
        m = q.measure()
        print(f"Alice measured: {m}")

# Run: netqasm simulate --app-dir=./app""",
    },
    {
        "name": "QuISP",
        "description": "Quantum Internet Simulation Package built on OMNeT++ for simulating large-scale quantum repeater networks. Supports up to 100 networks of 100 nodes each. Uses error-basis tracking (not full density matrices) for scalability. Has a WebAssembly version for browser-based simulation.",
        "github_url": "https://github.com/sfc-aqua/quisp",
        "docs_url": "https://aqua.sfc.wide.ad.jp/quisp-online/master/",
        "language": "C++ 65%, OMNeT++ NED 27%, Python 5%",
        "dependencies": "OMNeT++ 6.0+, Eigen, GoogleTest, nlohmann/json, spdlog. Docker available.",
        "install_command": "git clone https://github.com/sfc-aqua/quisp && cd quisp && make",
        "license": "BSD 3-Clause",
        "status": "active",
        "scenarios": "Large-scale repeater networks, Entanglement swapping, Purification protocols, Link architectures (MM/MIM/MSM), Congestion analysis",
        "paper_reference": "AQUA research group, Keio University (Prof. Rodney Van Meter). See GitHub repo for publications.",
        "example_code": """// QuISP uses OMNeT++ NED files for network topology definition
// Example: simple 3-node repeater chain (networks/topology.ned)

network Linear_3node extends QuantumNetwork {
    submodules:
        endnode[2]: QNode {
            address = index;
            node_type = "EndNode";
        }
        repeater: QNode {
            address = 2;
            node_type = "Repeater";
        }
    connections:
        endnode[0].port++ <--> QuantumChannel <--> repeater.port++;
        repeater.port++ <--> QuantumChannel <--> endnode[1].port++;
}

// Run from command line:
// ./quisp -u Cmdenv -c Linear_3node -n networks
// Or use the browser version at https://aqua.sfc.wide.ad.jp/quisp-online/""",
    },
    {
        "name": "SimQN",
        "description": "Network-layer quantum network simulator from USTC. Focuses on QKD network simulation with BB84 protocol, CASCADE error correction, and privacy amplification. Supports multiple routing algorithms (Dijkstra, Q-CAST, REPS) and both quantum-state and fidelity-based entanglement models.",
        "github_url": "https://github.com/QNLab-USTC/SimQN",
        "docs_url": "https://ertuil.github.io/SimQN/",
        "language": "Python 3 (Cython for performance)",
        "dependencies": "NumPy, Cython",
        "install_command": "pip3 install -U qns",
        "license": "GPL-3.0",
        "status": "active",
        "scenarios": "QKD networks (BB84), Entanglement routing, Network topology generation, Resource allocation, Dijkstra/Q-CAST routing",
        "paper_reference": "Chen et al., 'SimQN: A network-layer simulator for the quantum network investigation', IEEE Network, 2023. DOI: 10.1109/MNET.130.2200481",
        "example_code": """from qns.simulator.simulator import Simulator
from qns.network.topology import RandomTopology
from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp
from qns.network import QuantumNetwork
from qns.network.route.dijkstra import DijkstraRouteAlgorithm
from qns.network.topology.topo import ClassicTopology
import qns.utils.log as log
import logging

init_fidelity = 0.99
nodes_number = 150
lines_number = 450
qchannel_delay = 0.05
cchannel_delay = 0.05
memory_capacity = 50
send_rate = 10

s = Simulator(0, 10, accuracy=1000000)
log.logger.setLevel(logging.INFO)
log.install(s)

topo = RandomTopology(
    nodes_number=nodes_number,
    lines_number=lines_number,
    qchannel_args={"delay": qchannel_delay},
    cchannel_args={"delay": cchannel_delay},
    memory_args=[{"capacity": memory_capacity}],
    nodes_apps=[EntanglementDistributionApp(init_fidelity=init_fidelity)]
)

net = QuantumNetwork(
    topo=topo,
    classic_topo=ClassicTopology.All,
    route=DijkstraRouteAlgorithm()
)
net.build_route()
net.random_requests(10, attr={"send_rate": send_rate})
net.install(s)
s.run()""",
    },
    {
        "name": "Interlin-q",
        "description": "Distributed quantum computing simulator that extends QuNetSim. Uses a master-slave centralized-control architecture to map monolithic quantum circuits onto distributed computing hosts connected via a quantum network.",
        "github_url": "https://github.com/Interlin-q/Interlin-q",
        "docs_url": "https://github.com/Interlin-q/Interlin-q",
        "language": "Python 3",
        "dependencies": "QuNetSim, NumPy, CircuitParser",
        "install_command": "git clone https://github.com/Interlin-q/Interlin-q && pip install -r requirements.txt",
        "license": "MIT",
        "status": "stalled",
        "scenarios": "Distributed quantum computing, Circuit distribution, Multi-node quantum algorithms, Quantum Phase Estimation",
        "paper_reference": "Parekh et al., 'Quantum Algorithms and Simulation for Parallel and Distributed Quantum Computing', arXiv:2106.06841, 2021.",
        "example_code": """from interlinq import ControllerHost, Clock, Circuit
from qunetsim.components import Host, Network

def controller_host_protocol(host, q_map):
    # Create a distributed CNOT between two computing hosts
    circuit = Circuit(q_map, gate_list=[
        {"gate": "H", "target": {"host_id": "host_1", "qubit_id": 0}},
        {"gate": "CNOT",
         "control": {"host_id": "host_1", "qubit_id": 0},
         "target":  {"host_id": "host_2", "qubit_id": 0}},
        {"gate": "MEASURE", "target": {"host_id": "host_1", "qubit_id": 0}},
        {"gate": "MEASURE", "target": {"host_id": "host_2", "qubit_id": 0}},
    ])
    host.run_circuit(circuit)
    results = host.get_results()
    print(f"Distributed CNOT results: {results}")

network = Network.get_instance()
network.start()
clock = Clock()
controller = ControllerHost("controller", clock=clock)
hosts, q_map = controller.create_distributed_network(
    num_computing_hosts=2, num_qubits_per_host=2)
controller.start()
network.add_host(controller)
for h in hosts:
    network.add_host(h)
controller.run_protocol(controller_host_protocol, (q_map,))
network.stop(True)""",
    },
    {
        "name": "QNE-ADK",
        "description": "Quantum Network Explorer Application Development Kit from QuTech. Provides a CLI and SDK for building quantum network applications that can run on the Quantum Network Explorer platform, using NetQASM as the programming interface and NetSquid/SquidASM as the simulation backend.",
        "github_url": "https://github.com/QuTech-Delft/qne-adk",
        "docs_url": "https://www.quantum-network.com/",
        "language": "Python 3.8+",
        "dependencies": "NetQASM, SquidASM (requires NetSquid credentials)",
        "install_command": "pip install qne-adk",
        "license": "MIT",
        "status": "active",
        "scenarios": "Quantum network application development, QKD applications, Teleportation protocols, Quantum Network Explorer platform",
        "paper_reference": "QuTech Delft. See https://www.quantum-network.com/ for platform documentation.",
        "example_code": """# QNE-ADK uses a CLI workflow to create and run experiments

# Step 1: Create a new application with two roles
# $ qne application create my_qkd_app Alice Bob

# Step 2: Edit the application logic (app_alice.py)
from netqasm.sdk import EPRSocket
from netqasm.sdk.external import NetQASMConnection

def main(app_config=None):
    with NetQASMConnection("Alice") as alice:
        epr_socket = EPRSocket("Bob")
        alice.context.connect(epr_socket)
        # Create EPR pair and measure
        q = epr_socket.create_keep()[0]
        result = q.measure()
        return {"measurement": int(result)}

# Step 3: Create and run an experiment
# $ qne experiment create my_experiment my_qkd_app europe
# $ qne experiment run --block --timeout=30 my_experiment
# $ qne experiment results my_experiment""",
    },
]

# ── Quantum networking scenarios ──────────────────────────────────────
QUANTUM_SCENARIOS = [
    {
        "name": "QKD Networks",
        "description": "Simulating quantum key distribution protocols (BB84, E91, BBM92) across network topologies to evaluate secret key rates, error thresholds, and eavesdropper detection under realistic channel conditions.",
        "simulators": ["SimQN", "QuNetSim", "NetSquid", "QNE-ADK"],
    },
    {
        "name": "Entanglement Distribution",
        "description": "Modeling the generation, swapping, and purification of entangled pairs over long distances. Critical for understanding fidelity degradation and optimizing entanglement protocols across multi-hop networks.",
        "simulators": ["NetSquid", "SeQUeNCe", "SimQN", "QuISP"],
    },
    {
        "name": "Quantum Repeater Chains",
        "description": "Testing repeater architectures from first-generation (purify-and-swap) through third-generation (QEC-based). Evaluates trade-offs between repeater spacing, memory coherence times, and end-to-end fidelity.",
        "simulators": ["QuISP", "NetSquid", "SeQUeNCe"],
    },
    {
        "name": "Quantum Internet Protocols",
        "description": "Designing and validating link-layer, network-layer, and transport-layer protocols for a future quantum internet. Includes routing, resource management, and scheduling of quantum operations across nodes.",
        "simulators": ["NetSquid", "SeQUeNCe", "SimulaQron", "QNE-ADK"],
    },
    {
        "name": "Distributed Quantum Computing",
        "description": "Simulating multi-node quantum computation where entanglement links enable non-local gate operations. Maps monolithic quantum circuits onto physically separated processors connected via a quantum network.",
        "simulators": ["Interlin-q", "NetSquid", "SimulaQron"],
    },
    {
        "name": "Satellite QKD",
        "description": "Modeling free-space quantum communication links between ground stations and satellites. Evaluates atmospheric losses, timing synchronization, and orbital dynamics for space-based quantum key distribution.",
        "simulators": ["NetSquid", "SimQN"],
    },
    {
        "name": "Quantum Sensor Networks",
        "description": "Networked quantum sensors that exploit entanglement for enhanced measurement precision beyond the standard quantum limit. Applications include clock synchronization, distributed sensing, and geodesy.",
        "simulators": ["NetSquid", "SeQUeNCe"],
    },
    {
        "name": "Hybrid Classical-Quantum Networks",
        "description": "Integration of quantum channels with existing classical network infrastructure. Evaluates coexistence of quantum and classical signals on shared fiber, wavelength management, and cross-layer protocol design.",
        "simulators": ["QuISP", "SeQUeNCe", "SimQN"],
    },
]
