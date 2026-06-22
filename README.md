# Susan- Interviewer Intelligence Platform (IIP)

The **Susan** is a production-grade, enterprise-ready full-stack application for AI-driven adaptive interviewing, continuous skill modeling, and candidates' evaluation.

The repository is structured as a monorepo containing a high-performance Python backend and a modern Next.js/React frontend.

---

## Project Structure

``` bash
AI-Interviewer/
├── backend/               # FastAPI application, UV environment, database migrations
├── frontend/              # Next.js web application (React, TypeScript, ESLint)
├── docker-compose.yml     # Orchestration for PostgreSQL, Redis, Qdrant, MinIO, & Backend
├── Makefile               # Automated workspace commands (Setup, run, test, lint)
├── .gitignore             # Root git ignore patterns
├── .gitattributes         # Line-ending normalization configurations
└── .env                   # Shared local environment configuration
```

---

## Technology Stack

### Backend

- **Core Framework**: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async)
- **Data & Vector Storage**:

  - PostgreSQL (Relational Storage)
  - Redis (Caching & Lock Management)
  - Qdrant (Vector Database for RAG / Embedding index)
  - MinIO (Object Storage for resumes & audio/video interview recordings)
- **Dependency Management**: `uv` (Fast Python dependency installer and environment manager)
- **Task Pipeline**: Celery, Redis Broker
- **Observability**: OpenTelemetry, Prometheus, Langfuse

### Frontend

- **Core Framework**: Next.js 15+ (App Router), React 19, TypeScript
- **Styling & Components**: PostCSS, TailwindCSS, CSS Modules
- **Development Tooling**: ESLint, TSConfig

---

## Getting Started

Follow these steps to get the entire workspace up and running locally.

### Prerequisites

Ensure you have the following installed on your machine:

1. Docker & Docker Compose
2. Python 3.12 & uv
3. Node.js (v18+) & npm
4. Make utility (highly recommended for convenience)

---

### Installation & Running

#### 1. Spin up Infrastructure (Docker)

Start the supporting services (PostgreSQL, Redis, Qdrant, MinIO) in the background:

```bash
make up
# Or: docker compose up -d postgres redis qdrant minio
```

#### 2. Install Project Dependencies

Install both backend (via `uv`) and frontend (via `npm`) dependencies with one command:

```bash
make install
```

#### 3. Initialize the Database

Run the seed scripts to provision PostgreSQL schemas and initial metadata:

```bash
make init-db
# Or: cd backend && uv run python scripts/init_db.py
```

#### 4. Run the Development Servers

- **Start Backend API Gateway** (runs on <http://localhost:8000>):

  ```bash
  make run
  # Or: cd backend && uv run uvicorn src.main:app --port 8000
  ```

- **Start Frontend Next.js Client** (runs on <http://localhost:3000>):

  ```bash
  make run-frontend
  # Or: cd frontend && npm run dev
  ```

---

## Command Matrix (Makefile Cheat Sheet)

| Command | Description | Directory Context |
| :--- | :--- | :--- |
| `make install` | Installs both backend and frontend dependencies | Root |
| `make up` | Starts all Docker containers (db, vector, cache, storage) | Root |
| `make down` | Stops and removes Docker containers | Root |
| `make init-db` | Runs database initialization & seeding scripts | `backend/` |
| `make run` | Starts the backend FastAPI server locally | `backend/` |
| `make run-frontend` | Starts the Next.js development server locally | `frontend/` |
| `make test` | Runs Pytest suite on backend code | `backend/` |
| `make lint` | Runs Ruff linter on backend | `backend/` |
| `make format` | Runs Ruff formatter on backend | `backend/` |
| `make lint-frontend` | Runs ESLint checker on frontend codebase | `frontend/` |
| `make clean` | Cleans up cache directories (`.pytest_cache`, `.ruff_cache`) | `backend/` |

---

## Sub-module References

For detailed setup, architectural specifications, and implementation details of individual layers, check their respective documentation:

- **[Backend README](file:///C:/Users/Shadab/Downloads/AI-Interviewer/backend/README.md)**
- **[Frontend README](file:///C:/Users/Shadab/Downloads/AI-Interviewer/frontend/README.md)**
