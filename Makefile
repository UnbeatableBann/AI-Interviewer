# Platform-agnostic Virtual Environment paths detection
ifeq ($(OS),Windows_NT)
	VENV_BIN = .venv\Scripts
	PYTHON = $(VENV_BIN)\python.exe
else
	VENV_BIN = .venv/bin
	PYTHON = $(VENV_BIN)/python
endif

UVICORN = $(PYTHON) -m uvicorn
PYTEST = $(PYTHON) -m pytest
RUFF = $(PYTHON) -m ruff

.PHONY: help install install-backend install-frontend up down init-db run run-frontend build-frontend test lint lint-frontend format clean

help:
	@echo "Interviewer Intelligence Platform - Command Guide:"
	@echo "  Setup & Install:"
	@echo "    make install           - Install both backend and frontend dependencies"
	@echo "    make install-backend   - Install backend dependencies using uv"
	@echo "    make install-frontend  - Install frontend dependencies using npm"
	@echo "  Docker Orchestration:"
	@echo "    make up                - Start database, vector, cache & backend containers"
	@echo "    make down              - Stop local containers"
	@echo "  Backend Operations:"
	@echo "    make init-db           - Provision tables in PostgreSQL"
	@echo "    make run               - Run the FastAPI application locally"
	@echo "    make test              - Run the backend test suite"
	@echo "    make lint              - Lint backend using Ruff"
	@echo "    make format            - Auto-format backend using Ruff"
	@echo "  Frontend Operations:"
	@echo "    make run-frontend      - Run the Next.js dev server locally"
	@echo "    make build-frontend    - Build Next.js optimized production package"
	@echo "    make lint-frontend     - Lint frontend codebase using ESLint"
	@echo "  Cleanup:"
	@echo "    make clean             - Remove Python caching artifacts"

install-backend:
	cd backend && uv sync

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

up:
	docker compose up

down:
	docker compose down

init-db:
	cd backend && $(PYTHON) scripts/init_db.py

run:
	cd backend && $(UVICORN) src.main:app --port 8000

run-frontend:
	cd frontend && npm run dev

build-frontend:
	cd frontend && npm run build

test:
	cd backend && $(PYTEST)

lint:
	cd backend && $(RUFF) check src tests

lint-frontend:
	cd frontend && npm run lint

format:
	cd backend && $(RUFF) format src tests

clean:
	rm -rf backend/.pytest_cache backend/.ruff_cache
