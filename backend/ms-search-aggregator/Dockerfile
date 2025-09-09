FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/ms-search-aggregator/pyproject.toml backend/ms-search-aggregator/uv.lock* ./
RUN uv sync --no-dev --frozen

COPY backend/ms-search-aggregator/ ./
COPY backend/utils/ ./utils/

EXPOSE 8000

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]