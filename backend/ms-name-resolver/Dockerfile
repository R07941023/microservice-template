FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# Copy utils for future use (to ../utils relative to /app)
COPY backend/utils/ /utils/

COPY backend/ms-name-resolver/pyproject.toml backend/ms-name-resolver/uv.lock* ./
RUN uv sync --no-dev --frozen

COPY backend/ms-name-resolver/ ./

EXPOSE 8000

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]