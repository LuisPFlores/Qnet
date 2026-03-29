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
        "name": "MIT – Quantum Networks Center",
        "country": "USA",
        "url": "https://www.rle.mit.edu/qnc/",
        "department": "Research Laboratory of Electronics",
        "key_researchers": "Dirk Englund, Saikat Guha",
        "focus_areas": "Quantum repeaters, entanglement distribution",
    },
    {
        "name": "University of Chicago – Quantum Networks",
        "country": "USA",
        "url": "https://pme.uchicago.edu/quantum-networks",
        "department": "Pritzker School of Molecular Engineering",
        "key_researchers": "David Awschalom, Hannes Bernien",
        "focus_areas": "Quantum internet testbeds, quantum memory",
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
        "name": "Tsinghua University – Quantum Info Center",
        "country": "China",
        "url": "https://iiis.tsinghua.edu.cn/en/quantum/",
        "department": "IIIS",
        "key_researchers": "Luming Duan",
        "focus_areas": "Quantum communication, quantum computing",
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
        "name": "University of Innsbruck – Quantum Optics",
        "country": "Austria",
        "url": "https://www.uibk.ac.at/exphys/quantum/",
        "department": "Institute for Experimental Physics",
        "key_researchers": "Rainer Blatt, Ben Lanyon",
        "focus_areas": "Ion trap networks, long-distance entanglement",
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
]
