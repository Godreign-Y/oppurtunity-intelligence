FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv — copy binary from official image (no pip required)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock* ./

# Install dependencies into the system Python (no venv needed in containers)
RUN uv sync --no-dev --frozen --system

# Copy application code
COPY . .

# Create log directory
RUN mkdir -p /var/log/opp-intel

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["sh", "-c", "uv run --system uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
