# Interviewer Intelligence Platform (IIP)

Production-grade enterprise backend for AI-driven adaptive interviewing, continuous skill modeling, and evaluation.

## Technology Stack

- **Framework**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic
- **Storage**: PostgreSQL (Relational), Redis (Caching & Lock Manager), Qdrant (Vector DB), MinIO (Object Storage)
- **Background Pipeline**: Celery, Redis Broker
- **Observability**: OpenTelemetry, Prometheus, Langfuse

## Getting Started

This project uses `uv` for python environment and dependency management.

### Prerequisites

Make sure you have `uv` installed:

```bash
uv --version
```

### Installation

Install dependencies and synchronize the environment:

```bash
uv sync
```

### Run API Gateway

Start the FastAPI application locally:

```bash
uv run uvicorn src.main:app --reload
```
