FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Copy utils first (to ../utils relative to /app)
COPY backend/utils/ /utils/

# Copy dependency files and sync
COPY backend/ms-search-aggregator/pyproject.toml backend/ms-search-aggregator/uv.lock* ./
RUN uv sync --no-dev --frozen

COPY backend/ms-search-aggregator/ ./

EXPOSE 8000

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]