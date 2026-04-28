---
title: Intelligent Demand-Supply Matching — Sprint Plan & Backlog
description: Sprint-by-sprint work item breakdown derived from PRD v0.3. Sprint 0 delivers a deployable skeleton application to enable parallel feature development across all subsequent sprints.
author: GitHub Copilot
ms.date: 2026-04-28
ms.topic: reference
keywords:
  - sprint plan
  - backlog
  - demand-supply matching
  - work items
  - wipro
---

## Sprint Overview

| Sprint   | Duration   | Theme                                  | Stories | Points | Gate Criteria                                                    |
|----------|------------|----------------------------------------|---------|--------|------------------------------------------------------------------|
| Sprint 0 | 2026-04-28 → 2026-05-09 | Foundation & Skeleton App | 10      | 34     | Deployable skeleton; all Azure resources provisioned; schema locked |
| Sprint 1 | 2026-05-12 → 2026-05-23 | Data Ingestion & Profile Indexing      | 9       | 40     | Supply & Demand ingestion live; profile index populated in AI Search |
| Sprint 2 | 2026-05-26 → 2026-06-06 | Matching Engine                        | 8       | 39     | Ranked top-10 results returned with similarity scores ≥70%       |
| Sprint 3 | 2026-06-09 → 2026-06-20 | Result Management & Phase 1 UI         | 8       | 37     | Phase 1 UI live; JD events wired end-to-end; caching functional  |
| Sprint 4 | 2026-06-23 → 2026-07-04 | Evaluation, Security & Handoff         | 10      | 42     | Evaluation report delivered; security review passed; handoff done |

**Total:** 45 stories · 192 points · ~10 weeks

---

## Epics

| Epic ID | Name                             | Sprints  | PRD Coverage                              |
|---------|----------------------------------|----------|-------------------------------------------|
| E-01    | Foundation & Infrastructure      | S0       | NFR-002, NFR-004, NFR-005, NFR-009        |
| E-02    | Data Ingestion                   | S0, S1   | FR-009, FR-010, NFR-007, NFR-008          |
| E-03    | Event-Driven Indexing            | S1, S3   | FR-011, FR-012                            |
| E-04    | Matching Engine                  | S2       | FR-001, FR-002, FR-003, FR-004, FR-005, FR-006 |
| E-05    | Result Management                | S3       | FR-004, FR-013, FR-014                    |
| E-06    | Phase 1 UI                       | S0, S3   | FR-007, FR-006                            |
| E-07    | Evaluation Framework             | S4       | FR-015, FR-016, G-005                     |
| E-08    | Security & Compliance            | S0, S4   | NFR-005, NFR-006, NFR-009                 |
| E-09    | Monitoring & Operations          | S4       | NFR-003, NFR-004                          |

---

## Definition of Done

Every story is done when all of the following are true:

* Code merged to main via pull request with at least one reviewer approval.
* Unit tests written and passing; coverage meets team threshold.
* No high or critical security vulnerabilities introduced.
* Acceptance criteria verified by a team member other than the author.
* Relevant documentation (README, API contract, or ADR) updated.
* No real employee PII present in dev/test environments.

---

## Sprint 0: Foundation & Skeleton App

**Goal:** Deliver a fully deployable skeleton application with all Azure resources provisioned, real event wiring in place (stub handlers), a mock API layer, and a scaffold UI. By end of Sprint 0, every feature stream (ingestion, matching, UI, evaluation) can operate in parallel against real infrastructure without waiting for other teams.

**Parallelization unlocked after Sprint 0:**

* Team A (Ingestion) works on Supply and Demand parsers against real Blob Storage containers.
* Team B (Matching) builds the vectorization and retrieval logic against a real AI Search index schema.
* Team C (UI) develops Phase 1 screens against mock API endpoints returning synthetic data.
* Team D (Evaluation) prepares the test harness and synthetic labelled dataset.

---

### SP0-001 · Lock and Document Excel Dump Schemas

**Epic:** E-02 | **Type:** Spike | **Points:** 3 | **Owner:** Rupali Agarwal / Dev

As a developer, I want confirmed column names, data types, and sample values for both the Supply and Demand Excel Dump files so that all ingestion and vectorization work proceeds against a stable, known schema.

**Acceptance Criteria:**

* Supply schema document confirmed and committed: Employee ID (anon), skills, designation, location, experience band, project history, availability — with exact column names and data types.
* Demand schema document confirmed and committed: Demand ID, role title, required skills, location, experience band, business unit — with exact column names and data types.
* Schema document stored in `docs/schemas/` and referenced in the project README.
* Any ambiguous or optional columns flagged explicitly.
* OQ-03 (column names) resolved and closed.

**Dependencies:** None — this is the first critical path item. Blocks SP0-004, SP1-001, SP1-002.

---

### SP0-002 · Provision Azure Development Infrastructure

**Epic:** E-01 | **Type:** Task | **Points:** 5 | **Owner:** ISE / Wipro Infra

As the development team, I want all required Azure services provisioned in the dev environment so that every team member can connect to real infrastructure from day one.

**Acceptance Criteria:**

* Azure Blob Storage account created with two containers: `supply-uploads` and `demand-uploads`.
* Azure AI Search service provisioned at a tier supporting ≥150,000 vectors (confirm S1 or higher); index schema created with all supply attribute fields plus a vector field (empty, no data yet).
* Search Result DB (Azure Cosmos DB) provisioned; database and collection created with the planned result schema (demand ID, employee ID, similarity score, rank, timestamp).
* Azure Event Grid configured with blob-created and blob-updated triggers on both containers (events routed to stub handlers).
* All services deployed to Wipro Azure tenant; zero external cloud dependencies.
* Connection strings and managed identity roles documented in `docs/infra/dev-setup.md`.

**Dependencies:** SP0-001 (schema needed to define AI Search index fields).

---

### SP0-003 · Initialize Repository, Project Scaffold & CI/CD Pipeline

**Epic:** E-01 | **Type:** Task | **Points:** 5 | **Owner:** ISE Dev Lead

As the team, I want a well-structured repository with a working CI/CD pipeline so that every team member can build, test, and deploy from the first day of Sprint 1.

**Acceptance Criteria:**

* Repository initialized with the following top-level structure:

  ```text
  src/
    ingestion/          # Supply & Demand Excel parsers
    indexing/           # Event handlers for profile and JD events
    matching/           # Vectorization + retrieval engine
    api/                # Backend REST API (FastAPI or equivalent)
    ui/                 # Phase 1 frontend application
    evaluation/         # Evaluation framework
  tests/
    unit/
    integration/
  docs/
  infra/                # Bicep / ARM templates for Azure resources
  ```

* CI pipeline runs on every pull request: lint, unit tests, build.
* CD pipeline deploys to dev environment on merge to main.
* Branch protection: main requires at least one review and passing CI.
* README includes local dev setup instructions.

**Dependencies:** None.

---

### SP0-004 · Generate Anonymized Synthetic Dataset

**Epic:** E-02 | **Type:** Task | **Points:** 3 | **Owner:** Dev team

As a developer, I want a realistic synthetic dataset for both Supply and Demand in the confirmed Excel Dump format so that all feature teams can develop and test against representative data without real employee PII.

**Acceptance Criteria:**

* Synthetic Supply Excel Dump generated with ≥1,000 rows (scalable script to generate 150,000).
* Synthetic Demand Excel Dump generated with ≥20 rows covering varied role types, locations, and experience bands.
* All Employee IDs are anonymized (e.g., `EMP-00001`); no real names, emails, or PII.
* Intentionally sparse rows included (≥10% of supply records have 1–2 missing fields) to validate NFR-007.
* Intentionally incomplete demand records included (below 70% completeness) to validate NFR-008.
* Dataset committed to `tests/fixtures/` and uploaded to Blob Storage dev containers.

**Dependencies:** SP0-001 (schema must be locked before generation).

---

### SP0-005 · Create Skeleton Backend API with Stub Endpoints

**Epic:** E-06 | **Type:** Task | **Points:** 5 | **Owner:** Dev team

As the UI team, I want a running backend API with stub endpoints for every planned route so that I can build the Phase 1 UI without waiting for the real matching engine.

**Acceptance Criteria:**

* API service scaffolded (Python FastAPI recommended) and deployable to dev environment.
* The following endpoints exist and return HTTP 200 with mock JSON payloads:
  * `GET /demands` — returns a list of mock open demand records.
  * `GET /demands/{demand_id}/matches` — returns a mock ranked top-10 list of supply profiles with similarity scores.
  * `GET /demands/{demand_id}/matches?page=2` — returns next batch (pagination stub).
  * `POST /events/profile` — accepts profile change event payload; logs and returns 202.
  * `POST /events/jd` — accepts JD change event payload; logs and returns 202.
  * `GET /health` — returns service status.
* API contract (OpenAPI spec) committed to `docs/api/`.
* Azure AD authentication middleware present but configured in bypass mode for dev.

**Dependencies:** SP0-003.

---

### SP0-006 · Create Skeleton Frontend Application

**Epic:** E-06 | **Type:** Task | **Points:** 5 | **Owner:** Dev team (UI)

As a Talent Lead or Hiring Manager, I want a navigable application scaffold with placeholder screens so that the UI team can develop the Phase 1 views iteratively against the mock API.

**Acceptance Criteria:**

* Frontend application scaffolded (React + TypeScript recommended) and deployable to dev environment.
* Two navigable screens exist with placeholder content:
  * Open Demands list screen — shows a table of mock demand records.
  * Demand Match Results screen — shows a ranked list of mock employee profiles with a numeric similarity score badge per row.
* Application connects to the skeleton backend API (SP0-005) and renders the mock responses.
* Routing, layout, and component structure established so Sprint 3 UI stories can build on top without restructuring.
* Application builds successfully in CI.

**Dependencies:** SP0-003, SP0-005.

---

### SP0-007 · Configure Local Development Environment

**Epic:** E-01 | **Type:** Task | **Points:** 2 | **Owner:** Dev Lead

As a developer, I want a documented local dev setup that works with Azure emulators as fallback so that I can develop and test even when Wipro Azure tenant access is delayed.

**Acceptance Criteria:**

* `docs/infra/dev-setup.md` provides step-by-step instructions for Windows and macOS.
* Azurite (Azure Storage emulator) configured as fallback for Blob Storage.
* Local Cosmos DB emulator configured as fallback for Search Result DB.
* `docker-compose.yml` starts all local emulators with a single command.
* Environment variable template (`.env.example`) committed for all connection strings; `.env` in `.gitignore`.
* At least two team members verify the setup works end-to-end on their machines.

**Dependencies:** SP0-003.

---

### SP0-008 · Define and Commit System ADR for Architecture Decisions

**Epic:** E-01 | **Type:** Spike | **Points:** 2 | **Owner:** ISE / Dev Lead

As the team, I want a lightweight Architecture Decision Record (ADR) capturing key design choices so that every team member builds consistently and future maintainers understand the rationale.

**Acceptance Criteria:**

* ADR committed to `docs/adr/` covering:
  * Embedding model selection (Azure OpenAI text-embedding-3-large or equivalent) and rationale.
  * Retrieval strategy default (hybrid: dense + sparse BM25) with switchability requirement per NFR-010.
  * Search Result DB choice (Cosmos DB) with justification.
  * Event trigger mechanism (Azure Event Grid vs. Blob Trigger Function) and decision rationale.
  * Authentication approach (Azure AD managed identity) per NFR-009.
* ADR reviewed and signed off by Shinoj Zacharias.

**Dependencies:** SP0-002.

---

### SP0-009 · Define Similarity Score Schema and Caching Key Contract

**Epic:** E-04, E-05 | **Type:** Spike | **Points:** 2 | **Owner:** Dev Lead

As the matching and result management teams, I want a documented contract for the similarity score structure and cache key format so that both teams can build independently in Sprint 2 and Sprint 3 without integration surprises.

**Acceptance Criteria:**

* Document committed to `docs/contracts/` specifying:
  * Similarity score format: float 0.0–1.0 internally, displayed as integer 0–100% in UI.
  * Per-attribute score breakdown (skills, designation, location, experience band, project history) — optional for Phase 1 display but computed internally.
  * Composite score formula or weighting approach (or explicit statement that weights are equal pending future tuning).
  * Cache key schema: `{demand_id}:{supply_index_version}`.
  * Cache invalidation trigger events: JD Modify, JD Delete.
* Document reviewed by Anshuman Bhadauria.

**Dependencies:** SP0-001.

---

### SP0-010 · Set Up Security Baseline (Dev Environment)

**Epic:** E-08 | **Type:** Task | **Points:** 2 | **Owner:** Dev Lead / ISE Security

As the team, I want a security baseline in place from day one so that no insecure patterns are established early and later difficult to remove.

**Acceptance Criteria:**

* Azure AD App Registration created for the backend API; all endpoints require a valid bearer token.
* Managed identity assigned to all Azure services (AI Search, Cosmos DB, Blob Storage) — no connection strings or API keys stored in code.
* RBAC roles assigned: ingestion pipeline has Storage Blob Data Reader; matching engine has Search Index Data Reader; API has Cosmos DB data contributor.
* Dependency scanning (e.g., `pip-audit` or `npm audit`) added to CI pipeline; build fails on critical vulnerabilities.
* `.gitignore` prevents secrets, `.env` files, and key files from being committed.

**Dependencies:** SP0-002, SP0-003.

---

## Sprint 1: Data Ingestion & Event-Driven Profile Indexing

**Goal:** Implement the full data ingestion path for both Supply and Demand datasets, and wire all three profile change events (add, update, delete) to the AI Search index. By end of Sprint 1, the supply index is populated with vectorized profiles, and demand records are parsed and ready for matching.

**Parallel tracks within this sprint:**

* Track A: Supply ingestion + profile vectorization + profile event handlers (SP1-001, SP1-003, SP1-004, SP1-005, SP1-006).
* Track B: Demand ingestion + demand completeness validation + sparse data handling (SP1-002, SP1-007, SP1-008).

---

### SP1-001 · Implement Supply Excel Dump Reader and Row Parser

**Epic:** E-02 | **Type:** Feature | **Points:** 5 | **Owner:** Team A

As the system, I want to read Supply Excel Dump files from Azure Blob Storage and parse each row into a typed supply profile object so that profiles are available for vectorization.

**Acceptance Criteria:**

* Supply Excel Dump read from the `supply-uploads` Blob Storage container without manual intervention.
* Each row parsed into a `SupplyProfile` model with all confirmed schema fields (SP0-001).
* Parser is schema-validated: if a required column is missing from the file, an error is raised and logged; missing per-row values are set to null rather than causing an exception.
* At least 1,000 synthetic supply records (SP0-004) parsed without error.
* Intentionally sparse rows (missing 1–2 fields) parsed successfully, returning valid `SupplyProfile` objects with null fields.
* Unit tests covering: valid full row, sparse row (2 missing fields), completely empty row, malformed file.

**Dependencies:** SP0-001, SP0-004, SP0-002.

---

### SP1-002 · Implement Demand Excel Dump Reader and Row Parser

**Epic:** E-02 | **Type:** Feature | **Points:** 5 | **Owner:** Team B

As the system, I want to read Demand Excel Dump files from Azure Blob Storage and parse each row into a typed demand record object so that demand records are available for completeness validation and matching.

**Acceptance Criteria:**

* Demand Excel Dump read from the `demand-uploads` Blob Storage container without manual intervention.
* Each row parsed into a `DemandRecord` model with all confirmed schema fields (SP0-001).
* Schema validation as per SP1-001: missing required file columns raise an error; missing per-row values set to null.
* At least 20 synthetic demand records (SP0-004) parsed without error.
* Unit tests covering: valid full row, row with 2 missing fields, completely empty row, malformed file.

**Dependencies:** SP0-001, SP0-004, SP0-002.

---

### SP1-003 · Implement Supply Profile Vectorization

**Epic:** E-03 | **Type:** Feature | **Points:** 8 | **Owner:** Team A

As the system, I want to convert a parsed supply profile into a single embedding vector using Azure OpenAI so that profiles can be stored in the AI Search index and queried semantically.

**Acceptance Criteria:**

* `SupplyProfile` fields concatenated into a structured text representation before embedding (e.g., `"Skills: Python, Azure. Role: Senior Engineer. Location: Bangalore. Experience: 8 years."`).
* Vectorization calls Azure OpenAI Embeddings API (text-embedding-3-large or confirmed model) via managed identity — no API keys in code.
* Null fields in the profile are omitted from the text representation; at least one populated field produces a valid vector.
* Vectorization function is deterministic for the same input.
* Batch vectorization supported (process multiple profiles per API call) to minimize latency and token cost.
* Unit tests covering: full profile, sparse profile (1 field), all-null profile raises a `InsufficientDataError`.
* Integration test: 100 synthetic profiles vectorized and dimensions verified against the expected model output dimension.

**Dependencies:** SP1-001, SP0-002 (Azure OpenAI endpoint), SP0-008 (embedding model ADR).

---

### SP1-004 · Implement Profile Added Event Handler → AI Search Index

**Epic:** E-03 | **Type:** Feature | **Points:** 5 | **Owner:** Team A

As the system, when a new supply profile is added to Blob Storage, I want the profile vectorized and added to the AI Search index so that the profile is immediately eligible for matching.

**Acceptance Criteria:**

* Azure Blob Storage trigger (Event Grid) fires on new file in `supply-uploads` container.
* Handler parses the new profile row (SP1-001), vectorizes it (SP1-003), and upserts the vector document into the AI Search index.
* Profile is retrievable from the AI Search index within 30 seconds of the blob upload.
* If vectorization fails, the event is sent to a dead-letter queue (not silently dropped).
* Idempotent: re-processing the same event produces the same index state.
* Integration test: upload a synthetic profile blob → verify profile appears in AI Search index.

**Dependencies:** SP1-003, SP0-002, SP0-010.

---

### SP1-005 · Implement Profile Updated Event Handler → AI Search Re-index

**Epic:** E-03 | **Type:** Feature | **Points:** 3 | **Owner:** Team A

As the system, when an existing supply profile is updated in Blob Storage, I want the profile re-vectorized and the AI Search index entry updated so that matching reflects the latest profile data.

**Acceptance Criteria:**

* Azure Blob Storage trigger fires on blob overwrite for an existing supply profile.
* Handler parses the updated row, re-vectorizes, and upserts the document in the AI Search index (using the employee ID as the document key).
* The updated vector replaces the old vector; no duplicate entries created.
* Old vector is not queryable after the update completes.
* Integration test: upload updated profile → verify AI Search returns the updated skills in a semantic query.

**Dependencies:** SP1-004.

---

### SP1-006 · Implement Profile Deleted Event Handler → AI Search Removal

**Epic:** E-03 | **Type:** Feature | **Points:** 3 | **Owner:** Team A

As the system, when a supply profile is deleted from Blob Storage, I want the corresponding document removed from the AI Search index so that deleted employees are never returned in match results.

**Acceptance Criteria:**

* Blob delete event triggers the handler.
* Handler deletes the document with the matching employee ID from the AI Search index.
* After deletion, querying the AI Search index with the deleted employee's attributes does not return that employee.
* Idempotent: deleting an already-absent document does not raise an error.
* Integration test: add a profile → delete it → verify it does not appear in AI Search.

**Dependencies:** SP1-004.

---

### SP1-007 · Implement Demand Completeness Validation

**Epic:** E-02 | **Type:** Feature | **Points:** 3 | **Owner:** Team B

As the system, I want demand records below 70% field completeness rejected before matching so that the matching engine never processes underspecified roles that would produce meaningless results.

**Acceptance Criteria:**

* Completeness score computed as `(populated_fields / total_defined_fields) × 100`.
* Demand records with completeness score < 70% are rejected with an `IncompleteDemandError` containing the demand ID and computed score.
* Rejected records are logged with their completeness score; they are not passed to the matching pipeline.
* Valid demand records (≥70% completeness) pass through unchanged.
* Unit tests: 100% complete demand, exactly 70% complete demand (accepted), 69% complete demand (rejected), empty demand (rejected).

**Dependencies:** SP1-002.

---

### SP1-008 · Implement Sparse Supply Profile Handling

**Epic:** E-02 | **Type:** Feature | **Points:** 3 | **Owner:** Team A

As the system, I want supply profiles with missing fields to produce valid (non-zero, non-error) similarity scores so that sparse profiles are evaluated rather than silently excluded from results.

**Acceptance Criteria:**

* Supply profile with only one populated attribute (e.g., skills only) produces a valid vector and a non-zero similarity score when matched against a demand record.
* No exception thrown for profiles with any combination of missing fields.
* Similarity score for a sparse profile is lower than an equivalent fully populated profile for the same query (confirmed via test).
* Unit tests: profile with all fields, profile with 1 field, profile with all fields null (raises `InsufficientDataError`).

**Dependencies:** SP1-003.

---

### SP1-009 · End-to-End Ingestion Integration Test

**Epic:** E-02, E-03 | **Type:** Task | **Points:** 5 | **Owner:** Team A + B

As the team, I want an automated integration test that exercises the full ingestion flow from blob upload to indexed profile so that we can validate the pipeline before Sprint 2 begins.

**Acceptance Criteria:**

* Test uploads 1,000 synthetic supply profiles to `supply-uploads` and 20 synthetic demand records to `demand-uploads`.
* Test verifies: all 1,000 supply profiles appear in AI Search index; all demand records parsed without error; sparse profiles indexed with valid vectors.
* Test verifies rejected demand records (below 70% completeness) are not passed downstream.
* Test runs in CI as part of the integration test suite.
* Test completes in under 5 minutes.

**Dependencies:** SP1-001 through SP1-008.

---

## Sprint 2: Matching Engine

**Goal:** Implement the core semantic matching engine that queries the AI Search index for a demand record and returns a ranked, similarity-scored, threshold-filtered shortlist. All three retrieval strategies (dense, sparse, hybrid) are implemented to enable the Sprint 4 evaluation framework.

**Parallel tracks within this sprint:**

* Track A: Dense retrieval, score computation, threshold, and ranking (SP2-001 through SP2-005).
* Track B: JD vectorization + New JD event handler (SP2-006, SP2-007) — requires Track A score contract.
* Track C: Sparse and hybrid strategy implementations (SP2-008) — depends only on the retrieval interface defined in SP2-001.

---

### SP2-001 · Implement Dense Semantic Retrieval Against AI Search

**Epic:** E-04 | **Type:** Feature | **Points:** 8 | **Owner:** Team B

As the system, I want to query the vectorized supply profile index using a demand record's embedding vector so that semantically similar profiles are retrieved even when exact keyword matches are absent.

**Acceptance Criteria:**

* Demand record fields are serialized into the same structured text format used for supply profiles (SP1-003) and vectorized using the same embedding model.
* Vectorized demand query submitted to Azure AI Search using the vector search (ANN/HNSW) API.
* Query evaluates all indexed supply profiles — no pre-filter excludes records unless the filter is an explicit requirement (e.g., location hard-filter if required by demand record).
* Raw retrieval returns the top-N candidates (configurable, default 50) with their AI Search similarity scores.
* Unit tests: mock AI Search returns expected candidates in expected order.
* Integration test against the dev AI Search index with 1,000 synthetic profiles.

**Dependencies:** SP1-003, SP1-009, SP0-009 (score schema).

---

### SP2-002 · Implement Similarity Score Normalization (0–100%)

**Epic:** E-04 | **Type:** Feature | **Points:** 3 | **Owner:** Team B

As the system, I want AI Search raw similarity scores normalized to a 0–100% integer scale so that Talent Leads and Hiring Managers see an intuitive, consistent score on every matched profile.

**Acceptance Criteria:**

* Raw cosine similarity scores (range -1 to 1, or 0 to 1 depending on model) mapped to 0–100 integer.
* Normalization formula documented and consistent across all retrieval strategies.
* Scores are reproducible: same demand-supply pair always produces the same normalized score.
* Score boundary tests: raw score 1.0 → 100, raw score 0.0 → 0, negative scores → 0 (not negative).
* Unit tests covering boundary values and mid-range values.

**Dependencies:** SP2-001.

---

### SP2-003 · Implement 70% Similarity Score Threshold Enforcement

**Epic:** E-04 | **Type:** Feature | **Points:** 2 | **Owner:** Team B

As the system, I want all supply profiles scoring below 70% similarity suppressed from results so that Talent Leads only see candidates who meaningfully match the role.

**Acceptance Criteria:**

* Any candidate with normalized score < 70 is excluded from the result set.
* Threshold value is configurable via environment variable (`MATCH_SCORE_THRESHOLD`, default 70) within the 70–80% range per FR-005.
* If zero candidates meet the threshold, the result set is empty (not an error).
* Unit tests: list with candidates above, at, and below threshold — verify only above/at-threshold candidates returned.

**Dependencies:** SP2-002.

---

### SP2-004 · Implement Ranked Top-10 Shortlist Generation

**Epic:** E-04 | **Type:** Feature | **Points:** 3 | **Owner:** Team B

As the system, I want the filtered candidates sorted by descending similarity score and truncated to the top 10 so that Talent Leads always receive a concise, prioritized shortlist.

**Acceptance Criteria:**

* Candidates passing the threshold are sorted by normalized score descending.
* Result set contains at most 10 candidates; if fewer than 10 pass the threshold, all passing candidates are returned.
* Each result item includes: employee ID, similarity score (0–100), rank (1–10), and all supply profile attributes.
* Results are deterministic for the same input (tie-breaking by employee ID ascending).
* Unit tests: 15 candidates above threshold → returns top 10 in correct order; 5 candidates above threshold → returns all 5; 0 above threshold → returns empty list.

**Dependencies:** SP2-003.

---

### SP2-005 · Implement Multi-Attribute Simultaneous Matching

**Epic:** E-04 | **Type:** Feature | **Points:** 5 | **Owner:** Team B

As the system, I want matching to consider skills, role/designation, location, experience band, and project history simultaneously so that the composite similarity score reflects all relevant attributes rather than skills alone.

**Acceptance Criteria:**

* Supply profile embedding is generated from the concatenated representation of all five attributes (skills, designation, location, experience band, project history).
* Demand record embedding is generated from the corresponding required attributes.
* Ablation test confirms that a profile with matching skills but mismatched location scores lower than a profile matching on all five attributes.
* Ablation test confirms that each attribute contributes to the composite score (removing one attribute changes the score).
* Integration test: two synthetic supply profiles — one matching on skills only, one matching on all attributes — confirm the all-attribute match scores higher.

**Dependencies:** SP2-001, SP2-002, SP1-003 (embedding format).

---

### SP2-006 · Implement JD Vectorization

**Epic:** E-03 | **Type:** Feature | **Points:** 3 | **Owner:** Team B

As the system, I want demand (JD) records vectorized and stored in a dedicated JD Index so that JD embeddings are persisted and available for matching without re-computing on every query.

**Acceptance Criteria:**

* `DemandRecord` fields serialized into a structured text representation and vectorized using the same embedding model as supply profiles.
* Vectorized JD stored in the JD Index (separate AI Search index or Cosmos DB collection — per ADR SP0-008).
* JD Index document keyed by demand ID.
* Re-vectorizing the same demand record produces the same vector.
* Unit tests covering full demand record and sparse demand record (still above 70% completeness threshold).

**Dependencies:** SP2-005, SP1-007, SP0-009.

---

### SP2-007 · Implement New JD Event Handler → Vectorize → Match → Store Results

**Epic:** E-03, E-05 | **Type:** Feature | **Points:** 8 | **Owner:** Team B

As the system, when a new JD is published to Blob Storage, I want the end-to-end flow triggered automatically: vectorize the JD, store it in the JD Index, run matching against the full supply index, and persist the top-10 results in the Search Result DB so that results are pre-computed and ready to serve.

**Acceptance Criteria:**

* Blob add event on `demand-uploads` triggers the JD event handler.
* Handler: (1) parses the demand row, (2) validates completeness ≥70%, (3) vectorizes the JD (SP2-006), (4) runs dense retrieval against the full supply index (SP2-001), (5) applies threshold (SP2-003) and ranking (SP2-004), (6) persists the top-10 results to Search Result DB (schema per SP0-009).
* Results appear in Search Result DB within 60 seconds of blob upload.
* Handler is idempotent: re-processing the same new JD event produces the same Search Result DB state.
* Failed events go to dead-letter queue.
* Integration test: upload a synthetic demand blob → verify top-10 results appear in Search Result DB with correct schema.

**Dependencies:** SP2-001 through SP2-006, SP0-002 (Search Result DB).

---

### SP2-008 · Implement Sparse and Hybrid Retrieval Strategies

**Epic:** E-04 | **Type:** Feature | **Points:** 8 | **Owner:** Team B

As the evaluation framework, I want sparse (BM25/keyword) and hybrid (dense + sparse) retrieval strategies implemented behind the same interface as dense retrieval so that Sprint 4 can compare all three strategies on identical test data.

**Acceptance Criteria:**

* Retrieval strategy selectable via a configuration flag (`RETRIEVAL_STRATEGY`: `dense` | `sparse` | `hybrid`); switching requires no code change per NFR-010.
* Sparse strategy uses Azure AI Search BM25 full-text search over supply profile text fields.
* Hybrid strategy uses Azure AI Search hybrid query combining the vector query and the BM25 query with Reciprocal Rank Fusion (RRF).
* All three strategies implement the same `RetrievalStrategy` interface (same inputs, same output schema).
* Integration test: same demand query run with all three strategies against the same 1,000-profile index; results logged for comparison.

**Dependencies:** SP2-001, SP0-008 (ADR on hybrid strategy).

---

## Sprint 3: Result Management & Phase 1 UI

**Goal:** Complete the end-to-end JD event lifecycle (Modify and Delete), implement result caching and iterative retrieval, deliver a functional Phase 1 UI, and integrate the UI against the real matching API. By end of Sprint 3, a Talent Lead can open the app, browse open demands, select one, and see ranked matched supply profiles with real similarity scores.

**Parallel tracks within this sprint:**

* Track A: JD Modify/Delete event handlers + caching (SP3-001, SP3-002, SP3-003).
* Track B: Phase 1 UI development against mock API, then swap to real API (SP3-004, SP3-005, SP3-006).
* Track C: Iterative retrieval/pagination (SP3-007) — can run in parallel once SP2-004 is stable.

---

### SP3-001 · Implement JD Modify Event Handler

**Epic:** E-03 | **Type:** Feature | **Points:** 5 | **Owner:** Team A

As the system, when an existing JD is modified in Blob Storage, I want the old match results cleared from the Search Result DB, the JD re-vectorized, and matching re-run so that the stored results always reflect the current JD definition.

**Acceptance Criteria:**

* Blob overwrite event on an existing demand file triggers the JD Modify handler.
* Handler: (1) clears all existing match results for the demand ID from Search Result DB, (2) re-vectorizes the updated JD, (3) updates the JD Index document, (4) re-runs matching, (5) persists new top-10 results.
* Between clearing old results and storing new results, the API returns an empty or `MATCHING_IN_PROGRESS` response for the affected demand ID — not stale results.
* Integration test: upload a JD → modify it → verify Search Result DB contains only the new results and old results are gone.

**Dependencies:** SP2-007.

---

### SP3-002 · Implement JD Delete Event Handler

**Epic:** E-03 | **Type:** Feature | **Points:** 3 | **Owner:** Team A

As the system, when a JD is deleted from Blob Storage, I want the JD removed from the JD Index and all associated match results purged from the Search Result DB so that no orphaned results persist for deleted roles.

**Acceptance Criteria:**

* Blob delete event on a demand file triggers the JD Delete handler.
* Handler: (1) removes the JD document from the JD Index, (2) deletes all match result documents for the demand ID from Search Result DB.
* After deletion, `GET /demands/{demand_id}/matches` returns 404.
* Idempotent: deleting an already-absent JD does not raise an error.
* Integration test: upload a JD → delete it → verify JD Index and Search Result DB contain no data for that demand ID.

**Dependencies:** SP3-001.

---

### SP3-003 · Implement Result Caching and Cache Invalidation

**Epic:** E-05 | **Type:** Feature | **Points:** 5 | **Owner:** Team A

As the system, I want match results served from cache when neither the demand record nor the supply index has changed so that repeated queries for the same demand do not re-run the full matching pipeline.

**Acceptance Criteria:**

* Cache key: `{demand_id}:{supply_index_version}` where `supply_index_version` is an incrementing counter updated on any profile add/update/delete event.
* `GET /demands/{demand_id}/matches` returns cached results when the cache key matches; no call to the matching pipeline is made.
* Cache is automatically invalidated (old entry deleted) on JD Modify event for the affected demand ID.
* Cache is automatically invalidated on JD Delete event.
* Cache is automatically invalidated when `supply_index_version` increments (i.e., a supply profile change occurred).
* Unit tests: cache hit path, cache miss path, invalidation on JD Modify, invalidation on supply version increment.

**Dependencies:** SP3-001, SP3-002, SP2-007.

---

### SP3-004 · Implement Phase 1 UI — Open Demands List Screen

**Epic:** E-06 | **Type:** Feature | **Points:** 5 | **Owner:** Team C

As a Talent Lead or Hiring Manager, I want to open the application and see a list of all open demand records so that I can browse and select a role to view matched supply profiles.

**Acceptance Criteria:**

* Demands list screen displays: Demand ID, role title, location, experience band, business unit, and a "View Matches" button for each record.
* List is populated from `GET /demands` API response.
* List is sortable by role title and location.
* Empty state shown when no demand records exist.
* Loading state shown while the API call is in progress.
* Accessibility: table has proper ARIA labels; keyboard navigation works.
* Connects to real API (not mock) by end of Sprint 3.

**Dependencies:** SP0-006 (UI scaffold), SP0-005 (API contract).

---

### SP3-005 · Implement Phase 1 UI — Demand Match Results Screen

**Epic:** E-06 | **Type:** Feature | **Points:** 8 | **Owner:** Team C

As a Talent Lead or Hiring Manager, I want to select a demand record and see a ranked list of matched employee profiles with their similarity scores so that I can quickly identify the best-fit internal candidates.

**Acceptance Criteria:**

* Selecting "View Matches" navigates to the match results screen for that demand ID.
* Results screen displays: rank, employee ID, similarity score (displayed as an integer percentage, e.g., "87%"), skills, designation, location, experience band, and project history.
* Profiles are displayed in descending similarity score order (rank 1 at top).
* Score is visually prominent (badge or progress bar).
* "Load More" button appears if results indicate a next page is available (supports iterative retrieval SP3-006).
* `MATCHING_IN_PROGRESS` state displayed when JD Modify is in progress.
* Empty state displayed when no candidates meet the 70% threshold.
* Connects to real API by end of Sprint 3.

**Dependencies:** SP3-004, SP2-007.

---

### SP3-006 · Implement Iterative Retrieval / Pagination

**Epic:** E-05 | **Type:** Feature | **Points:** 5 | **Owner:** Team A + C

As a Talent Lead, when fewer than 10 candidates meet the threshold, I want to request the next best-fit batch so that I can see additional candidates ranked below the initial top-10.

**Acceptance Criteria:**

* `GET /demands/{demand_id}/matches?page=2` returns the next batch of candidates below the initial top-10, ranked by descending score.
* Candidates in subsequent pages scored below the initial threshold (70%) are still returned but flagged as `below_threshold: true`.
* The UI "Load More" button triggers the page 2 API call and appends results below the initial list with a visual separator.
* No duplicate candidates across pages.
* Unit tests: first page returns 10, second page returns next 10, final page returns remaining candidates.

**Dependencies:** SP3-005, SP2-004.

---

### SP3-007 · Real API Integration — UI Connected to Matching Engine

**Epic:** E-06 | **Type:** Task | **Points:** 3 | **Owner:** Team C

As the product, I want the Phase 1 UI consuming real matching results from the live backend so that the integration is validated end-to-end before Sprint 4 evaluation begins.

**Acceptance Criteria:**

* Both UI screens (`/demands` and `/demands/{id}/matches`) driven by live API calls to the real matching engine (not mock data).
* At least 20 demand records and 1,000 supply profiles loaded in the dev environment; at least 5 demand records return non-empty real match results.
* Real similarity scores are displayed; ranked order matches the Search Result DB.
* No hardcoded mock data remains in the UI codebase.
* End-to-end smoke test executed by a Talent Lead persona: browse demands → select one → view ranked results.

**Dependencies:** SP3-004, SP3-005, SP2-007, SP3-003.

---

### SP3-008 · End-to-End JD Event Lifecycle Test

**Epic:** E-03 | **Type:** Task | **Points:** 3 | **Owner:** Team A

As the team, I want an automated integration test covering the complete JD event lifecycle (New → Modify → Delete) so that all three event handlers are validated together before Sprint 4.

**Acceptance Criteria:**

* Test: Upload new JD → verify results appear in Search Result DB.
* Test: Modify JD → verify old results cleared, new results appear.
* Test: Delete JD → verify all data removed from JD Index and Search Result DB.
* Test runs in CI integration test suite.
* Test completes in under 3 minutes.

**Dependencies:** SP3-001, SP3-002, SP3-003.

---

## Sprint 4: Evaluation, Security & Handoff

**Goal:** Deliver the evaluation framework with precision/recall metrics and multi-strategy comparison, harden security across all components, validate performance at 150,000-record scale, and produce the handoff package for the Wipro developer team.

**Parallel tracks within this sprint:**

* Track A: Evaluation framework and multi-strategy comparison (SP4-001 through SP4-004).
* Track B: Security hardening and compliance (SP4-005 through SP4-007).
* Track C: Performance validation and monitoring (SP4-008, SP4-009).
* Track D: Documentation and handoff (SP4-010).

---

### SP4-001 · Implement Evaluation Framework — Precision and Recall

**Epic:** E-07 | **Type:** Feature | **Points:** 8 | **Owner:** Anshuman Bhadauria / Dev

As Anshuman, I want a repeatable evaluation framework that measures matching precision and recall against a labelled test set so that matching accuracy can be baselined and tracked over time.

**Acceptance Criteria:**

* Evaluation framework implemented as a standalone script in `src/evaluation/`.
* Accepts as input: a set of demand records and corresponding ground truth supply profiles (expert-reviewed or synthetic labelled set).
* Computes and outputs: precision@10, recall@10, Mean Reciprocal Rank (MRR), and throughput (demand records matched per second).
* If no labelled ground truth is available, the framework generates a Talent Lead review template (CSV) listing the top-10 results per demand for manual scoring — addressing OQ-04.
* Output written to `docs/evaluation/evaluation-report.md` with a summary table.
* Framework runnable with a single command: `python src/evaluation/run_evaluation.py --strategy dense`.

**Dependencies:** SP2-007, SP2-008.

---

### SP4-002 · Implement Multi-Strategy Comparison

**Epic:** E-07 | **Type:** Feature | **Points:** 5 | **Owner:** Anshuman Bhadauria / Dev

As Anshuman, I want a side-by-side comparison of dense, sparse, and hybrid retrieval strategies on identical test queries so that the team can choose the optimal strategy for production deployment.

**Acceptance Criteria:**

* Evaluation script runs all three strategies (dense, sparse, hybrid) sequentially against the same test set.
* Comparison table produced showing precision@10, recall@10, MRR, and throughput for each strategy.
* Strategy that performs best on precision@10 identified and recommended in the output report.
* Report includes query-level breakdowns: for each test demand, show the rank of the ground truth candidate under each strategy.
* Output committed to `docs/evaluation/multi-strategy-comparison.md`.

**Dependencies:** SP4-001, SP2-008.

---

### SP4-003 · Scale Validation — 150,000-Record Supply Index

**Epic:** E-07 | **Type:** Task | **Points:** 8 | **Owner:** Dev team

As the system, I want performance validated at full 150,000-record scale so that NFR-002 (full supply pool evaluation per query) and NFR-001 (near real-time P95 latency) are confirmed or flagged for remediation before handoff.

**Acceptance Criteria:**

* Synthetic Supply Excel Dump scaled to 150,000 rows using the generator from SP0-004.
* All 150,000 profiles indexed into Azure AI Search.
* 100 sequential demand queries executed against the full index; P95 query latency recorded.
* No query evaluates a partial subset of the index — full coverage verified by comparing result candidate pool against index size.
* If P95 latency exceeds the agreed SLA (OQ-01), a performance finding is documented in `docs/evaluation/performance-report.md` with recommended index tier or algorithm changes.
* Throughput (demand records matched per hour) reported against the 50X–100X improvement target.

**Dependencies:** SP2-007, SP2-008, SP0-002 (AI Search tier).

---

### SP4-004 · Throughput Benchmarking

**Epic:** E-07 | **Type:** Task | **Points:** 3 | **Owner:** Dev team

As the team, I want throughput measured and reported against the 50X–100X improvement baseline so that the goal G-002 is verified with evidence.

**Acceptance Criteria:**

* Baseline throughput established: current manual process ~1 demand matched per day (per PRD G-002 baseline).
* System throughput measured: number of demand records fully matched (top-10 results stored) per hour under sustained load.
* Throughput improvement ratio computed and reported.
* If throughput target (50X–100X) is not met, bottleneck identified and documented.
* Results included in the evaluation report (SP4-001).

**Dependencies:** SP4-003.

---

### SP4-005 · Security Hardening — Authentication and Authorization

**Epic:** E-08 | **Type:** Task | **Points:** 5 | **Owner:** Dev Lead / ISE Security

As the system, I want all API endpoints and UI routes protected by Azure AD authentication so that no unauthenticated user can access supply data, demand data, or match results.

**Acceptance Criteria:**

* All API endpoints require a valid Azure AD bearer token; requests without a valid token return 401.
* UI application enforces Azure AD login before displaying any data (MSAL integration).
* RBAC roles enforced: Talent Lead role can view demands and match results; admin role required for data management endpoints.
* No API keys or connection strings used for authentication; managed identity used for all service-to-service calls.
* Security review checklist (OWASP API Security Top 10) completed and any findings remediated.

**Dependencies:** SP0-010, SP3-007.

---

### SP4-006 · PII and Data Residency Compliance Review

**Epic:** E-08 | **Type:** Task | **Points:** 3 | **Owner:** Rupali Agarwal / Dev

As the compliance owner, I want a documented review confirming all data remains within the Wipro Azure tenant and no real employee PII exists in non-production environments so that the project meets Wipro Data Privacy Policy requirements.

**Acceptance Criteria:**

* Architecture review documents confirming zero data egress outside Wipro Azure tenant completed and signed off by Shinoj Zacharias.
* Dev and test environments audited: no real employee names, emails, or identification numbers present.
* Synthetic data generation process documented and approved as the standard for all non-production environments.
* Wipro DPO approval process initiated for production use of real employee data.
* Compliance status updated in `docs/compliance/compliance-review.md`.

**Dependencies:** SP0-010.

---

### SP4-007 · Monitoring and Alerting Configuration

**Epic:** E-09 | **Type:** Task | **Points:** 5 | **Owner:** Dev team

As the operations team, I want Azure Monitor configured with dashboards and alerts for key pipeline metrics so that failures and performance degradation are detected without manual log inspection.

**Acceptance Criteria:**

* Azure Monitor workspace configured; diagnostic logs enabled for AI Search, Cosmos DB, Blob Storage, and Event Grid.
* Dashboard created showing: event pipeline processing rate, event dead-letter queue depth, query P95 latency, cache hit/miss ratio, and Search Result DB write latency.
* Alerts configured for: dead-letter queue depth > 0 (any failed event), P95 latency > agreed SLA threshold, event pipeline processing failure rate > 1%.
* Alert notifications routed to the Wipro operations team.
* Monitoring setup documented in `docs/infra/monitoring.md`.

**Dependencies:** SP0-002.

---

### SP4-008 · Load Testing and Concurrency Validation

**Epic:** E-09 | **Type:** Task | **Points:** 5 | **Owner:** Dev team

As the team, I want load testing run against the query API to confirm the system handles the expected concurrent user volume so that OQ-02 (concurrent demand queries) is answered with evidence.

**Acceptance Criteria:**

* Load test simulating concurrent demand query traffic executed against the dev environment (concurrent user count per OQ-02 estimate, or 50 concurrent users as default if OQ-02 remains unresolved).
* P95 latency under load recorded and compared against the SLA target.
* No query failures under target concurrency.
* Load test results committed to `docs/evaluation/load-test-report.md`.
* If SLA is breached under load, remediation options documented (scaling tier, caching improvements).

**Dependencies:** SP4-003, SP3-003.

---

### SP4-009 · Security Penetration Testing Preparation

**Epic:** E-08 | **Type:** Task | **Points:** 2 | **Owner:** Dev Lead

As the security team, I want a penetration testing scope document and a pre-pen-test remediation log prepared so that any identified vulnerabilities are tracked and addressed before handoff.

**Acceptance Criteria:**

* Pen test scope document created covering: API authentication bypass, injection attacks, RBAC bypass, data exfiltration paths.
* OWASP Top 10 checklist completed for the API layer; any findings remediated and documented.
* Dependency scan report (from CI) reviewed; all critical/high vulnerabilities resolved.
* Pre-pen-test remediation log committed to `docs/security/`.

**Dependencies:** SP4-005.

---

### SP4-010 · Documentation and Handoff Package

**Epic:** E-01 | **Type:** Task | **Points:** 8 | **Owner:** ISE Dev Lead + Rupali Agarwal

As the Wipro developer team receiving the codebase, I want comprehensive documentation and a structured handoff package so that I can maintain, extend, and operate the system without needing the ISE team present.

**Acceptance Criteria:**

* `README.md` updated with: project overview, architecture summary, local dev setup, deployment instructions, and link to all key docs.
* `docs/runbooks/` contains: how to re-index all supply profiles; how to roll back to a previous index version; how to add a new retrieval strategy; how to scale the AI Search tier.
* `docs/evaluation/` contains the final evaluation report and multi-strategy comparison (SP4-001, SP4-002).
* `docs/adr/` contains all ADRs written during the project.
* All open questions (OQ-01 through OQ-04) documented with their resolution status; any still-open questions flagged with recommended next steps.
* Handoff walkthrough session conducted with Wipro developer team and recorded or noted.
* Codebase passes all CI checks; no failing tests in main branch.

**Dependencies:** All preceding stories.

---

## Full Backlog Summary

| Story ID | Title                                                         | Sprint | Epic | Points | Priority  |
|----------|---------------------------------------------------------------|--------|------|--------|-----------|
| SP0-001  | Lock and Document Excel Dump Schemas                         | S0     | E-02 | 3      | Critical  |
| SP0-002  | Provision Azure Development Infrastructure                   | S0     | E-01 | 5      | Critical  |
| SP0-003  | Initialize Repository, Project Scaffold & CI/CD Pipeline     | S0     | E-01 | 5      | Critical  |
| SP0-004  | Generate Anonymized Synthetic Dataset                        | S0     | E-02 | 3      | Critical  |
| SP0-005  | Create Skeleton Backend API with Stub Endpoints              | S0     | E-06 | 5      | Critical  |
| SP0-006  | Create Skeleton Frontend Application                         | S0     | E-06 | 5      | Critical  |
| SP0-007  | Configure Local Development Environment                      | S0     | E-01 | 2      | High      |
| SP0-008  | Define and Commit System ADR                                 | S0     | E-01 | 2      | High      |
| SP0-009  | Define Similarity Score Schema and Caching Key Contract      | S0     | E-04 | 2      | High      |
| SP0-010  | Set Up Security Baseline (Dev Environment)                   | S0     | E-08 | 2      | High      |
| SP1-001  | Implement Supply Excel Dump Reader and Row Parser            | S1     | E-02 | 5      | Must      |
| SP1-002  | Implement Demand Excel Dump Reader and Row Parser            | S1     | E-02 | 5      | Must      |
| SP1-003  | Implement Supply Profile Vectorization                       | S1     | E-03 | 8      | Must      |
| SP1-004  | Implement Profile Added Event Handler → AI Search Index      | S1     | E-03 | 5      | Must      |
| SP1-005  | Implement Profile Updated Event Handler → AI Search Re-index | S1     | E-03 | 3      | Must      |
| SP1-006  | Implement Profile Deleted Event Handler → AI Search Removal  | S1     | E-03 | 3      | Must      |
| SP1-007  | Implement Demand Completeness Validation                     | S1     | E-02 | 3      | Must      |
| SP1-008  | Implement Sparse Supply Profile Handling                     | S1     | E-02 | 3      | Must      |
| SP1-009  | End-to-End Ingestion Integration Test                        | S1     | E-02 | 5      | Must      |
| SP2-001  | Implement Dense Semantic Retrieval Against AI Search         | S2     | E-04 | 8      | Must      |
| SP2-002  | Implement Similarity Score Normalization (0–100%)            | S2     | E-04 | 3      | Must      |
| SP2-003  | Implement 70% Similarity Score Threshold Enforcement         | S2     | E-04 | 2      | Must      |
| SP2-004  | Implement Ranked Top-10 Shortlist Generation                 | S2     | E-04 | 3      | Must      |
| SP2-005  | Implement Multi-Attribute Simultaneous Matching              | S2     | E-04 | 5      | Must      |
| SP2-006  | Implement JD Vectorization                                   | S2     | E-03 | 3      | Must      |
| SP2-007  | Implement New JD Event Handler → Vectorize → Match → Store   | S2     | E-03 | 8      | Must      |
| SP2-008  | Implement Sparse and Hybrid Retrieval Strategies             | S2     | E-04 | 8      | Should    |
| SP3-001  | Implement JD Modify Event Handler                            | S3     | E-03 | 5      | Must      |
| SP3-002  | Implement JD Delete Event Handler                            | S3     | E-03 | 3      | Must      |
| SP3-003  | Implement Result Caching and Cache Invalidation              | S3     | E-05 | 5      | Should    |
| SP3-004  | Implement Phase 1 UI — Open Demands List Screen              | S3     | E-06 | 5      | Must      |
| SP3-005  | Implement Phase 1 UI — Demand Match Results Screen           | S3     | E-06 | 8      | Must      |
| SP3-006  | Implement Iterative Retrieval / Pagination                   | S3     | E-05 | 5      | Should    |
| SP3-007  | Real API Integration — UI Connected to Matching Engine       | S3     | E-06 | 3      | Must      |
| SP3-008  | End-to-End JD Event Lifecycle Test                           | S3     | E-03 | 3      | Must      |
| SP4-001  | Implement Evaluation Framework — Precision and Recall        | S4     | E-07 | 8      | Must      |
| SP4-002  | Implement Multi-Strategy Comparison                          | S4     | E-07 | 5      | Should    |
| SP4-003  | Scale Validation — 150,000-Record Supply Index               | S4     | E-07 | 8      | Must      |
| SP4-004  | Throughput Benchmarking                                      | S4     | E-07 | 3      | Must      |
| SP4-005  | Security Hardening — Authentication and Authorization        | S4     | E-08 | 5      | Must      |
| SP4-006  | PII and Data Residency Compliance Review                     | S4     | E-08 | 3      | Must      |
| SP4-007  | Monitoring and Alerting Configuration                        | S4     | E-09 | 5      | Should    |
| SP4-008  | Load Testing and Concurrency Validation                      | S4     | E-09 | 5      | Should    |
| SP4-009  | Security Penetration Testing Preparation                     | S4     | E-08 | 2      | Should    |
| SP4-010  | Documentation and Handoff Package                            | S4     | E-01 | 8      | Must      |

---

## Parallelization Map

The diagram below shows which stories can run in parallel once Sprint 0 completes.

```text
Sprint 0 (all sequential within sprint, ship skeleton app)
└── SP0-001 → SP0-002 → SP0-004
└── SP0-003 → SP0-005 → SP0-006
└── SP0-007, SP0-008, SP0-009, SP0-010

Sprint 1 (two parallel tracks)
├── Track A (Ingestion + Indexing)
│   SP1-001 → SP1-003 → SP1-004 → SP1-005
│                                 → SP1-006
│                     SP1-008
└── Track B (Demand Ingestion)
    SP1-002 → SP1-007
              SP1-009 (waits for both tracks)

Sprint 2 (two parallel tracks)
├── Track A (Matching Engine)
│   SP2-001 → SP2-002 → SP2-003 → SP2-004
│          → SP2-005
│   SP2-006 → SP2-007 (waits for SP2-001 through SP2-005)
└── Track B (Alternative Strategies)
    SP2-008 (parallel to Track A, shares SP2-001 interface)

Sprint 3 (three parallel tracks)
├── Track A (JD Events + Caching)
│   SP3-001 → SP3-002 → SP3-003
├── Track B (Phase 1 UI)
│   SP3-004 → SP3-005 → SP3-007
└── Track C (Pagination)
    SP3-006 (parallel once SP2-004 stable)
    SP3-008 (waits for all Track A)

Sprint 4 (four parallel tracks)
├── Track A (Evaluation)
│   SP4-001 → SP4-002
│   SP4-003 → SP4-004
├── Track B (Security)
│   SP4-005 → SP4-009
│   SP4-006
├── Track C (Performance + Monitoring)
│   SP4-007, SP4-008
└── Track D (Handoff)
    SP4-010 (waits for all other tracks)
```

---

## Open Questions Tracker

| Q ID  | Question                                                                              | Sprint Impact          | Resolution Required By | Status  |
|-------|---------------------------------------------------------------------------------------|------------------------|------------------------|---------|
| OQ-01 | What is the agreed P95 query latency SLA?                                             | NFR-001, SP4-003       | Start of Sprint 2      | Open    |
| OQ-02 | What is the expected concurrent demand query volume at peak?                          | SP4-008 test design    | Start of Sprint 4      | Open    |
| OQ-03 | Exact column names and data types in Supply and Demand Excel Dumps?                   | SP0-001 (blocks S1)    | End of Sprint 0        | Partial |
| OQ-04 | Will a labelled ground truth test set be available, or will expert review be the proxy? | SP4-001 test set design | Start of Sprint 4    | Open    |

---

*Generated 2026-04-28 by GitHub Copilot*
