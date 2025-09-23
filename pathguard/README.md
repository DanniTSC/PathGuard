
# PathGuard — Minimal MVP Starter

This is a minimal scaffolding to demonstrate, in a single day, the bullets on your CV:
- **ETL**: Prefect flow that ingests a small GeoJSON of street segments and computes a toy `safety_score`.
- **API**: FastAPI with `/health` and `/route` (toy) endpoints.
- **LLM touchpoint**: A wrapper with a `USE_HF` flag (currently rule-based fallback); swap with a Hugging Face model if you want.
- **Dashboard**: Streamlit page that calls the API and shows a basic view (title + placeholder).

> Scope is microscopic by design. You can extend later.

## Quickstart

### 0) Create & activate a virtual environment
```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 1) Install deps
```bash
pip install -r requirements.txt
```

### 2) Run the ETL once (writes a parquet file)
```bash
python etl/flow.py
```

### 3) Run the API
```bash
uvicorn app.api:app --reload
```

### 4) Run the dashboard (in a second terminal)
```bash
streamlit run dashboard/Home.py
```

Open the Streamlit URL in your browser. The dashboard is minimal; it prints the API base URL and offers a placeholder button.

## Environment
Create a `.env` at the project root if you want to customize:
```
API_BASE=http://127.0.0.1:8000
USE_HF=false
```

## Notes
- PostGIS/DVC are intentionally left as "ready to integrate" to keep setup fast. You can add them later.
- Code is commented with TODOs to guide you during the 1‑day build.
