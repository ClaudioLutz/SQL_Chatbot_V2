# SQL Chatbot POC (SQL_Chatbot_V2)

Natural‑language → SQL for Microsoft SQL Server, built with **FastAPI**, a tiny **HTML/JS** frontend, and **OpenAI (GPT‑5)** for SQL generation. The app is intended as a **proof‑of‑concept** to demo querying a SQL database (e.g., AdventureWorks) without writing SQL.

> ⚠️ **Safety first**: the backend enforces **read‑only** access. Only `SELECT` statements are allowed and potentially dangerous patterns are rejected. Non‑aggregate queries are capped with `TOP 200` rows by default.

---

## Features

* Ask questions in plain English; receive the generated SQL and results
* **Automatic data analysis** with statistical insights in the Analysis tab
* Read‑only execution against SQL Server (e.g., AdventureWorks)
* Minimal, self‑contained frontend served by FastAPI
* Simple configuration via `.env`

## Analysis Feature

### Overview
The SQL Chatbot now includes automatic data analysis capabilities. After executing a query, users can view statistical insights about their data in the Analysis tab.

### Features
- **Variable Type Summary:** Breakdown of column data types
- **Numeric Statistics:** Mean, standard deviation, quartiles for numeric columns
- **Cardinality Analysis:** Unique value counts for all columns
- **Missing Values:** Detection of null/missing data

### Usage
1. Submit a natural language question
2. View query results in the Results tab
3. Click the **Analysis** tab to see statistical summary
4. Analysis is generated automatically (< 2 seconds for typical datasets)

### Limitations
- Analysis requires at least 2 rows of data
- Maximum dataset size: 50,000 rows
- Datasets exceeding the limit will display an informational message

### Dependencies
- `skimpy==0.0.9` - Statistical analysis engine
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical operations

---

## Architecture (at a glance)

* **Frontend**: static HTML/CSS/JS served from `/` by FastAPI
* **Backend**: FastAPI with one main endpoint `POST /api/query`
* **AI**: OpenAI model (default: `gpt-5`) translates question → SQL
* **DB**: SQL Server via `pyodbc`

See detailed docs in `docs/` (PRD, Architecture, Brief).

---

## Project Structure

```
/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app + /api/query + serves /static
│   └── services.py      # GPT → SQL + safety checks + DB execution
├── static/
│   ├── index.html       # Minimal UI
│   ├── app.js           # Calls /api/query and renders results
│   └── styles.css
├── docs/
│   ├── prd.md           # Product requirements
│   ├── architecture.md  # Architecture blueprint
│   └── brief.md         # Project brief
├── .env.example         # Template for local configuration
├── requirements.txt
└── README.md
```

---

## Prerequisites

* **Python** 3.11+
* **SQL Server** reachable from your machine (AdventureWorks sample recommended)
* **ODBC Driver 18 for SQL Server** (required by `pyodbc`)
* **OpenAI API key** with access to a GPT‑5 family model

---

## Quickstart

1. **Clone & create a virtual env**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment**
   Copy `.env.example` → `.env` and fill in values:

```env
OPENAI_API_KEY=sk-...
# Optional (defaults shown)
OPENAI_MODEL=gpt-5
DB_CONNECTION_STRING="DRIVER={ODBC Driver 18 for SQL Server};SERVER=localhost,1433;DATABASE=AdventureWorks2022;UID=sa;PWD=...;Encrypt=Yes;TrustServerCertificate=Yes"
```

4. **Run the app**

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) and try a question, e.g., “How many employees are currently active?”

---

## API

### `POST /api/query`

**Request**

```json
{
  "question": "Top 10 products by sales last year"
}
```

**Response (success)**

```json
{
  "sql_query": "SELECT TOP 200 ...",
  "results": {
    "columns": ["Col1", "Col2", "..."],
    "rows": [
      {"Col1": "...", "Col2": "..."}
    ]
  }
}
```

**Response (DB error)**

```json
{
  "sql_query": "SELECT ...",
  "results": { "error": "<message>" }
}
```

### `POST /api/analyze`

Generate statistical analysis for query results.

**Request**

```json
{
  "columns": ["Name", "ListPrice"],
  "rows": [
    {"Name": "Product A", "ListPrice": 49.99},
    {"Name": "Product B", "ListPrice": 29.99}
  ]
}
```

**Response (Success)**

```json
{
  "status": "success",
  "row_count": 150,
  "column_count": 5,
  "variable_types": {
    "numeric": 2,
    "categorical": 2,
    "datetime": 1
  },
  "numeric_stats": [
    {
      "column": "ListPrice",
      "count": 150,
      "mean": 3486.63,
      "std": 96.88,
      "min": 3374.99,
      "q25": 3399.99,
      "q50": 3489.13,
      "q75": 3578.27,
      "max": 3578.27
    }
  ],
  "cardinality": [
    {"column": "Name", "unique_count": 150, "total_count": 150},
    {"column": "ListPrice", "unique_count": 3, "total_count": 150}
  ],
  "missing_values": [
    {"column": "Name", "null_count": 0, "null_percentage": 0.0},
    {"column": "ListPrice", "null_count": 0, "null_percentage": 0.0}
  ]
}
```

**Response (Too Large)**

```json
{
  "status": "too_large",
  "row_count": 75000,
  "column_count": 5,
  "message": "Analysis unavailable for datasets exceeding 50,000 rows. Please refine your query for detailed statistics."
}
```

**Response (Insufficient Data)**

```json
{
  "status": "insufficient_rows",
  "row_count": 1,
  "column_count": 3,
  "message": "Analysis requires at least 2 rows of data."
}
```

**Response (Error)**

```json
{
  "status": "error",
  "message": "Analysis could not be generated for this dataset.",
  "error_detail": "..."
}
```

**Status Codes:**
- 200: Success (includes all response types above)
- 422: Validation error (malformed request)
- 500: Server error

---

## Configuration

Environment variables (set in `.env`):

* `OPENAI_API_KEY` – required
* `OPENAI_MODEL` – defaults to `gpt-5`
* `DB_CONNECTION_STRING` – SQL Server ODBC connection string
* Optional runtime tuning:

  * `OPENAI_REQUEST_TIMEOUT` (seconds, default `30`)
  * `OPENAI_MAX_RETRIES` (default `2`)

---

## Implementation Notes

* **Safety guardrails**: Only `SELECT` statements permitted, common DDL/DML keywords blocked, multiple‑statement attempts rejected. Non‑aggregate queries are wrapped with `TOP 200` if no explicit limit is present.
* **Result shape**: backend returns `{ columns: string[], rows: object[] }` where each row is a dict keyed by column name.
* **Frontend**: renders generated SQL and tabular results, and displays friendly errors.

---

## Troubleshooting

* **ODBC driver not found**: ensure *ODBC Driver 18 for SQL Server* is installed and your connection string uses that driver name.
* **Cannot connect to DB**: verify host/port/firewall and credentials; try connecting with a SQL client using the same string.
* **Empty/unsafe SQL**: the backend will retry once with stricter instructions; unsafe SQL is rejected with a clear error.

---

## Roadmap / Ideas

* Optional **visualization** page: auto‑analysis (pandas) and chart suggestions; ability to request custom plots
* Query history and saved insights
* Authentication and per‑user connection profiles

---

## Contributing

PRs welcome! Keep changes small and focused. Please add/update docstrings and update this README if you change setup or behavior.

---

## License

TBD
