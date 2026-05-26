# 🧠 QueryMind — Natural Language to SQL Agentic System

QueryMind is an AI-powered backend that converts natural language questions into SQL queries, executes them safely against your database, and returns rich, interpreted results — complete with auto-generated chart suggestions and conversational follow-up prompts. Built on **FastAPI**, **LangGraph**, and **LangChain**, it features a self-correcting agent loop that retries failed queries up to 3 times, SQL injection protection via AST-level validation, and plug-and-play support for OpenAI, Google Gemini, and Anthropic Claude.

---

## 📐 Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        QueryMind API                            │
│                     FastAPI + Uvicorn                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐    ┌─────────────┐    ┌───────────────────────┐    │
│  │ /query  │───▶│  LangGraph  │───▶│   Result Interpreter  │    │
│  │ /schema │    │  Agent Loop │    │   Chart Suggester     │    │
│  │ /health │    │             │    │   Follow-up Engine    │    │
│  └─────────┘    │  ┌───────┐  │    └───────────────────────┘    │
│                 │  │Retry  │  │                                  │
│                 │  │Loop   │  │                                  │
│                 │  │(≤3x)  │  │                                  │
│                 │  └───────┘  │                                  │
│                 └──────┬──────┘                                  │
│                        │                                         │
│            ┌───────────┼───────────┐                            │
│            ▼           ▼           ▼                            │
│     ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│     │  Schema  │ │   SQL    │ │  Safety  │                     │
│     │  Loader  │ │ Executor │ │Validator │                     │
│     └────┬─────┘ └────┬─────┘ └──────────┘                     │
│          │            │                                         │
│          ▼            ▼                                         │
│    ┌──────────────────────────┐                                  │
│    │   PostgreSQL / SQLite    │                                  │
│    └──────────────────────────┘                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Request lifecycle:**

1. User sends a natural language question to `POST /query`.
2. The LangGraph agent loads the database schema (cached) and generates SQL.
3. The SQL safety validator rejects any destructive or injectable statements.
4. Safe SQL is executed; if it errors, the agent self-corrects and retries (up to 3×).
5. Results are interpreted in plain English, chart types are suggested, and follow-up questions are generated.

---

## ✨ Features

- 🗣️ **Natural language to SQL** — Ask questions in plain English, get structured results
- 🔄 **Self-correcting SQL** — Agent retries failed queries up to 3 times with error context
- 🛡️ **SQL injection protection** — AST-level validation blocks `DROP`, `DELETE`, `INSERT`, `UPDATE`, and multi-statement attacks
- 📊 **Auto-visualization suggestions** — Recommends chart types (bar, line, pie, etc.) based on result shape
- 💬 **Conversational memory** — Maintains chat history for contextual follow-up questions
- 🔌 **Multi-LLM support** — Switch between OpenAI, Google Gemini, and Anthropic Claude with one env var
- 🐳 **Docker-ready** — One command to spin up the full stack with PostgreSQL
- 🗄️ **Dual database support** — Works with PostgreSQL (production) and SQLite (development)
- 📋 **Schema introspection** — Live `GET /schema` endpoint for exploring your database structure

---

## 🚀 Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/your-org/querymind.git
cd querymind
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your LLM API key(s)
```

Open `.env` and set at least one LLM API key:

```dotenv
OPENAI_API_KEY=sk-...          # Required if using OpenAI (default)
GOOGLE_API_KEY=AIza...         # Required if using Gemini
ANTHROPIC_API_KEY=sk-ant-...   # Required if using Claude
LLM_PROVIDER=openai            # openai | gemini | claude
```

### 3. Start the stack

```bash
docker-compose up --build
```

The API will be available at **http://localhost:8000** once both services are healthy.

> **Without Docker (local dev):** If you prefer running without Docker, QueryMind falls back to SQLite automatically:
>
> ```bash
> pip install -r requirements.txt
> uvicorn main:app --reload
> ```

---

## 💡 Example Queries

Send a `POST` request to `/query` with a natural language question:

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the top 5 products by revenue?"}'
```

### Sample questions and responses

#### 1. Aggregation query

**Question:** `"What are the top 5 products by revenue?"`

```json
{
  "question": "What are the top 5 products by revenue?",
  "sql": "SELECT product_name, SUM(quantity * unit_price) AS revenue FROM order_details JOIN products USING (product_id) GROUP BY product_name ORDER BY revenue DESC LIMIT 5;",
  "result": [
    {"product_name": "Widget Pro", "revenue": 125400.00},
    {"product_name": "Gadget X",   "revenue": 98750.50},
    {"product_name": "Sensor V2",  "revenue": 87200.00},
    {"product_name": "Module A",   "revenue": 65430.25},
    {"product_name": "Cable Kit",  "revenue": 54100.00}
  ],
  "interpretation": "Widget Pro leads revenue at $125,400, followed by Gadget X at $98,750. The top 5 products account for the majority of total sales.",
  "chart_suggestion": {"type": "bar", "x": "product_name", "y": "revenue"},
  "follow_up_questions": [
    "What is the monthly revenue trend for Widget Pro?",
    "Which customers bought the most Widget Pro units?",
    "How does this compare to last quarter?"
  ]
}
```

#### 2. Time-series query

**Question:** `"Show me monthly order counts for the last 12 months"`

```json
{
  "question": "Show me monthly order counts for the last 12 months",
  "sql": "SELECT DATE_TRUNC('month', order_date) AS month, COUNT(*) AS order_count FROM orders WHERE order_date >= NOW() - INTERVAL '12 months' GROUP BY month ORDER BY month;",
  "result": [
    {"month": "2025-06-01", "order_count": 142},
    {"month": "2025-07-01", "order_count": 158}
  ],
  "interpretation": "Order volume has been trending upward over the past 12 months, with a peak in December likely driven by holiday demand.",
  "chart_suggestion": {"type": "line", "x": "month", "y": "order_count"},
  "follow_up_questions": [
    "Which month had the highest average order value?",
    "What is the year-over-year growth rate?"
  ]
}
```

#### 3. Lookup query

**Question:** `"How many customers signed up this year?"`

```json
{
  "question": "How many customers signed up this year?",
  "sql": "SELECT COUNT(*) AS new_customers FROM customers WHERE created_at >= DATE_TRUNC('year', CURRENT_DATE);",
  "result": [{"new_customers": 1284}],
  "interpretation": "1,284 new customers have signed up so far this year.",
  "chart_suggestion": null,
  "follow_up_questions": [
    "What is the signup trend by month?",
    "Which acquisition channel brought the most signups?"
  ]
}
```

#### 4. Comparative query

**Question:** `"Compare average order values between regions"`

```json
{
  "question": "Compare average order values between regions",
  "sql": "SELECT region, ROUND(AVG(total_amount), 2) AS avg_order_value FROM orders JOIN customers USING (customer_id) GROUP BY region ORDER BY avg_order_value DESC;",
  "result": [
    {"region": "West",    "avg_order_value": 245.80},
    {"region": "East",    "avg_order_value": 231.40},
    {"region": "Central", "avg_order_value": 198.60}
  ],
  "interpretation": "The West region has the highest average order value at $245.80, approximately 24% higher than Central.",
  "chart_suggestion": {"type": "bar", "x": "region", "y": "avg_order_value"},
  "follow_up_questions": [
    "What is the order volume per region?",
    "Which products are most popular in the West?"
  ]
}
```

#### 5. Relationship query

**Question:** `"Which employees have processed the most orders?"`

```json
{
  "question": "Which employees have processed the most orders?",
  "sql": "SELECT e.first_name || ' ' || e.last_name AS employee, COUNT(o.order_id) AS orders_processed FROM employees e JOIN orders o ON e.employee_id = o.employee_id GROUP BY employee ORDER BY orders_processed DESC LIMIT 10;",
  "result": [
    {"employee": "Jane Smith",   "orders_processed": 312},
    {"employee": "John Doe",     "orders_processed": 287},
    {"employee": "Alice Johnson","orders_processed": 265}
  ],
  "interpretation": "Jane Smith leads with 312 orders processed, 9% more than the second-place John Doe.",
  "chart_suggestion": {"type": "bar", "x": "employee", "y": "orders_processed"},
  "follow_up_questions": [
    "What is the average order value per employee?",
    "How do processing times compare across employees?"
  ]
}
```

---

## 🗄️ Connecting a Different Database

QueryMind connects to any PostgreSQL or SQLite database. Just change the `DATABASE_URL` in your `.env`:

```dotenv
# PostgreSQL (production)
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# SQLite (development / local)
DATABASE_URL=sqlite+aiosqlite:///./my_database.db
```

QueryMind will automatically introspect the schema at startup and adapt its SQL generation to the target dialect (PostgreSQL or SQLite).

> **Note:** When using Docker Compose, the `DATABASE_URL` in `docker-compose.yml` overrides the `.env` value to point to the containerized PostgreSQL instance.

---

## 🔌 LLM Provider Switching

Switch between LLM providers by changing a single environment variable:

```dotenv
# Use OpenAI GPT-4 (default)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Use Google Gemini
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIza...

# Use Anthropic Claude
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

All providers use the same agent pipeline — no code changes required. The LLM factory in `llm/factory.py` handles instantiation based on the `LLM_PROVIDER` value.

---

## 📡 API Reference

### `GET /health`

Health check endpoint. Returns service status and database connectivity.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "database": "connected",
  "llm_provider": "openai"
}
```

---

### `POST /query`

Convert a natural language question to SQL, execute it, and return interpreted results.

**Request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the top 5 products by revenue?",
    "conversation_id": "optional-uuid-for-memory"
  }'
```

| Field             | Type   | Required | Description                                      |
|-------------------|--------|----------|--------------------------------------------------|
| `question`        | string | ✅       | Natural language question about your data         |
| `conversation_id` | string | ❌       | UUID to maintain conversational context           |

**Response (200 OK):**
```json
{
  "question": "What are the top 5 products by revenue?",
  "sql": "SELECT product_name, SUM(quantity * unit_price) AS revenue ...",
  "result": [ ... ],
  "row_count": 5,
  "interpretation": "Widget Pro leads revenue at $125,400 ...",
  "chart_suggestion": {
    "type": "bar",
    "x": "product_name",
    "y": "revenue"
  },
  "follow_up_questions": [
    "What is the monthly revenue trend for Widget Pro?",
    "Which customers bought the most Widget Pro units?"
  ]
}
```

**Error Response (422):**
```json
{
  "detail": "Unsafe SQL detected: statement contains DROP keyword"
}
```

---

### `GET /schema`

Retrieve the database schema (tables, columns, types, relationships).

**Request:**
```bash
curl http://localhost:8000/schema
```

**Response (200 OK):**
```json
{
  "dialect": "PostgreSQL",
  "tables": [
    {
      "name": "products",
      "columns": [
        {"name": "product_id", "type": "INTEGER", "primary_key": true},
        {"name": "product_name", "type": "VARCHAR(255)", "primary_key": false},
        {"name": "unit_price", "type": "NUMERIC(10,2)", "primary_key": false}
      ]
    },
    {
      "name": "orders",
      "columns": [
        {"name": "order_id", "type": "INTEGER", "primary_key": true},
        {"name": "customer_id", "type": "INTEGER", "primary_key": false},
        {"name": "order_date", "type": "TIMESTAMP", "primary_key": false}
      ]
    }
  ]
}
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_safety.py

# Run with coverage report
pytest --cov=. --cov-report=term-missing
```

Tests use SQLite in-memory databases by default — no external services required.

---

## 📁 Project Structure

```
querymind/
├── main.py                     # FastAPI app entry point & route definitions
├── config.py                   # Pydantic settings (env vars, defaults)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Full-stack orchestration (API + PostgreSQL)
├── .env.example                # Environment variable template
│
├── agents/                     # LangGraph agent pipeline
│   ├── graph.py                # Agent state graph definition & compilation
│   ├── state.py                # TypedDict agent state schema
│   └── nodes.py                # Graph node functions (generate, validate, execute, …)
│
├── llm/                        # LLM provider abstraction
│   └── factory.py              # Multi-provider LLM factory (OpenAI, Gemini, Claude)
│
├── db/                         # Database layer
│   ├── engine.py               # Async SQLAlchemy engine & session factory
│   ├── schema_loader.py        # Live schema introspection with TTL caching
│   └── seeds/
│       └── sample_data.sql     # Seed data for Docker development
│
├── services/                   # Business logic services
│   ├── sql_executor.py         # Safe, async SQL execution with row limiting
│   ├── safety.py               # SQL injection & destructive-query validator
│   ├── result_interpreter.py   # LLM-powered plain-English result summaries
│   ├── chart_suggester.py      # Auto chart-type recommendation engine
│   └── followup.py             # Contextual follow-up question generator
│
├── models/                     # Pydantic request/response schemas
│   └── schemas.py              # QueryRequest, QueryResponse, SchemaResponse, …
│
├── prompts/                    # LLM prompt templates
│   └── templates.py            # System & user prompt strings
│
└── tests/                      # Test suite
    ├── conftest.py             # Shared fixtures (in-memory DB, mock LLM)
    ├── test_safety.py          # SQL validator unit tests
    ├── test_agent.py           # Agent graph integration tests
    └── test_api.py             # FastAPI endpoint tests
```

---

## 🔧 Configuration Reference

| Variable              | Default                                        | Description                          |
|-----------------------|------------------------------------------------|--------------------------------------|
| `OPENAI_API_KEY`      | —                                              | OpenAI API key                       |
| `GOOGLE_API_KEY`      | —                                              | Google AI API key                    |
| `ANTHROPIC_API_KEY`   | —                                              | Anthropic API key                    |
| `LLM_PROVIDER`        | `openai`                                       | LLM backend: `openai`/`gemini`/`claude` |
| `DATABASE_URL`        | `sqlite+aiosqlite:///./dev.db`                 | Async database connection string     |
| `MAX_RETRIES`         | `3`                                            | Max SQL self-correction attempts     |
| `SCHEMA_CACHE_TTL`    | `300`                                          | Schema cache lifetime (seconds)      |
| `MAX_RESULT_ROWS`     | `100`                                          | Max rows returned per query          |
| `LOG_LEVEL`           | `INFO`                                         | Logging level                        |

---

## 📄 License

MIT

---

<p align="center">
  Built with ❤️ using FastAPI, LangGraph, and LangChain
</p>
