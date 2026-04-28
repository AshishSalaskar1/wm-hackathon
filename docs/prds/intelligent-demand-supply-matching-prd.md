<!-- markdownlint-disable-file -->
<!-- markdown-table-prettify-ignore-start -->
# Intelligent Internal Demand-Supply Matching — Product Requirements Document (PRD)
Version 0.3 | Status Draft | Owner Rupali Agarwal | Team Wipro Co-Innovation / Microsoft ISE | Lifecycle Active Development

## Progress Tracker

| Phase              | Done                                            | Gaps                                                 | Updated    |
|--------------------|-------------------------------------------------|------------------------------------------------------|------------|
| Context            | ✅ Problem, stakeholders, scope                 | —                                                    | 2026-04-27 |
| Problem & Users    | ✅ Personas defined                             | Detailed workflow confirmation pending               | 2026-04-27 |
| Scope              | ✅ In/out scope; event-driven architecture      | —                                                    | 2026-04-27 |
| Requirements       | ✅ Functional and non-functional requirements   | SLA target; concurrent user volume                   | 2026-04-27 |
| Metrics & Risks    | ✅ KPIs and risks captured                      | Ground truth method to be confirmed                  | 2026-04-27 |
| Operationalization | Partial                                         | Monitoring thresholds; deployment topology           | 2026-04-27 |
| Finalization       | ⏳ Pending open questions                       | See Section 14                                       | 2026-04-27 |

Unresolved Critical Questions: 4 | TBDs: 2

---

## 1. Executive Summary

### Context

Wipro employs approximately 150,000 professionals globally. Talent leads and hiring managers need to fill open internal roles by matching them against the full employee pool. Today this is done manually — searching records using keyword filters or relying on personal networks — producing slow, inconsistent, and network-biased results.

Employee supply data is maintained as structured tabular records exported as Excel Dump files, with columns for employee ID, skills, designation, location, experience band, and project history. Internal demand (open roles) is similarly a structured Excel Dump, with columns for demand ID, role title, required skills, location, experience band, and business unit. Both datasets are stored in Azure Blob Storage.

No automated system exists to match these two datasets at scale. This is a **greenfield application development initiative**.

### Core Opportunity

Build an event-driven semantic matching application that evaluates Wipro's full 150,000-employee supply pool against each open demand record and returns a ranked, similarity-scored shortlist per role in near real-time — replacing manual search with systematic, attribute-based matching at 50X–100X the current throughput.

### Goals

| Goal ID | Statement                                                                                 | Type        | Baseline         | Target                               | Priority |
|---------|-------------------------------------------------------------------------------------------|-------------|------------------|--------------------------------------|----------|
| G-001   | Evaluate the full ~150,000-record supply pool per demand record                           | Scale       | Ad hoc / limited | 100% of supply pool per query        | High     |
| G-002   | Achieve 50X–100X throughput improvement over the current manual process                   | Performance | 1X (manual)      | 50X–100X                             | High     |
| G-003   | Return a ranked top-10 shortlist per demand record with similarity score ≥70%             | Quality     | Not enforced     | Top-10, ≥70% similarity score        | High     |
| G-004   | Eliminate manual search and personal-network bias as the primary identification mechanism | Process     | 100% manual      | Systematic attribute-based matching  | High     |
| G-005   | Deliver an evaluation framework for ongoing accuracy measurement                          | Quality     | No measurement   | Precision/recall baselined           | Medium   |

---

## 2. Problem Definition

### Current Situation

* Talent leads and hiring managers manually search Excel-based employee records using keyword filters.
* Reliance on personal networks means only a small, biased subset of 150,000 profiles is ever evaluated.
* No automated system compares demand parameters against supply profiles.

### Problem Statement

Wipro cannot systematically match open internal roles against its full employee supply at scale. Qualified employees go unmatched, internal mobility stalls, and avoidable external hiring costs are incurred.

### Root Causes

* No system performs semantic matching between demand (role parameters) and supply (employee profiles).
* Both datasets are sparse structured tabular records — requiring an embedding-based approach suited to short-form structured data rather than free-text documents.
* At 150,000 supply records, sequential scanning is computationally infeasible without a pre-built vector index maintained through event-driven updates.

### Impact of Inaction

Wipro fills roles with visible/networked employees rather than best-fit employees; internal mobility cannot be measured; external hiring costs persist for roles that could be filled internally.

---

## 3. Users & Personas

| Persona                  | Goals                                                         | Pain Points                                                                     | Impact    |
|--------------------------|---------------------------------------------------------------|---------------------------------------------------------------------------------|-----------|
| Talent Lead              | Identify best-fit internal employees for open demands quickly | Manual process is slow; results are network-biased; no similarity score or ranking | Primary |
| Hiring Manager           | Fill open internal roles quickly with the best-fit employee   | Cannot scan the full employee pool; shortlists are inconsistent and unscored    | Primary   |
| Wipro HR / TA Leadership | Track and improve internal mobility KPIs                      | No data to measure internal fill rate or match quality                          | Oversight |
| Talent Supply Chain Team | Prioritize demand across concurrent open roles                | No ranked candidate data to inform prioritization decisions                     | Consumer  |

### User Journey — Talent Lead / Hiring Manager

1. Opens the application and views the list of open demand records.
2. Selects a demand record to see its matched supply results.
3. Views a ranked list of matched employee profiles, each showing a numeric similarity score (0–100%).
4. Reviews the shortlist and selects candidates to approach.
5. If fewer than 10 candidates meet the threshold, requests the next best-fit batch.

---

## 4. Scope

### In Scope

* Semantic multi-attribute matching of tabular Demand records against the full tabular Supply dataset (~150,000 records).
* Ingestion of Supply (employee profiles) and Demand (open roles) from structured Excel Dump files uploaded to Azure Blob Storage.
* Fully event-driven indexing — all index updates are triggered by data change events:
  * **Profile events:** new profile added, profile updated, profile deleted.
  * **JD events:** New JD published, JD modified, JD deleted.
* Ranked top-10 shortlist per demand record; records below 70% similarity score suppressed.
* Numeric similarity score (0–100%) per matched employee profile.
* Result caching: return cached results when neither the demand record nor supply profiles have changed.
* Cache invalidation: JD Modify clears old results; JD Delete clears all associated data from the Search Result DB.
* Phase 1 UI: Talent Lead and Hiring Manager view open demand records and select one to see ranked matched supply profiles with similarity scores.
* Evaluation framework: precision, recall, and throughput measurement; side-by-side comparison of retrieval strategies (dense, sparse, hybrid).
* All data and compute within the Wipro Azure environment.

### Out of Scope

* External candidates or external-facing hiring workflows.
* Data quality remediation or normalization of either dataset.
* Demand prioritization across concurrent open roles.
* Post-selection feedback loops.
* Periodic or scheduled batch re-indexing — all indexing is event-driven only.
* Query input interface beyond the Phase 1 demand-supply match view — future phase.
* Role-specific profile variants per employee — future phase.
* Handling duplicate candidates across multiple concurrent demands — future phase.

### Assumptions

* Supply and Demand datasets are provided as structured Excel Dump files with defined, stable column schemas.
* Demand records must be ≥70% complete to be eligible for matching.
* Supply records may have sparse fields; missing values must not cause errors or zero scores.
* All development uses anonymized representative data; no real employee PII in dev/test.

### Constraints

* Azure-only: no external cloud services or on-premises infrastructure.
* All co-innovation work remains within the Wipro Azure tenant.

---

## 5. Product Overview

### Value Proposition

A semantic, event-driven matching application that evaluates Wipro's full 150,000-employee supply pool against each open demand record and returns a ranked shortlist with explicit similarity scores in near real-time — replacing manual search with systematic, scalable, attribute-based matching.

### Architecture Summary

The application follows a two-flow event-driven architecture (see attached architecture diagram):

**Flow 1 — Profile:**
Change in Profile → Azure Blob Storage → Event Updates (skills change) → Vectorize → Azure AI Search index updated

**Flow 2 — JD:**
Change in JD → Azure Blob Storage → Event Updates (New JD / JD Modify / JD Delete) → Vectorize → JD Index → Matching (JD + Profile via AI Search) → Search Result DB

* JD Modify triggers: clear old results from Search Result DB, re-run matching.
* JD Delete triggers: clear all associated data from Search Result DB.
* AI Search holds the full vectorized supply profile index. One JD match queries all employee profiles.
* Search Result DB persists ranked match results and supports caching.

### UX / UI

**Phase 1:** Talent Lead and Hiring Manager open the application, browse open demand records, select one, and view ranked matched employee profiles with their similarity scores (0–100%). No chat or query input interface in this phase.

---

## 6. Functional Requirements

| FR ID  | Title                                 | Description                                                                                                                                                                                 | Goals           | Personas                    | Priority | Acceptance Criteria                                                                                                                           |
|--------|---------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|-----------------------------|----------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| FR-001 | Semantic multi-attribute matching     | Match Demand records against the full Supply dataset using embedding-based semantic methods, not keyword or field-equality filtering                                                         | G-001, G-004    | Talent Lead, Hiring Manager | Must     | Results differ from a keyword-only baseline; contextual synonyms and related skills are matched                                               |
| FR-002 | Full supply pool evaluation           | Evaluate all ~150,000 supply records per demand query without performance degradation                                                                                                       | G-001, G-002    | Talent Lead, Hiring Manager | Must     | 100% of indexed supply records are evaluated per query; no record excluded by a pre-filter                                                    |
| FR-003 | Multi-attribute simultaneous match    | Match simultaneously across: skills, role/designation, location, experience band, and project history                                                                                      | G-001, G-004    | Talent Lead, Hiring Manager | Must     | Each attribute contributes to the composite similarity score                                                                                  |
| FR-004 | Ranked top-10 shortlist               | Return a ranked top-10 list of supply records with similarity score ≥70%, ordered by descending score                                                                                       | G-003           | Talent Lead, Hiring Manager | Must     | Response contains ≤10 records all scoring ≥70%, ranked highest-to-lowest; no below-threshold record included                                  |
| FR-005 | Similarity score threshold enforcement | Suppress any supply record with similarity score below 70%                                                                                                                                 | G-003           | Talent Lead                 | Must     | No below-threshold record appears in results; threshold configurable within 70–80% range                                                      |
| FR-006 | Similarity score display              | Each matched supply record displays a numeric similarity score (0–100%) representing semantic similarity to the demand record                                                               | G-003           | Talent Lead, Hiring Manager | Must     | Every returned record shows a numeric similarity score; records ordered by descending score; score visible in Phase 1 UI                      |
| FR-007 | Demand-supply match view (Phase 1 UI) | Talent Lead and Hiring Manager browse open demand records and select one to view ranked matched supply profiles with similarity scores                                                       | G-003, G-004    | Talent Lead, Hiring Manager | Must     | User browses open demand records; selecting a record displays ranked matched employee profiles with similarity scores                          |
| FR-008 | Near real-time response               | Return results from the event-driven index within a defined SLA                                                                                                                             | G-002           | Talent Lead, Hiring Manager | Must     | P95 query response time meets the agreed SLA; SLA to be defined — see OQ-01                                                                   |
| FR-009 | Supply ingestion from Excel Dump      | Ingest Supply (employee profile) data from structured Excel Dump files uploaded to Azure Blob Storage; each row is one employee profile                                                     | G-001           | System                      | Must     | Excel Dump read from Blob Storage; profile rows parsed and available for vectorization without manual intervention                             |
| FR-010 | Demand ingestion from Excel Dump      | Ingest Demand (open role) data from structured Excel Dump files uploaded to Azure Blob Storage; each row is one demand record                                                               | G-001           | System                      | Must     | Excel Dump read from Blob Storage; demand rows parsed and available for matching without manual intervention                                   |
| FR-011 | Event-driven profile indexing         | On profile change events from Blob Storage: (a) Profile added — vectorize and add to AI Search index; (b) Profile updated — re-vectorize and update index; (c) Profile deleted — remove from index | G-001, G-002 | System             | Must     | Add → indexed; Update → re-indexed; Delete → removed from AI Search index; no scheduled batch runs                                           |
| FR-012 | Event-driven JD indexing and matching | On JD change events from Blob Storage: (a) New JD — vectorize, add to JD Index, run matching against AI Search, store results in Search Result DB; (b) JD Modify — re-vectorize, clear old results, re-run matching; (c) JD Delete — remove from JD Index, clear all associated results from Search Result DB | G-001, G-002 | System | Must | New JD → results in Search Result DB; JD Modify → stale results cleared, fresh results stored; JD Delete → all data removed |
| FR-013 | Result caching                        | Cache match results in Search Result DB; return cached results when neither the demand record nor supply profiles have changed                                                               | G-002           | System                      | Should   | Unchanged demand record returns cached results without re-running the pipeline; cache key: demand ID + supply index version                    |
| FR-014 | Iterative retrieval                   | When fewer than 10 supply records meet the threshold, allow the user to request the next best-fit batch                                                                                     | G-003           | Talent Lead, Hiring Manager | Should   | "Load more" / pagination supported; next batch returns records with next-highest similarity scores                                            |
| FR-015 | Evaluation framework                  | Framework measuring matching accuracy (precision, recall) and throughput against a labelled or expert-reviewed test set                                                                     | G-005           | Anshuman Bhadauria          | Must     | Precision and recall metrics produced; throughput (records/second) reported; runs on multiple retrieval strategies                            |
| FR-016 | Multi-strategy comparison             | Side-by-side comparison of dense, sparse, and hybrid retrieval strategies on the same test set                                                                                              | G-005           | Anshuman Bhadauria          | Should   | Evaluation output includes a comparison table with scores per strategy for the same test queries                                              |

### Feature Hierarchy

```plain
Intelligent Demand-Supply Matching Application
├── Data Ingestion Layer
│   ├── Supply profile ingestion (Excel Dump → Blob Storage → row parsing)
│   └── Demand (JD) ingestion (Excel Dump → Blob Storage → row parsing)
├── Event-Driven Indexing & Vectorization
│   ├── Profile added → vectorize → add to AI Search index
│   ├── Profile updated → re-vectorize → update AI Search index
│   ├── Profile deleted → remove from AI Search index
│   ├── New JD → vectorize → JD Index → matching → Search Result DB
│   ├── JD Modify → re-vectorize → update JD Index → clear old results → re-run matching
│   └── JD Delete → remove from JD Index → clear all results from Search Result DB
├── Matching Engine
│   ├── Semantic multi-attribute retrieval (dense / sparse / hybrid)
│   ├── Similarity score computation per demand-supply pair (0–100%)
│   └── Score threshold enforcement (records below 70% suppressed)
├── Result Management
│   ├── Ranked top-10 results stored in Search Result DB
│   ├── Result caching and cache invalidation on JD Modify / Delete events
│   └── Iterative retrieval / pagination [Should]
├── Phase 1 UI
│   ├── Open demand records list view
│   └── Matched supply profiles view with similarity scores
└── Evaluation Framework
    ├── Precision / recall measurement
    ├── Throughput benchmarking
    └── Multi-strategy comparison (dense vs. sparse vs. hybrid)
```

---

## 7. Non-Functional Requirements

| NFR ID  | Category             | Requirement                                                                                                               | Metric / Target                                                     | Priority | Validation                                              |
|---------|----------------------|---------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------|----------|---------------------------------------------------------|
| NFR-001 | Performance          | Query response time against the event-driven index must be near real-time                                                 | P95 latency TBD — see OQ-01                                         | Must     | Load test with representative query volume              |
| NFR-002 | Scalability          | System must evaluate the full 150,000-record supply pool per demand query without degradation                             | 150,000 records evaluated per query; no partial scans               | Must     | Integration test with full-size anonymized dataset      |
| NFR-003 | Reliability          | Event-driven pipeline must process all profile and JD change events reliably                                              | 99% of change events processed and reflected in index               | Must     | Pipeline monitoring; dead-letter queue for failed events |
| NFR-004 | Availability         | Query API and Phase 1 UI available during business hours                                                                  | Best-effort for Phase 1; production SLA TBD                         | Should   | Uptime monitoring                                       |
| NFR-005 | Data Residency       | All data — Supply, Demand, index, cache, results — must remain within the Wipro Azure tenant                              | Zero data egress outside Wipro Azure tenant                         | Must     | Architecture review; no external calls transmitting data |
| NFR-006 | Privacy / PII        | All dev/test data is anonymized; no real employee PII in non-production environments                                      | Zero PII records in dev/test                                        | Must     | Data anonymization review before loading to dev/test    |
| NFR-007 | Sparse Data Handling | System must return valid similarity scores for supply records with missing fields; missing values must not cause errors    | Valid scores returned for records with ≥1 populated attribute       | Must     | Test with intentionally sparse supply records           |
| NFR-008 | Input Completeness   | Demand records below 70% completeness must be rejected before matching with a clear error response                        | 100% of under-threshold demand records rejected pre-match           | Must     | Unit tests with incomplete demand records               |
| NFR-009 | Security             | All API endpoints and UI screens must be authenticated; no unauthenticated access to supply data, demand data, or results | Zero unauthenticated endpoints; Azure AD / managed identity         | Must     | Security review of authentication layer                 |
| NFR-010 | Maintainability      | Retrieval strategy is modular; switching dense/sparse/hybrid requires configuration change only, not code rewrite         | New strategy pluggable within 1 developer day                       | Should   | Code review; strategy pattern or plugin architecture    |

---

## 8. Data & Analytics

### Inputs

| Dataset        | Source                                    | Format             | Key Columns                                                                                  | Trigger                                         |
|----------------|-------------------------------------------|--------------------|----------------------------------------------------------------------------------------------|-------------------------------------------------|
| Supply profiles | Azure Blob Storage (Excel Dump upload)   | Structured tabular | Employee ID (anon), skills, designation, location, experience band, project history, availability | Profile add / update / delete events         |
| Demand records | Azure Blob Storage (Excel Dump upload)    | Structured tabular | Demand ID, role title, required skills, location, experience band, business unit             | New JD / JD Modify / JD Delete events          |

### Outputs

| Output                    | Description                                                                                              | Storage            |
|---------------------------|----------------------------------------------------------------------------------------------------------|--------------------|
| Ranked match results      | Top-10 matched employee profiles per demand record, ordered by similarity score (0–100%), records below 70% suppressed | Search Result DB |
| Cached results            | Stored match results returned when demand and supply data are unchanged; invalidated on JD Modify / Delete | Search Result DB |
| Vectorized supply index   | Embedding vectors for all active supply profiles, updated on each profile change event                   | Azure AI Search    |
| Evaluation report         | Precision, recall, throughput per retrieval strategy                                                     | Evaluation output  |

### Metrics & Success Criteria

| Metric                                    | Baseline         | Target                            | Source                 |
|-------------------------------------------|------------------|-----------------------------------|------------------------|
| Supply records evaluated per demand query | Ad hoc / limited | 100% of pool (~150,000)           | Matching pipeline logs |
| Query response latency (P95)              | Hours to days    | Seconds — SLA TBD                 | API response time logs |
| Minimum similarity score enforced         | Not enforced     | ≥70%                              | Matching engine output |
| Top-N returned per demand record          | Not defined      | Top-10 ranked by similarity score | Matching engine output |
| Matching precision                        | Not measured     | Baselined against test set        | Evaluation framework   |
| Throughput (demand records matched/hour)  | 1X manual        | 50X–100X improvement              | Evaluation framework   |

---

## 9. Dependencies

| Dependency                          | Type           | Criticality | Owner                  | Risk                                                   | Mitigation                                                             |
|-------------------------------------|----------------|-------------|------------------------|--------------------------------------------------------|------------------------------------------------------------------------|
| Excel Dump schema confirmation      | Data           | Critical    | Rupali Agarwal / Wipro | Column names and types not yet locked                  | Confirm and lock schema before development starts                      |
| Anonymized representative data      | Data           | Critical    | Rupali Agarwal / Wipro | Sample Excel Dump files not yet shared                 | Generate synthetic data from confirmed schema if samples are delayed   |
| Azure AI Search (Wipro tenant)      | Infrastructure | Critical    | Wipro / ISE            | Service provisioning and quota                         | Confirm tier and availability before development starts                |
| Azure Blob Storage (Wipro tenant)   | Infrastructure | High        | Wipro / ISE            | Event trigger configuration                            | Validate Azure Event Grid / Blob trigger setup early in development    |
| Wipro Azure tenant access (dev team)| Access         | High        | Wipro IT / Infra       | Provisioning timeline                                  | Track daily; use local Azure emulator as fallback for early iterations |

---

## 10. Risks & Mitigations

| Risk ID | Description                                                          | Severity | Likelihood | Mitigation                                                                                            | Owner                    | Status   |
|---------|----------------------------------------------------------------------|----------|------------|-------------------------------------------------------------------------------------------------------|--------------------------|----------|
| R-001   | Supply profile data too sparse for effective semantic matching       | High     | High       | Design for sparse structured data; validate embedding strategy on representative samples early        | Anshuman Bhadauria       | Open     |
| R-002   | Demand records inconsistently populated                              | High     | Medium     | Enforce ≥70% completeness check at ingestion; define completeness scoring logic                       | Dev team                 | Open     |
| R-003   | No labelled ground truth for accuracy validation                     | Medium   | Medium     | Use Talent Lead expert review of top-10 results as proxy; plan labelled dataset creation post-Phase 1 | Anshuman Bhadauria       | Open     |
| R-004   | Excel Dump schema inconsistent across exports                        | Medium   | Medium     | Confirm and lock schema; implement schema validation at the ingestion boundary                        | Rupali Agarwal / Dev     | Open     |
| R-005   | Performance degradation at 150K records with dense embeddings        | High     | Medium     | Evaluate sparse and hybrid approaches early; use ANN indexing (HNSW) in Azure AI Search              | Anshuman Bhadauria / Dev | Open     |
| R-006   | Event pipeline missed or duplicated change events                    | Medium   | Medium     | Implement idempotent event processing; dead-letter queue for failed events; monitor pipeline          | Dev team                 | Open     |
| R-007   | Repeated surfacing of the same supply records across concurrent JDs  | Low      | High       | Deferred to future phase; managed by talent supply chain team                                         | Talent Supply Chain Team | Deferred |

---

## 11. Privacy, Security & Compliance

### Data Classification

Supply and demand data contain employee personal information. All dev/test environments use anonymized data — employee IDs replace real names; no real PII is permitted outside production.

### PII Handling

* Dev/test uses anonymized or synthetic Excel Dump data only.
* Real employee data requires Wipro Data Privacy approval before any production use.
* Data must not leave the Wipro Azure tenant boundary.

### Security Controls

* All API endpoints and UI routes use Azure AD authentication or managed identity; no API-key-only access.
* Azure AI Search index and Search Result DB have role-based access control (RBAC).
* Excel Dump files in Blob Storage are access-controlled; only the ingestion pipeline and authorized administrators may read them.

### Compliance

| Regulation                | Applicability                              | Action                                                       | Owner            | Status  |
|---------------------------|--------------------------------------------|--------------------------------------------------------------|------------------|---------|
| Wipro Data Privacy Policy | Employee PII in Supply dataset             | Anonymize all dev/test data; DPO approval required before production | Rupali Agarwal | Pending |
| Co-innovation Agreement   | All development in Wipro Azure environment | Architecture review to confirm zero data egress              | Shinoj Zacharias | Pending |

---

## 12. Operational Considerations

| Aspect             | Requirement                                                                              | Notes                                                              |
|--------------------|------------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| Deployment         | All components in Wipro Azure tenant                                                     | Azure AI Search, Blob Storage, Search Result DB (Cosmos DB or equivalent) |
| Rollback           | Index versioning; rollback to previous index state on failed event processing            | Phase 1: manual rollback acceptable                                |
| Monitoring         | Event pipeline processing, query latency, and cache hit/miss rate monitored              | Azure Monitor; alerting thresholds TBD                             |
| Alerting           | Alert on failed event processing; alert on P95 latency breach                            | Thresholds TBD                                                     |
| Capacity Planning  | Azure AI Search tier must support 150,000 vectors                                        | Confirm tier and quota before Phase 1 development starts           |

---

## 13. Rollout Plan

| Phase                              | Gate Criteria                                                                                     | Owner                  |
|------------------------------------|---------------------------------------------------------------------------------------------------|------------------------|
| Foundation                         | Excel Dump schema confirmed; Azure environment provisioned; anonymized sample data available      | Rupali Agarwal / Dev   |
| Core Development                   | Event-driven ingestion and indexing pipeline functional; matching engine returns similarity-scored results | Dev team (Wipro + ISE) |
| UI Integration                     | Phase 1 UI delivered; Talent Lead and Hiring Manager can view matched supply for open demands     | Dev team (Wipro + ISE) |
| Evaluation                         | Evaluation framework run; precision/recall baselined; multi-strategy comparison completed         | Anshuman Bhadauria     |
| Handoff                            | Application, evaluation report, and codebase documented and handed to Wipro developer team       | Wipro + ISE            |

---

## 14. Open Questions

| Q ID  | Question                                                                                                       | Owner                   | Status  |
|-------|----------------------------------------------------------------------------------------------------------------|-------------------------|---------|
| OQ-01 | What is the agreed P95 query latency SLA for the near-real-time requirement?                                   | Rupali Agarwal / Shinoj | Open    |
| OQ-02 | What is the expected number of concurrent demand queries during peak usage?                                     | Rupali Agarwal          | Open    |
| OQ-03 | What are the confirmed column names and data types in both the Supply and Demand Excel Dump files?              | Rupali Agarwal / Dev    | Partial |
| OQ-04 | Will a labelled ground truth test set be available, or will Talent Lead expert review serve as the accuracy proxy? | Anshuman / Rupali    | Open    |

---

## 15. Changelog

| Version | Date       | Author                       | Summary                          | Type    |
|---------|------------|------------------------------|----------------------------------|---------|
| 0.1     | 2026-04-27 | GitHub Copilot (PRD Builder) | Initial PRD draft                | Created |
| 0.2     | 2026-04-27 | GitHub Copilot (PRD Builder) | Removed disallowed references; aligned to architecture diagram | Revised |
| 0.3     | 2026-04-27 | GitHub Copilot (PRD Builder) | Full clean rewrite — architecture diagram as sole technical source; all disallowed terms eliminated; clear and concise format | Revised |

---

## 16. Appendix — Glossary

| Term                  | Definition                                                                                                          |
|-----------------------|---------------------------------------------------------------------------------------------------------------------|
| Demand dataset        | Open internal roles in Excel Dump format: demand ID, role title, required skills, location, experience band, business unit |
| Supply dataset        | Internal employee profiles in Excel Dump format: employee ID (anonymized), skills, designation, location, experience band, project history, availability |
| Excel Dump            | A structured tabular export in Excel (.xlsx) format; the authoritative data source for both supply and demand       |
| Event-driven indexing | All AI Search index updates are triggered by data change events (profile add/update/delete; JD new/modify/delete); no scheduled batch runs |
| Similarity score      | Numeric value (0–100%) representing the semantic similarity between a demand record and an employee profile; the primary match quality indicator |
| Search Result DB      | Persistent store (e.g., Azure Cosmos DB) holding computed match results per demand record; supports caching and cache invalidation |
| AI Search             | Azure AI Search service holding the vectorized supply profile index; queried during JD matching to retrieve profile matches |
| ANN                   | Approximate Nearest Neighbor search — the indexing technique enabling fast vector similarity search at 150K-record scale |

Generated 2026-04-27 by GitHub Copilot PRD Builder
<!-- markdown-table-prettify-ignore-end -->
