---
title: Intelligent Internal Demand-Supply Matching — Business Requirements Document
description: Greenfield BRD for intelligently matching Wipro's structured Internal Demand and Supply datasets to surface top-N best-fit employees per open role at scale
author: Wipro Co-Innovation Team
ms.date: 2026-04-27
ms.topic: reference
keywords:
  - internal talent matching
  - demand supply mapping
  - semantic matching
  - internal mobility
---

## Context and Problem Statement

Wipro employs ~150,000 professionals globally and maintains two internal structured tabular datasets: an **Internal Demand dataset** (open roles: role title, required skills, location, experience band, business unit) and an **Internal Supply dataset** (employee profiles: skills, designation, location, experience, project history, availability). No intelligent system currently matches these two datasets at scale. Project managers rely on manual search and personal networks — a process that is slow, inconsistent, and cannot cover 150,000 supply records. Qualified employees go unmatched, internal mobility stalls, and avoidable external hiring costs are incurred. This is a **greenfield initiative** with no dependency on prior tooling.

## Business Objectives and Success Metrics

| ID   | Objective                                                                                          | Priority |
|------|----------------------------------------------------------------------------------------------------|----------|
| BO-1 | Intelligently match Demand records against the full ~150,000-record Supply dataset                 | High     |
| BO-2 | Achieve 50X–100X throughput improvement over the current manual process                            | High     |
| BO-3 | Return a ranked top-N shortlist per Demand record with a minimum 70–75% match score               | High     |
| BO-4 | Eliminate manual search and personal judgment as the primary talent identification mechanism        | High     |
| BO-5 | Deliver a reusable evaluation framework for ongoing accuracy measurement                           | Medium   |

| Metric                                      | Current Baseline  | Target                                     |
|---------------------------------------------|-------------------|--------------------------------------------|
| Supply records evaluated per demand record  | Ad hoc / limited  | Full pool (~150,000 records)               |
| Time to return shortlist                    | Hours to days     | Near real-time (seconds, indexed query)    |
| Minimum match score enforced                | Not enforced      | 70–75% threshold                           |
| Top-N returned per demand record            | Not defined       | Top 10 ranked matches                      |
| Matching accuracy (precision)               | Not measured      | Baselined against labelled test set        |

## Stakeholders

| Name / Group                   | Organization | Role                                                                        |
|--------------------------------|--------------|-----------------------------------------------------------------------------|
| Raju VN                        | Wipro        | Business Sponsor — approves scope and success criteria                      |
| Rupali Agarwal                 | Wipro        | Product Owner — defines requirements; accepts deliverables                  |
| Project Manager / Acct Manager | Wipro        | Primary end user — submits demand records; reviews shortlists               |
| Talent Acquisition / Recruiter | Wipro        | Secondary user — facilitates final selection from shortlists                |
| Wipro talent supply chain team | Wipro        | Demand prioritization across concurrent roles; output feeds their workflows |
| Wipro HR / TA leadership       | Wipro        | Business outcome owners; track internal mobility KPIs                       |
| Shinoj Zacharias               | Microsoft    | Technical Lead                                                              |
| Pinki Dutta                    | Microsoft    | Engagement Lead                                                             |
| Anshuman Bhadauria             | Microsoft    | Data Scientist — evaluation and matching strategies                         |
| Rishabh Mehrotra               | Wipro        | Developer                                                                   |
| Ankit Manjrekar                | Wipro        | Developer                                                                   |
| Aritra Sengupta                | Wipro        | Developer                                                                   |
| Rohan Verma                    | Wipro        | Developer (remote)                                                          |

## Scope

**In scope:** Semantic multi-attribute matching of tabular Demand records against the full tabular Supply dataset (~150,000 records); ingestion of both datasets from authoritative sources; ranked top-10 shortlist per demand record with 70–75% minimum match score; confidence-tiered results (high 90%+, medium 80–90%, suppressed below threshold); periodic background pre-indexing of Supply (every 15–30 days); event-driven partial re-index on record update; result caching for unchanged pairs; structured field input and natural language query input; evaluation framework; working prototype on anonymized representative data.

**Out of scope:** External candidates; data quality remediation of either dataset; demand prioritization across concurrent open roles (talent supply chain team responsibility); post-selection feedback loops; production deployment and enterprise security hardening.

**Key assumptions and constraints:** Both datasets are in tabular format with defined columns. Demand records must be ≥70% complete for a valid match. Supply records may be sparse; the solution must handle missing fields. All data and development must remain within Wipro's Azure environment. Deliverable is a prototype and evaluation framework.

## Business Requirements

### Matching

| ID     | Requirement                                                                                                                        | Objective  | Priority |
|--------|------------------------------------------------------------------------------------------------------------------------------------|------------|----------|
| BR-001 | Match Demand records against the full Supply dataset using semantic/contextual methods, not keyword or field-equality filtering     | BO-1, BO-4 | Must     |
| BR-002 | Evaluate all ~150,000 supply records per demand query without performance degradation                                              | BO-1, BO-2 | Must     |
| BR-003 | Match simultaneously across: skills, role/designation, location, experience band, and project history                              | BO-1, BO-4 | Must     |
| BR-004 | Return a ranked top-10 shortlist of supply records meeting the 70–75% minimum match threshold                                      | BO-3       | Must     |
| BR-005 | Suppress any supply record scoring below the 70% threshold from results                                                            | BO-3       | Must     |
| BR-006 | Support iterative retrieval of the next best-fit batch when fewer than top-N records meet the threshold                            | BO-3       | Should   |

### Input, Data, and Evaluation

| ID     | Requirement                                                                                                             | Objective | Priority |
|--------|-------------------------------------------------------------------------------------------------------------------------|-----------|----------|
| BR-008 | Accept demand input via structured field submission (role title, skills, location, experience band)                     | BO-1      | Must     |
| BR-009 | Accept demand input via natural language query                                                                          | BO-1      | Should   |
| BR-010 | Return results in near real-time against the pre-indexed Supply dataset (SLA to be defined)                             | BO-2      | Must     |
| BR-011 | Ingest Supply data from its tabular source via API or batch extract without manual preparation                          | BO-1      | Must     |
| BR-012 | Ingest Demand data from its tabular source; new records are picked up automatically                                     | BO-1      | Must     |
| BR-013 | Pre-index the full Supply dataset on a periodic background schedule (every 15–30 days)                                  | BO-2      | Must     |
| BR-014 | Support partial re-indexing of updated supply records within a defined time window                                      | BO-2      | Should   |
| BR-015 | Cache match results; return cached results when neither demand nor supply records have changed                           | BO-2      | Should   |
| BR-016 | Provide an evaluation framework measuring accuracy (precision, recall, throughput) against a labelled test set          | BO-6      | Must     |
| BR-017 | Support side-by-side comparison of multiple matching strategies (dense, sparse, hybrid) on the same test set            | BO-6      | Should   |

## Current and Future State

**Current state:** Project managers manually search internal HR records or rely on personal networks to find supply matches for open roles. No automated comparison of the Demand and Supply datasets exists. At 150,000 supply records, the process cannot scale; thousands of supply records go unevaluated per demand record.

**Future state:** A project manager submits a demand record (structured or natural language). The system returns a confidence-tiered, ranked top-10 shortlist in near real-time from the pre-indexed Supply dataset. The Supply index refreshes on schedule and on record change. An evaluation framework tracks accuracy over time.

## Benefits

| Dimension       | Current State        | Expected Improvement                                               |
|-----------------|----------------------|--------------------------------------------------------------------|
| Scale           | Ad hoc / limited     | Full 150,000-record supply pool evaluated per demand record        |
| Speed           | Hours to days        | Near real-time (seconds)                                           |
| Throughput      | 1X (manual)          | 50X to 100X                                                        |
| Consistency     | Network-dependent    | Systematic, attribute-based, bias-reduced                          |
| Internal fills  | Not tracked          | Measurable increase in internal mobility rate (baselined post-pilot) |
| Reusability     | None                 | Extensible architecture and evaluation framework for future use cases |

## Risks and Mitigations

| Risk                                                                 | Likelihood | Impact | Mitigation                                                                              |
|----------------------------------------------------------------------|------------|--------|-----------------------------------------------------------------------------------------|
| Supply data too sparse for effective semantic matching               | High       | High   | Design for sparse structured records; validate on representative sample early           |
| Demand records inconsistently populated                              | Medium     | High   | Define minimum completeness threshold; reject under-threshold records before matching   |
| No labelled ground truth to validate accuracy                        | Medium     | Medium | Use human expert review of top-10 results as proxy; plan labelled dataset creation      |
| Scope creep into hiring workflow or deployment tracking              | Low        | Medium | Scope boundary is shortlist delivery; downstream remains with talent supply chain team  |
| Repeated surfacing of same supply records across concurrent demands  | High       | Low    | Deferred to future phase; managed by talent supply chain team                           |

## Approval and Sign-off

| Role                    | Name            | Organization | Status  |
|-------------------------|-----------------|--------------|---------|
| Business Sponsor        | Raju VN         | Wipro        | Pending |
| Product Owner           | Rupali Agarwal  | Wipro        | Pending |
| Technical Lead          | Shinoj Zacharias| Microsoft    | Pending |
| Engagement Lead         | Pinki Dutta     | Microsoft    | Pending |
