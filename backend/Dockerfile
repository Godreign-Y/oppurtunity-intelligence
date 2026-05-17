FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv — copy binary from official image (no pip required)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Tell uv to use the system Python, not create a venv
# This is the correct way to prevent venv creation inside containers
ENV UV_SYSTEM_PYTHON=1

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (frozen = use exact versions from uv.lock)
RUN uv sync --no-dev --frozen

# Copy application code
COPY . .

# Create log directory
RUN mkdir -p /var/log/opp-intel

# Expose port
EXPOSE 8000

# Run with uvicorn — uses $PORT from Render, fallback 8000 for local
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
