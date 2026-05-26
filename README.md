# QueryMind 🧠✨

QueryMind is an AI-powered natural language database query assistant. It allows users to ask questions about their database in plain English, securely generates the corresponding SQL, executes it, and returns the results in rich formats including plain text summaries, interactive data tables, and dynamic charts.

![QueryMind UI Mockup](querymind_ui_mockup_1779784808957.png)

## 🌟 Features

- **Natural Language to SQL**: Powered by LLMs (Claude/Groq) to intelligently translate user questions into accurate SQL queries.
- **Secure Execution Engine**: Read-only database access and strict query validation to prevent destructive operations or SQL injections.
- **Rich Interactive UI**: A premium, responsive "Dark Neon" frontend built with React and Vite.
- **Dynamic Charting**: Automatically suggests and renders Bar, Line, and Pie charts based on the queried data.
- **Schema Explorer**: Inspect your database tables and columns directly from the sidebar.
- **Session History**: Easily review and replay past queries.
- **Follow-up Suggestions**: AI-generated smart prompts to guide your next analytical questions.

## 🏗️ Architecture

This repository is structured as a monorepo containing both the frontend and the backend:

- `/querymind` — The backend API built with **Python**, **FastAPI**, and **LangGraph**. It handles LLM orchestration, SQL generation, and database execution.
- `/querymind-ui` — The frontend interface built with **React**, **Vite**, and **Vanilla CSS**. It provides the chat interface, data tables, and chart rendering.

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v24 or later)
- **Python** (3.10 or later)
- **Docker** & **Docker Compose** (optional, for running PostgreSQL)

### 1. Backend Setup

The backend can be run using either an in-memory SQLite database (for quick testing) or a PostgreSQL instance.

```bash
# Navigate to the backend directory
cd querymind

# Create a virtual environment
python -m venv venv
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create a .env file and add your API keys
echo "LLM_PROVIDER=groq" > .env
echo "GROQ_API_KEY=your_api_key_here" >> .env
echo "DB_TYPE=sqlite" >> .env

# Run the FastAPI server (starts on http://localhost:8000)
python main.py
```

*(Optional)* To use PostgreSQL with seeded dummy data instead of SQLite, start the Docker container:
```bash
docker-compose up -d
```
Then update your `.env` to `DB_TYPE=postgres` and restart the Python server.

### 2. Frontend Setup

The frontend proxy is configured to automatically route `/api` requests to `http://localhost:8000`.

```bash
# Navigate to the frontend directory
cd querymind-ui

# Install dependencies
npm install

# Start the Vite development server (starts on http://localhost:5173)
npm run dev
```

### 3. Usage

1. Open **[http://localhost:5173](http://localhost:5173)** in your browser.
2. Check the top right header to ensure the Health Indicator says **"Connected"**.
3. Use the **Schema tab** in the sidebar to understand what data is available.
4. Type a question in the chat input (e.g., *"Show me the top 5 highest paying customers"*).
5. View the SQL generated, the data table returned, and the visual charts!

---

## 🛠️ Technology Stack

**Frontend:**
- React 18
- Vite
- Recharts (for data visualization)
- Highlight.js (for SQL syntax highlighting)
- Lucide React (for iconography)

**Backend:**
- Python 3.10+
- FastAPI (for high-performance REST API)
- LangChain & LangGraph (for agentic LLM flows)
- SQLAlchemy (for database connections)
- Docker (for PostgreSQL hosting)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📝 License

This project is licensed under the MIT License.
