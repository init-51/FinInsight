# FinInsight

FinInsight is a backend service for financial data analysis and insights. It will collect market data, perform analysis, and provide an API for frontend and other services.

Tech stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Redis
- Celery
- Uvicorn

Local setup
1. Create a virtual environment and activate it:

   Windows (PowerShell):
   python -m venv .venv; .\.venv\Scripts\Activate.ps1

2. Install dependencies:

   pip install -r requirements.txt

3. Copy `.env.example` to `.env` and adjust values.

4. Run FastAPI locally:

   uvicorn app.main:app --reload

Next steps
- Add Docker files and compose for Postgres/Redis/Celery
- Implement database models, routers, and background tasks
