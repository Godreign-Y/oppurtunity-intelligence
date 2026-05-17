---
trigger: manual
---

# Role & Project Context
You are an expert Senior Software Engineer.

# Tech Stack Constraints
- Backend: FastAPI
- Python Version: Strictly 3.11.x
- Database: Neon (Serverless PostgreSQL)
- Package Manager: `uv` (Strictly enforced)
- Migrations: Alembic

# 🚨 CRITICAL RULES (MUST FOLLOW AT ALL TIMES) 🚨
1. ALWAYS use `uv` for Python package management. NEVER use `pip`, `pipenv`, or `poetry`. All installation commands must use `uv pip install ...`.
2. ALWAYS use Alembic for database migrations. NEVER execute raw DDL (CREATE TABLE, ALTER) directly against the Neon database.
3. ALWAYS keep code extremely modular. Separate concerns (extraction, transformation, database loading) into distinct files. Do not write monolithic scripts.
4. ALWAYS use Python type hints for all variables, functions, and class methods. No exceptions.
5. ALWAYS create Google-style docstrings for any file, function, and class. 
6. NEVER mock implementations. If a real implementation is blocked (e.g., missing API key, rate limit, database connection issue), STOP, ask for clarification, and explain the blocker before proceeding. Do not write dummy data functions.