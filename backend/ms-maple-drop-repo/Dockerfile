FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/ms-maple-drop-repo/pyproject.toml backend/ms-maple-drop-repo/uv.lock* ./
RUN uv sync --no-dev --frozen

COPY backend/ms-maple-drop-repo/ ./
COPY backend/utils/ ./utils/

EXPOSE 8000

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]