---
title: Local Development Environment Setup
description: Step-by-step guide to set up the wm-hackathon local development environment on Windows and macOS, including Azure emulator fallbacks when Wipro Azure tenant access is unavailable.
author: GitHub Copilot
ms.date: 2026-04-28
ms.topic: how-to
keywords:
  - local development
  - azurite
  - cosmos db emulator
  - docker compose
  - dev setup
---

## Prerequisites

Install the following tools before proceeding.

| Tool | Version | Windows | macOS |
|------|---------|---------|-------|
| Git | any | <https://git-scm.com> | `brew install git` |
| Python | ≥ 3.12 | <https://python.org/downloads> | `brew install python@3.12` |
| Node.js | ≥ 20 LTS | <https://nodejs.org> | `brew install node@20` |
| Docker Desktop | latest | <https://docker.com/products/docker-desktop> | <https://docker.com/products/docker-desktop> |
| Azure CLI | ≥ 2.60 | `winget install Microsoft.AzureCLI` | `brew install azure-cli` |

> [!TIP]
> Docker Desktop must be running before you execute any `docker compose` commands.
> On Windows, confirm Docker is set to use the WSL 2 backend for best performance.

---

## Quick Start (with Docker)

This is the recommended path. All Azure storage and database services run locally via emulators.

### 1. Clone the repository and configure environment

**Windows (PowerShell):**

```powershell
git clone <repo-url>
cd wm-hackathon-main
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
git clone <repo-url>
cd wm-hackathon-main
cp .env.example .env
```

Open `.env` in your editor. For local emulator development, activate the emulator override
block at the bottom of the file (see [Configure .env for local emulators](#configure-env-for-local-emulators)).

### 2. Start the local emulators

```bash
docker compose up -d
```

This command starts two services:

| Service | What it emulates | Ports |
|---------|-----------------|-------|
| `azurite` | Azure Blob, Queue, and Table Storage | 10000, 10001, 10002 |
| `cosmos` | Azure Cosmos DB for NoSQL | 8081, 10251–10254 |

Wait for both services to become healthy before proceeding:

```bash
docker compose ps
```

Expected output when ready:

```text
NAME          STATUS
wm-azurite    Up (healthy)
wm-cosmos     Up (healthy)
```

> [!NOTE]
> The Cosmos DB emulator can take 60–90 seconds to initialize on first start.
> If its status shows `(health: starting)`, wait and re-run `docker compose ps`.

### 3. Initialize Blob Storage containers (one-time)

Create the two required Blob Storage containers in Azurite after first startup:

**Windows (PowerShell):**

```powershell
$conn = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;" +
        "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;" +
        "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

az storage container create --name supply-uploads  --connection-string $conn
az storage container create --name demand-uploads  --connection-string $conn
```

**macOS / Linux:**

```bash
CONN="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;\
AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;\
BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"

az storage container create --name supply-uploads  --connection-string "$CONN"
az storage container create --name demand-uploads  --connection-string "$CONN"
```

Alternatively, use **Azure Storage Explorer** (<https://azure.microsoft.com/features/storage-explorer/>)
connected to `http://127.0.0.1:10000` with the `devstoreaccount1` credentials.

### 4. Configure .env for local emulators

Open `.env` and enable the emulator override block. Replace the default Azure service entries
with the values below:

```ini
# --- Azure Storage (Azurite emulator) ---
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;
AZURE_STORAGE_SUPPLY_CONTAINER=supply-uploads
AZURE_STORAGE_DEMAND_CONTAINER=demand-uploads

# --- Azure Cosmos DB (local emulator) ---
AZURE_COSMOS_ENDPOINT=https://localhost:8081
AZURE_COSMOS_KEY=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b5nOH4Vz/6tZGyw==
AZURE_COSMOS_DATABASE=matching-results
AZURE_COSMOS_CONTAINER=results
AZURE_COSMOS_DISABLE_SSL_VERIFY=true

# --- Auth (bypass for local dev) ---
AUTH_BYPASS_DEV=true
```

> [!IMPORTANT]
> `AZURE_COSMOS_DISABLE_SSL_VERIFY=true` disables TLS certificate verification for the
> Cosmos DB emulator's self-signed certificate. Use this setting **only** in local development.
> Never set this in staging or production environments.

> [!NOTE]
> Azure AI Search has no official local emulator. Leave `AZURE_SEARCH_ENDPOINT` blank.
> The matching and indexing layers will fall back to mock/no-op behaviour during local
> development, allowing you to work on ingestion, API, and UI without a live search index.

### 5. Install Python dependencies

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

If `pip install -e ".[dev]"` fails due to setuptools version constraints, install packages directly:

```powershell
pip install fastapi "uvicorn[standard]" pydantic httpx pytest pytest-asyncio ruff mypy
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 6. Install frontend dependencies

```bash
cd src/ui
npm install
cd ../..
```

### 7. Run the backend API

```bash
uvicorn src.api.main:app --reload --port 8000
```

The API is available at <http://localhost:8000>.
OpenAPI (Swagger UI) docs are at <http://localhost:8000/docs>.

### 8. Run the frontend

Open a second terminal (with the virtual environment activated):

```bash
cd src/ui
npm run dev
```

The UI is available at <http://localhost:3000>.

### 9. Verify the setup

Run the unit tests to confirm everything is wired correctly:

```bash
python -m pytest tests/unit -v
```

Expected result: all tests pass.

```bash
python -m ruff check src tests
```

Expected result: no linting errors.

---

## Cosmos DB Emulator — TLS Certificate

The Cosmos DB emulator uses a self-signed certificate that causes SDK connection errors unless
you either trust the certificate or disable SSL verification.

### Option A — Disable SSL verification (simplest, local dev only)

Set `AZURE_COSMOS_DISABLE_SSL_VERIFY=true` in `.env` as shown in step 4 above.

### Option B — Trust the emulator certificate (recommended for team-wide use)

**Windows:**

```powershell
# Download the emulator certificate
Invoke-WebRequest -Uri "https://localhost:8081/_explorer/emulator.pem" `
  -OutFile "$env:TEMP\cosmos-emulator.pem" -SkipCertificateCheck

# Import into the Windows certificate store (requires admin)
Import-Certificate -FilePath "$env:TEMP\cosmos-emulator.pem" `
  -CertStoreLocation Cert:\LocalMachine\Root
```

**macOS:**

```bash
# Download the emulator certificate
curl -fsk https://localhost:8081/_explorer/emulator.pem -o /tmp/cosmos-emulator.pem

# Add to the macOS system keychain (requires sudo)
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain /tmp/cosmos-emulator.pem
```

After trusting the certificate you can remove `AZURE_COSMOS_DISABLE_SSL_VERIFY` from `.env`.

---

## Stopping and Resetting Emulators

| Action | Command |
|--------|---------|
| Stop emulators (keep data) | `docker compose down` |
| Stop and delete all data | `docker compose down -v` |
| Restart a single service | `docker compose restart azurite` |
| View emulator logs | `docker compose logs -f` |

---

## Manual Setup (without Docker)

Use this path when Docker Desktop is unavailable.

### Azurite — npm global install

```bash
npm install -g azurite
azurite --blobHost 0.0.0.0 --queueHost 0.0.0.0 --tableHost 0.0.0.0 --location ./azurite-data
```

Azurite will listen on ports 10000, 10001, 10002. Apply the same `.env` connection string
from [step 4](#4-configure-env-for-local-emulators).

### Cosmos DB emulator — Windows only

Download the Windows installer from:
<https://aka.ms/cosmosdb-emulator>

Install and launch the emulator. It starts automatically on port 8081 at `https://localhost:8081`.
Apply the same `AZURE_COSMOS_ENDPOINT` and `AZURE_COSMOS_KEY` values from step 4.

> [!NOTE]
> The Cosmos DB Windows emulator is not available on macOS. On macOS without Docker,
> use the Docker-based emulator path described in [Quick Start](#quick-start-with-docker).

---

## Connecting to the Wipro Azure Dev Environment

When Wipro Azure tenant access is available, populate `.env` with real Azure service values
instead of the emulator overrides:

| Variable | Where to find it |
|----------|-----------------|
| `AZURE_TENANT_ID` | Azure Portal → Microsoft Entra ID → Overview |
| `AZURE_CLIENT_ID` | Azure Portal → App Registrations → your app → Overview |
| `AZURE_CLIENT_SECRET` | Azure Portal → App Registrations → your app → Certificates & secrets |
| `AZURE_STORAGE_ACCOUNT_NAME` | Azure Portal → Storage Account → Overview |
| `AZURE_SEARCH_ENDPOINT` | Azure Portal → AI Search service → Overview |
| `AZURE_OPENAI_ENDPOINT` | Azure Portal → Azure OpenAI resource → Overview |
| `AZURE_COSMOS_ENDPOINT` | Azure Portal → Cosmos DB account → Overview |

Leave `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_COSMOS_KEY` blank when using Azure — the
application authenticates via `DefaultAzureCredential` (managed identity or Azure CLI login).

Log in with the Azure CLI to enable `DefaultAzureCredential` locally:

```bash
az login --tenant <your-tenant-id>
```

---

## Troubleshooting

### "docker compose up" fails with port conflict

Another process is already using ports 10000, 8081, or similar. Find and stop it:

**Windows (PowerShell):**

```powershell
netstat -ano | Select-String "10000"
Stop-Process -Id <PID> -Force
```

**macOS / Linux:**

```bash
lsof -i :10000
kill -9 <PID>
```

### Cosmos DB emulator stays unhealthy for more than 2 minutes

This is normal on first pull — the emulator image is large and initialization takes time.
Check the container log for progress:

```bash
docker compose logs cosmos
```

If it remains stuck, try a full reset:

```bash
docker compose down -v
docker compose up -d
```

### "pytest: command not found" on Windows

Use the module invocation instead:

```powershell
python -m pytest tests/unit -v
```

### Azure SDK errors connecting to Azurite

Confirm `AZURE_STORAGE_CONNECTION_STRING` in `.env` points to `127.0.0.1` (not `azurite`).
The hostname `azurite` is only reachable inside the Docker network; from the host machine,
use the loopback address.

### Azurite containers missing after docker compose down -v

The `-v` flag removes the named volumes, which deletes all persisted data.
Re-run the container initialization commands from [step 3](#3-initialize-blob-storage-containers-one-time).
