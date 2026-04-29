---
title: wm-hackathon
description: Intelligent Demand-Supply Matching — Wipro Hackathon. Matches open talent demand records against the internal supply pool using Azure AI Search and Azure OpenAI embeddings.
author: GitHub Copilot
ms.date: 2026-04-28
ms.topic: overview
---

Intelligent Demand-Supply Matching — Wipro Hackathon. Matches open talent demand records against the internal supply pool using Azure AI Search and Azure OpenAI embeddings.

## Repository Structure

```text
src/
  ingestion/          # Supply & Demand Excel parsers (SP1-001, SP1-002)
  indexing/           # Event handlers for profile and JD events (SP1-004 → SP1-006, SP2-007)
  matching/           # Vectorization + retrieval engine (SP2-001 → SP2-008)
  api/                # Backend REST API — FastAPI (SP0-005)
  ui/                 # Phase 1 frontend — React + TypeScript (SP0-006, SP3-004, SP3-005)
  evaluation/         # Evaluation framework — precision, recall, MRR (SP4-001)
tests/
  unit/               # Fast, isolated unit tests
  integration/        # End-to-end tests requiring Azure services
docs/
  schemas/            # Locked Excel Dump schemas (SP0-001)
  sprints/            # Sprint plan and backlog
  brds/               # Business Requirements Document
  prds/               # Product Requirements Document
infra/                # Bicep / ARM templates for Azure resources (SP0-002)
  docker/             # Container image definitions
.github/
  workflows/
    ci.yml            # CI: lint + unit tests on every PR
    cd.yml            # CD: build + deploy to dev on merge to main
```

## Schema Documentation

Confirmed Excel Dump schemas are locked and documented in [`docs/schemas/`](docs/schemas/):

| Document | Description |
|----------|-------------|
| [`docs/schemas/supply-schema.md`](docs/schemas/supply-schema.md) | Supply schema — `Employee Data` sheet (8,335 employee records) |
| [`docs/schemas/demand-schema.md`](docs/schemas/demand-schema.md) | Demand schema — `Demand OIR Data` sheet (21 open demand records) |

> Source file: `context/Consolidated Demand Supply Data with JD.xlsx`
> Locked: 2026-04-28 · SP0-001 complete · OQ-03 resolved

## Local Development Setup

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | ≥ 3.12 | <https://python.org> |
| Node.js | ≥ 20 | <https://nodejs.org> |
| Docker Desktop | latest | <https://docker.com> |

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd wm-hackathon-main
cp .env.example .env
# Edit .env — fill in Azure service endpoints and credentials
```

### 2. Install Python dependencies

```bash
# Install runtime + dev extras directly into your active Python environment
pip install fastapi "uvicorn[standard]" pydantic httpx pytest pytest-asyncio
```

> **Virtual environment (recommended for isolation)**
>
> ```bash
> python -m venv .venv
> # Windows
> .venv\Scripts\activate
> # macOS / Linux
> source .venv/bin/activate
> pip install fastapi "uvicorn[standard]" pydantic httpx pytest pytest-asyncio
> ```
>
> `pip install -e ".[dev]"` requires setuptools ≥ 68 with `build_editable` support.
> If your Python is 3.14 and that command fails, use the explicit package list above.

### 3. Install frontend dependencies

```bash
cd src/ui
npm install
cd ../..
```

### 4. Run the backend API (dev mode)

```bash
uvicorn src.api.main:app --reload --port 8000
```

API is available at <http://localhost:8000>.
Interactive OpenAPI docs (Swagger UI) are at <http://localhost:8000/docs>.
Alternative ReDoc UI is at <http://localhost:8000/redoc>.

The static OpenAPI contract is committed to [`docs/api/openapi.yaml`](docs/api/openapi.yaml).

**Available stub endpoints (Sprint 0)**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/demands` | List all open demand records |
| `POST` | `/demands` | Submit a new demand record |
| `GET` | `/demands/{id}/matches` | Ranked match results (page 1 = above-threshold, page 2+ = below-threshold) |
| `GET` | `/supply` | List available supply profiles |
| `POST` | `/events/profile` | Accept a profile add / update / delete event (returns 202) |
| `POST` | `/events/jd` | Accept a JD add / modify / delete event (returns 202) |

All endpoints require an Azure AD bearer token. In dev, the token check is bypassed by default.
To disable the bypass and require a real token, set `AUTH_BYPASS_DEV=false` in your environment.

### 5. Run the frontend (dev mode)

```bash
cd src/ui
npm run dev
```

UI is available at <http://localhost:3000>.

### 6. Run tests

```bash
# Run all unit tests
python -m pytest tests/unit -v

# Run a specific test file
python -m pytest tests/unit/test_api_stubs.py -v

# Linting (requires ruff)
python -m ruff check src tests

# Type check (requires mypy)
python -m mypy src
```

> **Windows note:** if `pytest` is not on your `PATH`, use `python -m pytest` as shown above.

Expected output for a clean run:

```text
16 passed, 1 warning in ~1s
```

### Local emulators (when Azure access is not available)

Full local emulator setup (Azurite, Cosmos DB emulator, docker-compose) is documented in [`docs/infra/dev-setup.md`](docs/infra/dev-setup.md) — delivered in SP0-007.

## CI / CD

| Trigger | Pipeline | Actions |
|---------|----------|---------|
| Pull request to `main` | `.github/workflows/ci.yml` | ruff lint, mypy, pytest unit tests, ESLint, frontend build |
| Merge to `main` | `.github/workflows/cd.yml` | Build containers, push to ACR, deploy to dev Azure Container Apps |

> **Branch protection:** Require at least one review approval and passing CI before merging to `main`. Configure in GitHub → Settings → Branches.

## Key Documents

| Document | Path |
|----------|------|
| Sprint Plan & Backlog | [`docs/sprints/sprint-plan.md`](docs/sprints/sprint-plan.md) |
| PRD | [`docs/prds/intelligent-demand-supply-matching-prd.md`](docs/prds/intelligent-demand-supply-matching-prd.md) |
| BRD | [`docs/brds/intelligent-talent-screening-brd.md`](docs/brds/intelligent-talent-screening-brd.md) |
| Supply Schema | [`docs/schemas/supply-schema.md`](docs/schemas/supply-schema.md) |
| Demand Schema | [`docs/schemas/demand-schema.md`](docs/schemas/demand-schema.md) |
