# 🏦 Financial Document Analyzer

AI-powered financial document analysis system built with **CrewAI** and **FastAPI**. Upload financial PDFs and get comprehensive AI-driven analysis including investment recommendations and risk assessments.

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **LLM** | Google Gemini 2.5 Flash (via CrewAI + LiteLLM) |
| **AI Framework** | CrewAI (Multi-Agent Orchestration) |
| **Web Framework** | FastAPI + Uvicorn |
| **PDF Processing** | PyPDF |
| **Web Search** | Serper.dev API |
| **Database** | SQLAlchemy + SQLite |
| **Queue Worker** | Celery + Redis |
| **Language** | Python 3.10+ |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
│  /analyze (sync) │ /analyze/async │ /results │ /status  │
└──────────┬───────────────┬──────────────────────────────┘
           │               │
     ┌─────▼─────┐   ┌────▼─────┐
     │  run_crew  │   │  Celery  │
     │  (sync)    │   │  Worker  │
     └─────┬──────┘   └────┬─────┘
           │               │
     ┌─────▼───────────────▼──────┐
     │     CrewAI Sequential      │
     │         Pipeline           │
     │                            │
     │  1. Verifier Agent         │
     │  2. Financial Analyst      │
     │  3. Investment Advisor     │
     │  4. Risk Assessor          │
     └─────────────┬──────────────┘
                   │
     ┌─────────────▼──────────────┐
     │   SQLite Database          │
     │   (Analysis Results)       │
     └────────────────────────────┘
```

---

## 🐛 Bugs Found & Fixed

### Deterministic Bugs

#### `tools.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai_tools import tools` — `tools` is not a valid import from crewai_tools | Changed to `from crewai.tools import tool` (the `@tool` decorator) |
| 2 | `Pdf(file_path=path).load()` — `Pdf` class is never imported/undefined | Replaced with `pypdf.PdfReader` for PDF text extraction |
| 3 | `async def read_data_tool(...)` — async class methods don't work as CrewAI tools | Converted to synchronous functions with `@tool` decorator |
| 4 | Default path `data/sample.pdf` — doesn't match actual file `TSLA-Q2-2025-Update.pdf` | Fixed default path to `data/TSLA-Q2-2025-Update.pdf` |
| 5 | Methods inside classes (`FinancialDocumentTool`, `InvestmentTool`, `RiskTool`) lack `self`/`@staticmethod` and aren't decorated as tools | Extracted as standalone `@tool`-decorated functions |

#### `agents.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | `from crewai.agents import Agent` — incorrect import path | Changed to `from crewai import Agent, LLM` |
| 2 | `llm = llm` — self-referencing variable causes `NameError` | Initialized properly: `LLM(model="gemini/gemini-2.5-flash")` |
| 3 | `tool=[...]` — typo, Agent expects `tools` (plural) | Fixed to `tools=[...]` |
| 4 | `max_iter=1` — agent can only attempt once, too restrictive | Increased to `max_iter=5` |
| 5 | `max_rpm=1` — 1 request/minute makes the system extremely slow | Increased to `max_rpm=10` |
| 6 | `allow_delegation=True` on `financial_analyst` but only 1 agent in crew — delegation fails | Set to `False` (agents work sequentially) |
| 7 | `verifier`, `investment_advisor`, `risk_assessor` defined but never used | Added all agents to the Crew |

#### `task.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | All tasks use `agent=financial_analyst` instead of their proper agents | Assigned correct agents: `verifier`, `investment_advisor`, `risk_assessor` |
| 2 | `investment_analysis`, `risk_assessment`, `verification` tasks are defined but never used in Crew | Added all tasks to the Crew pipeline |

#### `main.py`
| # | Bug | Fix |
|---|-----|-----|
| 1 | `async def analyze_financial_document(...)` — same name as imported task, shadows the import | Renamed endpoint to `analyze_document_endpoint` |
| 2 | `file_path` passed to `run_crew()` but never forwarded to Crew inputs | Added `file_path` to the crew kickoff inputs dict |
| 3 | Crew only has 1 agent and 1 task | Updated to include all 4 agents and 4 tasks |
| 4 | `uvicorn.run(app, ..., reload=True)` — reload doesn't work with app object directly | Changed to `uvicorn.run("main:app", ...)` with string reference |

#### `requirements.txt`
| # | Bug | Fix |
|---|-----|-----|
| 1 | Missing `python-dotenv` (used by `load_dotenv()`) | Added |
| 2 | Missing PDF library (`pypdf`) | Added |
| 3 | Missing `uvicorn` (needed to run FastAPI) | Added |
| 4 | Missing `requests` (needed for custom Serper search tool) | Added |
| 5 | `pydantic==1.10.13` conflicts with CrewAI (needs v2) | Removed conflicting pin |
| 6 | `pip==24.0` shouldn't be in requirements | Removed |
| 7 | README says `requirement.txt` (singular) | Fixed filename in README |

---

### Inefficient Prompts Fixed

**All agent and task prompts were intentionally harmful** — they encouraged:
- Fabricating financial data and making up numbers
- Ignoring the user's actual query
- Giving unethical/non-compliant financial advice
- Including fake URLs and made-up research
- Contradicting themselves within responses

**Fixes applied:**
- **Agent roles**: Changed from satirical (e.g., "Investment Guru and Fund Salesperson") to professional (e.g., "Certified Investment Advisor")
- **Agent goals**: Changed from "make up advice" to "provide accurate, data-driven analysis based on the actual document"
- **Agent backstories**: Replaced reckless fictional personas with professional credentials and ethical standards
- **Task descriptions**: Changed from "feel free to use your imagination" to structured, specific analysis instructions
- **Task expected_outputs**: Changed from "make up URLs" to professional report formats with data requirements

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- A [Google Gemini API Key](https://aistudio.google.com/apikey) (requires Google Cloud billing — free $300 trial available)
- (Optional) [Serper API Key](https://serper.dev) for web search capability
- (Optional) [Redis](https://redis.io) for async queue processing

### Installation

```bash
# Clone the repository
git clone https://github.com/abhishekdev-ap/Wingify-Debug-.git
cd financial-document-analyzer-debug

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Download Sample Document

```bash
# Download Tesla Q2 2025 financial update
curl -L -o data/TSLA-Q2-2025-Update.pdf \
  "https://www.tesla.com/sites/default/files/downloads/TSLA-Q2-2025-Update.pdf"
```

### Run the Server

```bash
python main.py
# Or using uvicorn directly:
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

---

## 📡 API Documentation

### `GET /` — Health Check
```bash
curl http://localhost:8000/
```
**Response:**
```json
{"message": "Financial Document Analyzer API is running"}
```

---

### `POST /analyze` — Synchronous Analysis
Upload a PDF and wait for the full analysis.

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=What are Tesla's key financial metrics and growth prospects?"
```
**Response:**
```json
{
  "status": "success",
  "task_id": "uuid-string",
  "query": "What are Tesla's key financial metrics...",
  "analysis": "Comprehensive AI analysis...",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```

---

### `POST /analyze/async` — Async Analysis (Bonus: Queue Worker)
Queue a document for background processing. Requires Redis + Celery worker running.

```bash
curl -X POST http://localhost:8000/analyze/async \
  -F "file=@data/TSLA-Q2-2025-Update.pdf" \
  -F "query=Analyze risk factors"
```
**Response:**
```json
{
  "status": "queued",
  "task_id": "uuid-string",
  "message": "Document analysis has been queued. Use /status/{task_id} to check progress."
}
```

---

### `GET /status/{task_id}` — Check Task Status
```bash
curl http://localhost:8000/status/{task_id}
```
**Response:**
```json
{
  "task_id": "uuid-string",
  "status": "completed",
  "filename": "TSLA-Q2-2025-Update.pdf",
  "query": "...",
  "result": "Full analysis...",
  "created_at": "2025-01-01 00:00:00",
  "completed_at": "2025-01-01 00:05:00"
}
```

---

### `GET /results` — List All Results (Bonus: Database)
```bash
curl "http://localhost:8000/results?limit=10&offset=0"
```

### `GET /results/{task_id}` — Get Specific Result
```bash
curl http://localhost:8000/results/{task_id}
```

---

## ⚡ Bonus Features

### 1. Queue Worker Model (Celery + Redis)

For handling concurrent requests:

```bash
# Start Redis (install via brew/apt if needed)
redis-server

# Start Celery worker (in a separate terminal)
celery -A celery_worker.celery_app worker --loglevel=info

# Use the async endpoint
curl -X POST http://localhost:8000/analyze/async \
  -F "file=@data/TSLA-Q2-2025-Update.pdf"
```

### 2. Database Integration (SQLAlchemy + SQLite)

All analysis results are automatically stored in `financial_analyzer.db`:
- Query past results via `/results` endpoint
- Track analysis status (pending → processing → completed/failed)
- Persistent storage across server restarts

---

## 📁 Project Structure

```
financial-document-analyzer-debug/
├── main.py              # FastAPI application with all endpoints
├── agents.py            # CrewAI agent definitions (4 agents)
├── task.py              # CrewAI task definitions (4 tasks)
├── tools.py             # Custom tools (@tool decorated functions)
├── database.py          # SQLAlchemy models and database operations
├── celery_worker.py     # Celery async task worker
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── data/                # PDF documents directory
│   └── TSLA-Q2-2025-Update.pdf
├── outputs/             # Analysis output directory
└── README.md            # This file
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for LLM |
| `SERPER_API_KEY` | ❌ Optional | Serper.dev API key for web search |
| `REDIS_URL` | ❌ Optional | Redis URL for Celery (default: `redis://localhost:6379/0`) |
| `DATABASE_URL` | ❌ Optional | Database URL (default: `sqlite:///./financial_analyzer.db`) |

---

## 📊 Sample Output

When analyzing the Tesla Q2 2025 PDF, the system produces:

```json
{
  "status": "success",
  "task_id": "0e0c8cfa-36d7-4384-aed3-6bf02f7eb525",
  "query": "What are Tesla's key financial metrics?",
  "analysis": "**Comprehensive Risk Assessment Report for Tesla (Q2 2025)**\n\nOverall Risk Rating: Medium-High\n\n- Total Automotive Revenue: $16,661M (-16% YoY)\n- Total GAAP Gross Margin: 17.2% (-71 bp YoY)\n- Operating Margin: 4.1% (-219 bp YoY)\n- Diluted EPS: $0.33 (-18% YoY)\n- Free Cash Flow: $146M (-89% YoY)\n- Cash & Investments: $36,782M (+20% YoY)\n\nIncludes risk severity matrix, investment recommendations,\nand industry benchmark comparisons...",
  "file_processed": "TSLA-Q2-2025-Update.pdf"
}
```
