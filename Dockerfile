FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN python -m pip install --upgrade pip && \
    python -m pip install uv && \
    python -m uv sync --no-dev --locked

COPY . .

EXPOSE 8000

CMD ["python", "-m", "uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
