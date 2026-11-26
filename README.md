# CodePulse
    
**AI-Powered GitHub Repository Auditor**

CodePulse is an intelligent software auditing platform designed to analyze GitHub repositories, identify code quality issues, detect potential security vulnerabilities, evaluate software architecture, and generate AI-powered improvement recommendations.

## Project Objectives

- Automated repository analysis
- Code quality and maintainability assessment
- Security vulnerability detection
- Architecture and dependency analysis
- Performance issue identification
- AI-powered explanations and suggested fixes
- Comprehensive repository audit reports

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Driver | Psycopg |
| Database Migrations | Alembic |
| HTTP Client | Axios, HTTPX |
| Testing | Pytest |
| AI Integration (Planned) | Gemini API |
| Background Processing (Planned) | Celery, Redis |
| Containerization (Planned) | Docker |

## Project Structure

- `backend/` — Backend APIs, database and analysis engine.
- `frontend/` — React application.
- `docs/` — Technical documentation.
- `.env.example` — Environment configuration template.

## Local Development

### Backend Setup

1. Navigate to the backend directory.
2. Create and activate a Python virtual environment.
3. Install dependencies using `pip install -r requirements.txt`.
4. Copy the root `.env.example` file into `backend/.env`.
5. Configure PostgreSQL credentials.
6. Start the backend using `python -m uvicorn app.main:app --reload`.

### Frontend Setup

1. Navigate to the frontend directory.
2. Run `npm install`.
3. Copy `.env.example` to `.env`.
4. Run `npm run dev`.

## Application URLs

- Frontend: http://localhost:5173
- Backend: http://127.0.0.1:8000
- API Documentation: http://127.0.0.1:8000/docs

## Available APIs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Application information |
| GET | `/api/v1/health` | Backend health check |
| GET | `/api/v1/health/db` | Database health check |

## Development Roadmap

- [x] Phase 1 — Project Foundation
- [ ] Phase 2 — GitHub Repository Integration
- [ ] Phase 3 — Repository Intelligence
- [ ] Phase 4 — Code Quality Analyzer
- [ ] Phase 5 — Security Analyzer
- [ ] Phase 6 — Architecture and Performance Analysis
- [ ] Phase 7 — AI Recommendation Engine
- [ ] Phase 8 — Scan Orchestration and Persistence
- [ ] Phase 9 — Frontend Development
- [ ] Phase 10 — Testing and Deployment

## Security

CodePulse is designed to analyze untrusted repositories without executing their source code. Sensitive credentials must be stored in environment variables and must never be committed to version control.

## Project Status

Under active development.