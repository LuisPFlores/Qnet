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
├── .env.example            # Template for .env
├── .gitignore              # Git ignore rules
│
├── run_server.py           # Production entry point (Waitress WSGI, used by IIS)
├── web.config              # IIS HttpPlatformHandler configuration
├── deploy_iis.ps1          # Automated IIS deployment script (PowerShell)
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
├── logs/                   # Application and IIS logs (auto-created)
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
| `GET` | `/api/hot-topics` | Hot topics as JSON |

---

## Deploying to IIS on Windows Server

### Architecture overview

```
Client Browser
      |
      v
   IIS (port 80 / 443)
      |  HttpPlatformHandler
      v
   Waitress WSGI Server (run_server.py)
      |  (127.0.0.1:%HTTP_PLATFORM_PORT%)
      v
   Flask App (app.py)
      |
      v
   SQLite (data/qnet.db)
```

IIS acts as a reverse proxy via **HttpPlatformHandler**. It spawns `run_server.py`, which starts the **Waitress** production WSGI server on a dynamic port injected through the `%HTTP_PLATFORM_PORT%` environment variable. IIS forwards all inbound HTTP traffic to that port.

### Deployment files

| File | Purpose |
|------|---------|
| `run_server.py` | Production entry point -- starts Waitress on the IIS-assigned port, logs to `logs/` |
| `web.config` | IIS configuration -- HttpPlatformHandler directives, security headers, request limits |
| `deploy_iis.ps1` | Automated PowerShell deployment script (runs all 9 steps below) |

### Prerequisites

- **Windows Server** 2019 or 2022
- **Python 3.11+** installed system-wide (`C:\Python311\python.exe` or similar). During installation, check "Install for all users" and "Add Python to PATH".
- **Administrator access** to the server
- An **OpenAI API key**

---

### Option A: Automated deployment (recommended)

1. **Install Python 3.11+** on the server from https://www.python.org/downloads/

2. **Copy the application** to the server (git clone, zip, file share -- any method):

   ```powershell
   git clone <repository-url> C:\temp\Qnet
   ```

3. **Open an elevated PowerShell** (right-click > "Run as administrator") and run:

   ```powershell
   cd C:\temp\Qnet
   .\deploy_iis.ps1
   ```

   Or with custom parameters:

   ```powershell
   .\deploy_iis.ps1 -SiteName "QNetAgent" `
                     -Port 8080 `
                     -HostHeader "qnet.yourdomain.com" `
                     -PhysicalPath "C:\inetpub\QNetAgent" `
                     -PythonPath "C:\Python311\python.exe"
   ```

   The script performs these steps automatically:

   | Step | What it does |
   |------|-------------|
   | 1 | Verifies Python is installed at the specified path |
   | 2 | Enables IIS Windows features (WebServer, StaticContent, RequestFiltering, etc.) |
   | 3 | Downloads and installs HttpPlatformHandler v1.2 if not present |
   | 4 | Copies application files to the target directory (default `C:\inetpub\QNetAgent`) |
   | 5 | Creates a Python virtual environment and installs all pip dependencies |
   | 6 | Creates `.env` from `.env.example` and sets `FLASK_DEBUG=0` for production |
   | 7 | Rewrites `web.config` paths to match the server's physical path |
   | 8 | Creates an IIS Application Pool ("No Managed Code", AlwaysRunning, no idle timeout) and Website |
   | 9 | Grants Modify permissions to `IIS_IUSRS` and the AppPool identity, then starts the site |

4. **Edit the `.env` file** with your actual API keys:

   ```powershell
   notepad C:\inetpub\QNetAgent\.env
   ```

   Set at minimum:
   ```env
   OPENAI_API_KEY=sk-your-actual-key
   SECRET_KEY=a-long-random-string-for-production
   FLASK_DEBUG=0
   ```

5. **Open the Windows Firewall** for the chosen port (if not port 80, which is usually already open):

   ```powershell
   New-NetFirewallRule -DisplayName "QNet Agent HTTP" `
                       -Direction Inbound `
                       -Port 80 `
                       -Protocol TCP `
                       -Action Allow
   ```

6. **Verify** by browsing to `http://localhost` (or `http://your-server-ip:port`).

---

### Option B: Manual step-by-step deployment

#### Step 1 -- Install IIS features

Open an elevated PowerShell and run:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName `
    IIS-WebServerRole, `
    IIS-WebServer, `
    IIS-CommonHttpFeatures, `
    IIS-StaticContent, `
    IIS-DefaultDocument, `
    IIS-HttpErrors, `
    IIS-HttpLogging, `
    IIS-RequestFiltering, `
    IIS-ISAPIExtensions, `
    IIS-ISAPIFilter, `
    IIS-ManagementConsole `
    -NoRestart
```

#### Step 2 -- Install HttpPlatformHandler

Download the HttpPlatformHandler installer from:
https://www.iis.net/downloads/microsoft/httpplatformhandler

Or install via command line:

```powershell
$url = "https://download.microsoft.com/download/5/0/2/502F8E94-3222-4D58-A1A4-41ADE3EC22F3/httpPlatformHandler_amd64.msi"
Invoke-WebRequest -Uri $url -OutFile "$env:TEMP\httpPlatformHandler.msi"
Start-Process msiexec.exe -ArgumentList "/i `"$env:TEMP\httpPlatformHandler.msi`" /quiet /norestart" -Wait
```

Verify it installed:

```powershell
Test-Path "$env:SystemRoot\System32\inetsrv\httpPlatformHandler.dll"
# Should return True
```

#### Step 3 -- Copy application files

```powershell
$appPath = "C:\inetpub\QNetAgent"
mkdir $appPath -Force
Copy-Item -Path "C:\temp\Qnet\*" -Destination $appPath -Recurse -Force
mkdir "$appPath\data" -Force
mkdir "$appPath\logs" -Force
```

#### Step 4 -- Create Python virtual environment and install dependencies

```powershell
cd C:\inetpub\QNetAgent
C:\Python311\python.exe -m venv venv
.\venv\Scripts\pip.exe install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt
```

#### Step 5 -- Configure environment variables

```powershell
Copy-Item .env.example .env
notepad .env
```

Set these values in `.env`:

```env
OPENAI_API_KEY=sk-your-actual-key
OPENAI_MODEL=gpt-4o-mini
SECRET_KEY=a-long-random-string-for-production
FLASK_DEBUG=0
MAX_RESULTS_PER_SOURCE=20
REQUEST_TIMEOUT=30
```

#### Step 6 -- Update web.config paths

Replace every occurrence of `%HOME%` in `web.config` with the actual application path:

```powershell
$webConfig = Get-Content "$appPath\web.config" -Raw
$webConfig = $webConfig -replace '%HOME%', $appPath
Set-Content -Path "$appPath\web.config" -Value $webConfig -NoNewline
```

After replacement, the key section should look like:

```xml
<httpPlatform processPath="C:\inetpub\QNetAgent\venv\Scripts\python.exe"
              arguments="C:\inetpub\QNetAgent\run_server.py"
              stdoutLogEnabled="true"
              stdoutLogFile="C:\inetpub\QNetAgent\logs\iis-stdout.log"
              startupTimeLimit="120"
              requestTimeout="00:05:00"
              processesPerApplication="1">
```

#### Step 7 -- Create the IIS Application Pool

```powershell
Import-Module WebAdministration

# Create pool
New-WebAppPool -Name "QNetAgentPool"

# Configure: No Managed Code, Always Running, No Idle Timeout
Set-ItemProperty "IIS:\AppPools\QNetAgentPool" -Name "managedRuntimeVersion" -Value ""
Set-ItemProperty "IIS:\AppPools\QNetAgentPool" -Name "startMode" -Value "AlwaysRunning"
Set-ItemProperty "IIS:\AppPools\QNetAgentPool" -Name "processModel.idleTimeout" -Value ([TimeSpan]::FromMinutes(0))
Set-ItemProperty "IIS:\AppPools\QNetAgentPool" -Name "processModel.loadUserProfile" -Value $true
```

Key settings explained:

| Setting | Value | Why |
|---------|-------|-----|
| `managedRuntimeVersion` | `""` (empty) | Python is not a .NET runtime -- must be "No Managed Code" |
| `startMode` | `AlwaysRunning` | Keeps the Waitress process alive without waiting for the first request |
| `idleTimeout` | `0` | Prevents IIS from killing the process after inactivity |
| `loadUserProfile` | `true` | Required for the process to read environment variables and user-level paths |

#### Step 8 -- Create the IIS Website

```powershell
# Stop Default Web Site if using port 80
Stop-Website -Name "Default Web Site" -ErrorAction SilentlyContinue

# Create the QNet site
New-Website -Name "QNetAgent" `
            -PhysicalPath "C:\inetpub\QNetAgent" `
            -ApplicationPool "QNetAgentPool" `
            -Port 80 `
            -Force
```

To use a hostname binding instead:

```powershell
New-Website -Name "QNetAgent" `
            -PhysicalPath "C:\inetpub\QNetAgent" `
            -ApplicationPool "QNetAgentPool" `
            -Port 80 `
            -HostHeader "qnet.yourdomain.com" `
            -Force
```

#### Step 9 -- Set file permissions

The IIS worker process needs read/write access to the application directory (for SQLite, logs, etc.):

```powershell
icacls "C:\inetpub\QNetAgent" /grant "IIS_IUSRS:(OI)(CI)M" /T
icacls "C:\inetpub\QNetAgent" /grant "IIS AppPool\QNetAgentPool:(OI)(CI)M" /T
```

#### Step 10 -- Start the site and verify

```powershell
Start-Website -Name "QNetAgent"

# Open in browser
Start-Process http://localhost
```

---

### Adding HTTPS (optional but recommended)

To secure the site with SSL:

1. **Obtain an SSL certificate** (e.g., from Let's Encrypt, your organization's CA, or a commercial provider).

2. **Import the certificate** into the Windows Certificate Store:

   ```powershell
   Import-PfxCertificate -FilePath "C:\certs\qnet.pfx" `
                          -CertStoreLocation "Cert:\LocalMachine\My" `
                          -Password (ConvertTo-SecureString -String "pfx-password" -AsPlainText -Force)
   ```

3. **Add an HTTPS binding** to the site:

   ```powershell
   $cert = Get-ChildItem -Path "Cert:\LocalMachine\My" | Where-Object { $_.Subject -like "*qnet*" }

   New-WebBinding -Name "QNetAgent" -Protocol "https" -Port 443 -HostHeader "qnet.yourdomain.com"

   $binding = Get-WebBinding -Name "QNetAgent" -Protocol "https"
   $binding.AddSslCertificate($cert.Thumbprint, "My")
   ```

4. **(Optional) Redirect HTTP to HTTPS** by adding a URL Rewrite rule in `web.config`:

   ```xml
   <rewrite>
     <rules>
       <rule name="HTTP to HTTPS" stopProcessing="true">
         <match url="(.*)" />
         <conditions>
           <add input="{HTTPS}" pattern="off" />
         </conditions>
         <action type="Redirect" url="https://{HTTP_HOST}/{R:1}" redirectType="Permanent" />
       </rule>
     </rules>
   </rewrite>
   ```

---

### Troubleshooting

| Symptom | What to check |
|---------|---------------|
| **HTTP 500 Internal Server Error** | Check `C:\inetpub\QNetAgent\logs\iis-stdout.log` and `qnet_iis.log` for Python tracebacks |
| **HTTP 502.3 Bad Gateway** | Waitress failed to start -- verify `venv\Scripts\python.exe` exists and `run_server.py` runs manually: `.\venv\Scripts\python.exe run_server.py` |
| **Site won't start in IIS** | Confirm the Application Pool is set to "No Managed Code" (`managedRuntimeVersion = ""`) |
| **Timeout on "Give me the last content"** | The `/api/fetch-latest` call can take 2+ minutes. The `requestTimeout` in `web.config` is set to 5 minutes. If IIS still times out, increase this value. |
| **Permission denied on SQLite** | Ensure `IIS AppPool\QNetAgentPool` has Modify rights on the `data\` directory: `icacls "C:\inetpub\QNetAgent\data" /grant "IIS AppPool\QNetAgentPool:(OI)(CI)M"` |
| **HttpPlatformHandler not found** | Reinstall from https://www.iis.net/downloads/microsoft/httpplatformhandler then run `iisreset` |
| **Python not found by IIS** | The `processPath` in `web.config` must be an absolute path to `venv\Scripts\python.exe`. Run `where python` to find the correct path. |
| **OpenAI calls fail** | Verify the `.env` file exists in the app root and contains a valid `OPENAI_API_KEY`. The IIS worker process must be able to read this file. |
| **Changes to .env not taking effect** | Recycle the Application Pool after editing `.env`: `Restart-WebAppPool -Name "QNetAgentPool"` |

### Useful IIS management commands

```powershell
# Restart the application pool (reloads the Python process)
Restart-WebAppPool -Name "QNetAgentPool"

# Stop / start the site
Stop-Website -Name "QNetAgent"
Start-Website -Name "QNetAgent"

# Full IIS restart
iisreset

# View site status
Get-Website -Name "QNetAgent"

# View application pool status
Get-WebAppPoolState -Name "QNetAgentPool"

# Tail the application log
Get-Content "C:\inetpub\QNetAgent\logs\qnet_iis.log" -Tail 50 -Wait
```
