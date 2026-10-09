est# QNet Agent — Quantum Network Intelligence Consolidator

QNet Agent is a research aggregator that automatically collects and analyzes quantum networking content from multiple academic and industry sources. It generates extractive summaries and identifies topics locally, without requiring an external AI service or API key.

## Features

- **Multi-source collection** — Gathers content from arXiv, Google Scholar, IEEE Xplore, company websites, university research pages, and GitHub simulator repositories
- **Local summaries** — Produces concise extractive summaries from article abstracts and content
- **Topic extraction** — Matches article text against a domain-specific quantum networking vocabulary
- **Hot topic scoring** — Ranks topics using a composite formula: recency (40%), frequency (35%), and cross-source diversity (25%)
- **Trend detection** — Classifies topics as rising, declining, new, or stable over a 30-day window
- **Full-text search** — Search across titles, abstracts, and authors with source/content-type filters
- **Deduplication** — Two-layer dedup: same-source (external ID) and cross-source (normalized title matching) ensures articles appearing in multiple sources are stored only once
- **Automatic periodic fetching** — Background scheduler runs collection automatically at a configurable interval (default: every 6 hours)
- **Snapshot history** — Periodic timestamped snapshots of topic rankings with data-based reports
- **Simulator catalog** — Tracks 8 quantum network simulators (NetSquid, SeQUeNCe, QuNetSim, SimulaQron, QuISP, SimQN, Interlin-q, QNE-ADK) with live GitHub stats, code examples, install commands, and use-case scenario mapping
- **Broader research discovery** — Runs live searches for quantum computing or distributed computing content, saves deduplicated results, and catalogs active universities and companies in each area

## Architecture

```
Flask Web App (app.py)
        │
   QNetAgent (agent/core.py)
        │
   ┌────┼──────────────┐
   │    │              │
Collectors        Analyzer          TopicEngine
(6 sources)    (local analysis)  (scoring & trends)
   │    │              │
   └────┼──────────────┘
        │
   SQLite Database
   (data/qnet.db)
```

## Data Sources

| Collector | Source | Method | API Key Required |
|-----------|--------|--------|------------------|
| **arXiv** | arXiv.org | Official API | No |
| **Google Scholar** | Google Scholar | `scholarly` library | No |
| **IEEE Xplore** | IEEE Xplore | Official API (fallback: web scraping) | Optional |
| **Companies** | Industry websites | Web scraping (BeautifulSoup) | No |
| **Universities** | Research group pages | Web scraping (BeautifulSoup) | No |
| **GitHub Simulators** | GitHub repos | GitHub REST API | No (60 req/hr unauthenticated) |

Pre-configured sources include 7 quantum networking companies (ID Quantique, Toshiba, Qubitekk, QuTech, Aliro, PsiQuantum, Xanadu), 15 leading research universities worldwide (MIT, Caltech, TU Delft, Bristol, USTC, and more), and 8 quantum network simulators (NetSquid, SeQUeNCe, QuNetSim, SimulaQron, QuISP, SimQN, Interlin-q, QNE-ADK).

## Prerequisites

- Python 3.10 or higher
- *(Optional)* An [IEEE Xplore API key](https://developer.ieee.org/) for structured access to IEEE content

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Qnet
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root for optional service keys and Flask settings:

   ```env
   SECRET_KEY=your-flask-secret-key
   # Optional
   IEEE_API_KEY=your-ieee-key-here
   ```

## Configuration

All settings are loaded from environment variables with sensible defaults. See `config.py` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `qnet-dev-secret-key-change-in-prod` | Flask session secret key |
| `FLASK_DEBUG` | `1` | Enable Flask debug mode (`0` to disable) |
| `IEEE_API_KEY` | *(empty)* | IEEE Xplore API key; falls back to web scraping if absent |
| `MAX_RESULTS_PER_SOURCE` | `20` | Maximum articles fetched per source per run |
| `REQUEST_TIMEOUT` | `30` | HTTP request timeout in seconds |
| `FETCH_INTERVAL_HOURS` | `6` | How often (in hours) the background scheduler automatically fetches new articles |

## Running the Application

```bash
python app.py
```

The app starts at **http://localhost:5000** by default.

### Triggering a collection run

- **Automatic** — A background scheduler fetches new content every `FETCH_INTERVAL_HOURS` hours (default: 6). No manual action required.
- **From the UI** — Click the **"Give me the last content"** button on the dashboard.
- **Programmatically** — Send a POST request:

  ```bash
  curl -X POST http://localhost:5000/api/fetch-latest
  ```

This runs all collectors, deduplicates results, stores them in the database, and generates local summaries, keyword-based topics, and hot-topic reports.

## Distributed and Quantum Computing Research

The **Research Discovery** section includes dedicated **Quantum Computing** and **Distributed Computing** areas, plus a combined **Distributed + Quantum Computing** area for work at their intersection. The combined area searches for networked quantum processors, distributed quantum algorithms, quantum internet infrastructure, and hybrid quantum-classical systems. It includes the organizations listed in both existing computing areas, intersection-specific research groups, and a curated project directory. Open:

```text
http://localhost:5000/research-discovery?area=distributed-quantum-computing
```

The computing research areas cover topics such as:

- Distributed systems and algorithms
- Cloud and serverless computing
- Edge computing
- Consensus protocols and fault tolerance
- Peer-to-peer systems
- Distributed databases, storage, and data processing
- Large-scale networking and computing infrastructure

### Running a distributed-computing search

1. Open **Research Discovery** from the navigation bar.
2. Select **Distributed Computing** or **Distributed + Quantum Computing**.
3. Optionally enter a narrower topic, such as `Byzantine consensus`, `edge computing`, or `distributed databases`.
4. Click **Search live**.

The app searches arXiv, Google Scholar, IEEE Xplore, and curated university and company pages. Results are normalized, deduplicated, saved to SQLite, and summarized locally. A standard HTML form fallback allows the search to run even when browser JavaScript is unavailable.

Saved discovery results remain separate from the quantum-networking hot-topic rankings, so distributed-computing content does not change the specialized QNet trend scores.

### Computing research organizations and projects

The combined area includes university and company sources from both existing computing areas, along with organizations focused on networked quantum systems. Its curated project list includes the Quantum Internet Alliance full-stack prototype network, the UK Integrated Quantum Networks Hub, and QuTech Networked Quantum Computing. This is a maintained directory, not an exhaustive census of every global project.

### API example

Run and save a general distributed-computing search:

```bash
curl -X POST http://localhost:5000/api/research-discovery \
  -H "Content-Type: application/json" \
  -d '{"research_area":"distributed-computing","search_query":"distributed systems"}'
```

The `search_query` value is optional. The response includes the number of collected, matched, and newly saved articles, plus counts for each source type:

```json
{
  "success": true,
  "result": {
    "research_area": "distributed-computing",
    "search_query": "distributed systems",
    "total_collected": 138,
    "matched_articles": 127,
    "new_articles": 127,
    "source_counts": {
      "arxiv": 20,
      "scholar": 18,
      "ieee": 0,
      "company": 97,
      "university": 3
    }
  }
}
```

Counts vary between runs because external sources can change, rate-limit requests, or return no results.

## Project Structure

```
Qnet/
├── app.py                  # Flask application, routes, and API endpoints
├── config.py               # Environment variables and default settings
├── requirements.txt        # Python dependencies
├── .env                    # API keys (create manually, not committed)
├── .env.example            # Template for .env
├── .gitignore              # Git ignore rules
│
├── agent/
│   ├── core.py             # QNetAgent orchestrator (collect, analyze, query)
│   ├── analyzer.py         # Local summaries, topic extraction, and classification
│   ├── collector.py        # Base collector class
│   └── topic_engine.py     # Hot topic scoring and trend detection
│
├── collectors/
│   ├── arxiv_collector.py      # arXiv API collector
│   ├── scholar_collector.py    # Google Scholar collector
│   ├── ieee_collector.py       # IEEE Xplore collector
│   ├── company_collector.py    # Company website scraper
│   └── university_collector.py # University research page scraper
│
├── database/
│   ├── db.py               # SQLite setup, table creation, and data seeding
│   └── models.py           # SQLAlchemy ORM models
│
├── data/
│   └── qnet.db             # SQLite database (auto-created on first run)
│
├── logs/                   # Application logs (auto-created)
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Shared layout
│   ├── dashboard.html      # Main dashboard with stats and hot topics
│   ├── articles.html       # Article search and filter page
│   ├── hot_topics.html     # Topic rankings and trend analysis
│   ├── universities.html   # Research group directory
│   ├── sources.html        # Data source catalog
│   ├── simulators.html     # Quantum network simulator catalog
│   ├── latest.html         # Results from the last collection run
│   └── research_discovery.html # Quantum/distributed computing discovery
│
└── static/
    ├── css/style.css       # Stylesheet
    └── js/main.js          # Client-side logic
```

## Web UI Pages

| Page | Route | Description |
|------|-------|-------------|
| **Dashboard** | `/` | Stats cards, hot topics overview, trend indicators, recent articles |
| **Articles** | `/articles` | Full-text search across titles/abstracts/authors; filter by source or content type; paginated (50/page) |
| **Hot Topics** | `/hot-topics` | Ranked topics with composite scores, trend labels, and a data-based report |
| **Universities** | `/universities` | Directory of pre-configured research groups sorted by country |
| **Sources** | `/sources` | Catalog of all configured data sources |
| **Latest** | `/latest` | Summary and results from the most recent collection run |
| **Research Discovery** | `/research-discovery` | Live and saved quantum-computing or distributed-computing research with organization directories |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/fetch-latest` | Trigger a full collection run across all sources |
| `GET` | `/api/stats` | Dashboard statistics as JSON |
| `GET` | `/api/articles` | Articles as JSON (supports query filters) |
| `GET` | `/api/hot-topics` | Hot topics as JSON |
| `GET` | `/api/simulators` | Simulator catalog as JSON |
| `POST` | `/api/research-discovery` | Search external sources for a selected research area and save results |
