FROM python:3.11-slim
WORKDIR /app
# install uv
RUN pip install --no-cache-dir uv
# add package management file
COPY pyproject.toml uv.lock ./
# uv install
RUN uv sync --no-dev --frozen
# code
COPY . .
# port
EXPOSE 8000
# run
CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]