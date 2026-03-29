# QNet Agent — Quantum Network Intelligence Consolidator

QNet Agent is an AI-powered research aggregator that automatically collects, analyzes, and synthesizes quantum networking content from multiple academic and industry sources. It uses OpenAI to summarize articles, extract topics, detect hot trends, and generate narrative briefings — all served through a Flask web interface.

## Features

- **Multi-source collection** — Gathers content from arXiv, Google Scholar, IEEE Xplore, company websites, and university research pages
- **AI summarization** — Generates 2–3 sentence summaries for every collected article via OpenAI
- **Topic extraction** — Automatically identifies 3–7 quantum networking topics per article
- **Hot topic scoring** — Ranks topics using a composite formula: recency (40%), frequency (35%), and cross-source diversity (25%)
- **Trend detection** — Classifies topics as rising, declining, new, or stable over a 30-day window
- **Full-text search** — Search across titles, abstracts, and authors with source/content-type filters
- **Deduplication** — Articles are deduplicated by external ID across all sources
- **Snapshot history** — Periodic timestamped snapshots of topic rankings with AI-generated analysis

## Architecture

```
Flask Web App (app.py)
        │
   QNetAgent (agent/core.py)
        │
   ┌────┼──────────────┐
   │    │              │
Collectors        Analyzer          TopicEngine
(5 sources)    (OpenAI GPT)     (scoring & trends)
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

Pre-configured sources include 7 quantum networking companies (ID Quantique, Toshiba, Qubitekk, QuTech, Aliro, PsiQuantum, Xanadu) and 15 leading research universities worldwide (MIT, Caltech, TU Delft, Bristol, USTC, and more).

## Prerequisites

- Python 3.10 or higher
- An [OpenAI API key](https://platform.openai.com/api-keys)
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

4. **Create a `.env` file** in the project root with your API keys:

   ```env
   OPENAI_API_KEY=sk-your-openai-key-here
   SECRET_KEY=your-flask-secret-key
   # Optional
   IEEE_API_KEY=your-ieee-key-here
   ```

## Configuration

All settings are loaded from environment variables with sensible defaults. See `config.py` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | OpenAI API key for summarization and topic extraction |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model used for analysis |
| `SECRET_KEY` | `qnet-dev-secret-key-change-in-prod` | Flask session secret key |
| `FLASK_DEBUG` | `1` | Enable Flask debug mode (`0` to disable) |
| `IEEE_API_KEY` | *(empty)* | IEEE Xplore API key; falls back to web scraping if absent |
| `MAX_RESULTS_PER_SOURCE` | `20` | Maximum articles fetched per source per run |
| `REQUEST_TIMEOUT` | `30` | HTTP request timeout in seconds |

## Running the Application

```bash
python app.py
```

The app starts at **http://localhost:5000** by default.

### Triggering a collection run

- **From the UI** — Click the **"Give me the last content"** button on the dashboard.
- **Programmatically** — Send a POST request:

  ```bash
  curl -X POST http://localhost:5000/api/fetch-latest
  ```

This runs all five collectors, deduplicates results, stores them in the database, and triggers AI analysis (summarization, topic extraction, hot topic scoring).

## Project Structure

```
Qnet/
├── app.py                  # Flask application, routes, and API endpoints
├── config.py               # Environment variables and default settings
├── requirements.txt        # Python dependencies
├── .env                    # API keys (create manually, not committed)
│
├── agent/
│   ├── core.py             # QNetAgent orchestrator (collect, analyze, query)
│   ├── analyzer.py         # OpenAI integration (summarize, extract, classify)
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
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Shared layout
│   ├── dashboard.html      # Main dashboard with stats and hot topics
│   ├── articles.html       # Article search and filter page
│   ├── hot_topics.html     # Topic rankings and trend analysis
│   ├── universities.html   # Research group directory
│   ├── sources.html        # Data source catalog
│   └── latest.html         # Results from the last collection run
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
| **Hot Topics** | `/hot-topics` | Ranked topics with composite scores, trend labels, and AI-generated narrative analysis |
| **Universities** | `/universities` | Directory of pre-configured research groups sorted by country |
| **Sources** | `/sources` | Catalog of all configured data sources |
| **Latest** | `/latest` | Summary and results from the most recent collection run |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/fetch-latest` | Trigger a full collection run across all sources |
| `GET` | `/api/stats` | Dashboard statistics as JSON |
| `GET` | `/api/articles` | Articles as JSON (supports query filters) |
