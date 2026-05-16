# IDE Rules for AI Opportunity Intelligence Platform

## Python Package Management
- **Always use UV** for Python package management. Never use pip, poetry, or pipenv directly.
- Install packages: `uv add <package>`
- Run scripts: `uv run <script>`
- Sync dependencies: `uv sync`

## Database Migrations
- **Always use Alembic** for all database schema changes.
- Generate migration: `uv run alembic revision --autogenerate -m "<description>"`
- Apply migrations: `uv run alembic upgrade head`
- Never modify the database schema directly without a corresponding Alembic migration.

## Code Modularity
- **Always keep code very modular.** Each file should have a single responsibility.
- Services must be split by domain (career, blog, ai, etc.).
- Utility functions must be grouped logically in the `utils/` module.
- Never put business logic in API endpoint files — delegate to service layer.

## Type Hints
- **Always use type hints** for all function parameters and return types.
- Use `Optional[T]` from `typing` for nullable values.
- Use Pydantic models for all request/response schemas.

## Docstrings
- **Always create docstrings** for every file, function, and class.
- File-level docstrings describe the module's purpose.
- Function docstrings describe parameters, return values, and behavior.
- Class docstrings describe the class purpose and its attributes.

## No Mock Implementations
- **Never mock an implementation.** If a real implementation is blocked by missing credentials or external services, explain the blocker and ask before proceeding.
- Placeholder values (like API keys) must be clearly marked with `TODO:` comments.

## Python Version
- Use **Python 3.11.x** only.

## Database
- Use **Neon** (PostgreSQL-compatible) for all relational storage.
- Connection strings must be loaded from environment variables only.
