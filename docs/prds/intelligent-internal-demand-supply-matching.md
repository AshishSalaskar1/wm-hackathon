---
title: Intelligent Internal Demand-Supply Matching - Product Requirements Document
description: PRD for intelligent semantic matching of internal Demand and Supply datasets to surface ranked top-N best-fit employees per role.
author: Wipro Co-Innovation Team; Microsoft
ms.date: 2026-04-27
ms.topic: prd
keywords:
  - internal talent matching
  - semantic matching
  - internal mobility
---

<!-- markdownlint-disable-file -->
<!-- markdown-table-prettify-ignore-start -->
# Intelligent Internal Demand-Supply Matching - Product Requirements Document (PRD)
Version 0.1 | Status Draft | Owner: Rupali Agarwal | Team: Wipro & Microsoft | Target: Prototype

## Progress Tracker
| Phase | Done | Gaps | Updated |
|-------|------|------|---------|
| Context | Yes | None | 2026-04-27 |
| Problem & Users | Yes | None | 2026-04-27 |
| Scope | Yes | Minor NFR details | 2026-04-27 |
| Requirements | In progress | NFRs & metrics confirmation | 2026-04-27 |
| Metrics & Risks | In progress | Labelled dataset plan | 2026-04-27 |
| Operationalization | Not started | Deployment ops | 2026-04-27 |
| Finalization | Not started | Stakeholder sign-off | 2026-04-27 |

Unresolved Critical Questions: 3 | TBDs: 3

## 1. Executive Summary
### Context
Wipro maintains structured internal datasets: an Internal Demand dataset (open roles) and an Internal Supply dataset (employee profiles). Matching Demand to the full Supply pool (~150,000 records) is currently manual and does not scale.

### Core Opportunity
Build a prototype that semantically matches Demand records to the full Supply dataset and returns a confidence-tiered, ranked top-10 shortlist within near-real-time SLAs. The prototype will include an evaluation framework to baseline and track matching accuracy.

### Goals
| Goal ID | Statement | Baseline | Target | Timeframe | Priority |
|--------|-----------|----------|--------|----------|----------|
| G-001 | Evaluate full supply pool per demand query | Ad hoc | Full (~150k) | Prototype | High |
| G-002 | Shortlist returned in near-real-time | Hours–days | Seconds (indexed query) | Prototype | High |
| G-003 | Minimum match score enforcement | Not enforced | 70–75% threshold | Prototype | High |
| G-004 | Throughput improvement | 1X manual | 50–100X | Prototype | High |

## 2. Problem Definition
### Current Situation
Project managers currently rely on manual searches and personal networks; with ~150,000 supply records, this is incomplete, slow, and inconsistent.

### Problem Statement
There is no scalable, automated way to find best-fit internal talent for open roles across Wipro's internal Supply dataset. Qualified employees remain under-discovered and external hiring costs increase.

### Impact of Inaction
Slower fills, lower internal mobility rates, inconsistent matching quality, and avoidable external hires.

## 3. Users & Personas
| Persona | Goals | Pain Points | Impact |
|---------|-------|------------|--------|
| Project Manager | Quickly get a ranked shortlist for an open role | Manual search; misses qualified people | Faster staffing decisions |
| Talent Acquisition | Shortlist for final selection | Non-standard shortlists from PMs | Consistent candidate pools |
| Talent Supply Chain | Prioritize roles | Lack of systematic ranking | Better throughput planning |

## 4. Scope
### In scope
* Semantic multi-attribute matching of tabular Demand records against full Supply dataset (~150k)
* Ingestion of Demand and Supply via API or batch
* Periodic pre-indexing (15–30 days) and event-driven partial re-index
* Ranked top-10 shortlist with 70–75% minimum match score
* Confidence tiers: High (90%+), Medium (80–90%), Suppressed (<70%)
* Evaluation framework and prototype on anonymized data

### Out of scope
* External candidates
* Data quality remediation workflows
* Production security hardening and enterprise deployment (future phase)

### Assumptions
* Tabular datasets with defined columns
* Demand records must be ≥70% complete to be matched
* Development and data remain in Wipro's Azure environment

## 5. Product Overview
### Value Proposition
Surface high-quality internal candidate shortlists at scale and speed to increase internal fills and reduce external hiring dependency.

### Key Capabilities
* Semantic matching across skills, role/designation, location, experience band, and project history
* Natural language and structured demand input
* Indexed retrieval with caching for unchanged pairs
* Evaluation harness for precision/recall benchmarking

## 6. Functional Requirements
| FR ID | Title | Description | Priority | Acceptance Criteria |
|-------|-------|-------------|----------|---------------------|
| FR-001 | Semantic matching across attributes | Match Demand records against full Supply using semantic/contextual methods (not keyword equality). | Must | Demonstrated matching on representative sample with qualitative review. |
| FR-002 | Full-pool evaluation | Evaluate all ~150k supply records per demand query without performance degradation (using pre-indexing/approximate search). | Must | Prototype returns top-10 within SLA on representative dataset. |
| FR-003 | Multi-attribute match | Match across skills, designation, location, experience, project history. | Must | Matches include metadata showing contributing attributes. |
| FR-004 | Top-N shortlist | Return ranked top-10 meeting 70–75% match threshold. | Must | Top-10 contains at least X% judged relevant by human reviewers (baseline TBD). |
| FR-005 | Threshold suppression | Suppress results scoring below 70% by default. | Must | Results under threshold not shown unless requested. |
| FR-006 | Iterative retrieval | Support retrieval of next-best batch if fewer than N meet threshold. | Should | API supports paginated retrieval of subsequent candidates. |
| FR-007 | Structured and NL input | Accept structured fields and natural language queries. | Should | Both inputs produce consistent shortlists in tests. |
| FR-008 | Ingestion | Ingest Supply & Demand via API or batch extracts automatically. | Must | Ingestion jobs run and log status; errors reported. |
| FR-009 | Indexing | Pre-index full Supply periodically and support partial re-index on updates. | Must | Index refresh runs on schedule; updated records re-indexed within defined window. |
| FR-010 | Caching | Cache results and return cached results when inputs unchanged. | Should | Cached results returned and metrics logged. |
| FR-011 | Evaluation framework | Provide evaluation harness measuring precision, recall, throughput on labelled test set. | Must | Evaluation reports generated with baseline metrics. |

## 7. Non-Functional Requirements
| NFR ID | Category | Requirement | Target | Validation |
|--------|----------|-------------|--------|------------|
| NFR-001 | Performance | Top-10 returned in near-real-time for pre-indexed queries | <= 3s median (prototype target) | Benchmarks on representative dataset |
| NFR-002 | Throughput | Support 50–100X throughput improvement over manual baseline | Prototype demonstrates throughput uplift in tests | Throughput benchmarking report |
| NFR-003 | Scalability | Support full 150k supply records and growth | Scales linearly; index sharding possible | Load tests pass threshold |
| NFR-004 | Freshness | Pre-index scheduled every 15–30 days; partial re-index within defined window | Index refresh interval configurable | Index refresh job logs |
| NFR-005 | Availability | Prototype: best-effort; Production: SLA TBD | Prototype best-effort | Monitor uptime during test runs |
| NFR-006 | Security & Privacy | All processing stays within Wipro Azure; no PII leakage in prototype | Comply with Wipro data policies | Security review checklist (prototype) |
| NFR-007 | Observability | Log match decisions, scores, query latency, index status | Instrumentation and dashboards | Metrics validated during test runs |

## 8. Data & Analytics
### Inputs
* Internal Demand dataset (role title, required skills, location, experience band, business unit)
* Internal Supply dataset (employee skills, designation, location, experience, project history, availability)

### Outputs / Events
* Ranked top-10 shortlist with match scores and contributing attributes
* Evaluation reports (precision, recall, throughput)

### Instrumentation Plan
| Event | Trigger | Payload | Purpose | Owner |
|-------|---------|---------|---------|-------|
| Query executed | Demand submit | demand_id, input_type, latency | Performance tracking | Analytics |
| Match returned | After matching | top-N ids, scores | Evaluation & audit | Analytics |
| Index refresh | Scheduled | index_version, duration | Freshness tracking | Platform |

### Metrics & Success Criteria
| Metric | Baseline | Target |
|--------|----------|--------|
| Match latency | Hours–days | <= 3s median (prototype) |
| Top-N match quality | Not measured | 70–75% min threshold; human-reviewed baseline |
| Throughput | Manual | 50–100X improvement |

## 9. Dependencies
| Dependency | Type | Criticality | Owner | Risk | Mitigation |
|------------|------|------------|-------|------|-----------|
| Supply dataset access | Data | High | Wipro HR | High | Confirm early; use anonymized sample if needed |
| Demand dataset access | Data | High | Wipro HR | High | Confirm schemas and ingest method |
| Azure environment | Infrastructure | High | Microsoft/Wipro | Medium | Use agreed dev subscription |
| Labelled test set | Data | Medium | Data Science | Medium | Plan human labelling early |

## 10. Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Supply data too sparse | High | High | Validate on sample early; design for sparse inputs |
| Demand incompleteness | Medium | High | Enforce completeness threshold; provide user guidance |
| No labelled ground truth | Medium | Medium | Use human review; create labelled dataset plan |
| Scope creep | Low | Medium | Maintain shortlist-only scope for prototype |

## 11. Privacy, Security & Compliance
* All data processing constrained to Wipro Azure tenancy for prototype.
* Prototype will avoid storing or exposing unnecessary PII; anonymized datasets used where possible.
* Security review required before any production deployment.

## 12. Operational Considerations
* Deployment: Prototype as a set of containerized services in a dev Azure subscription.
* Monitoring: Collect latency, error rates, index status; surface on simple dashboard.
* Support: Handed to talent supply chain team for feedback loop (future work).

## 13. Rollout & Launch Plan
### Phases / Milestones
| Phase | Date | Gate Criteria | Owner |
|-------|------|--------------|-------|
| Prototype build | Q2 2026 | Indexing + shortlisting + evaluation | Wipro/Microsoft |
| Evaluation & labeling | Q2 2026 | Baseline metrics available | Data Science |
| Pilot (limited users) | Q3 2026 | Stakeholder sign-off | Wipro |

## 14. Open Questions
| Q ID | Question | Owner | Deadline | Status |
|------|----------|-------|---------|--------|
| Q-001 | Who will provide labelled test set and timeline? | Data Science | TBD | Open |
| Q-002 | Acceptable SLA for production queries? | Business Sponsor | TBD | Open |
| Q-003 | Any retention or PII masking requirements for prototype? | Security | TBD | Open |

## 15. Changelog
| Version | Date | Author | Summary | Type |
|---------|------|-------|---------|------|
| 0.1 | 2026-04-27 | Wipro / Microsoft | Initial PRD derived from BRD | Draft |

## 16. References & Provenance
| Ref ID | Type | Source | Summary |
|--------|------|--------|---------|
| BRD-001 | BRD | [docs/brds/intelligent-talent-screening-brd.md](docs/brds/intelligent-talent-screening-brd.md) | Source BRD used to derive PRD |

Generated 2026-04-27 by PRD Builder assistant (mode: interactive)
<!-- markdown-table-prettify-ignore-end -->
