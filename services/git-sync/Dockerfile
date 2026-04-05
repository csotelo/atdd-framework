FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e . pyyaml

COPY atdd_orchestrator/ ./atdd_orchestrator/

CMD ["python", "-m", "atdd_orchestrator.infrastructure.git_sync"]
