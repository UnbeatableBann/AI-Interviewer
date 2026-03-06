# AI Mock Interviewer Backend

Production-ready FastAPI backend for AI-powered mock interviews.  
Supports HR and candidate roles, Appwrite authentication/storage, Mistral LLM, Redis fallback, and modular code.

## Features

- User signup/login/logout (HR & candidate)
- Interview generation and answer evaluation (Mistral LLM)
- Appwrite DB for users, interviews, answers
- HR dashboard: analytics, scores, candidate info
- Redis queue for fallback/retry
- JSON logging for monitoring

## Setup

1. `cp .env.example .env` and fill secrets
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`

## 🌐 Deployed on Render

The AI Mock Interviewer backend is live and accessible via Render.

### ✅ Live API Endpoint
https://ai-interviewer-v1.onrender.com

Check FastAPI:
https://ai-interviewer-v1.onrender.com/

OpenAPI Docs:
https://ai-interviewer-v1.onrender.com/scalar

See code for details.