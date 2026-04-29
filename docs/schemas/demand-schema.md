---
title: Demand Schema — Demand OIR Data (CSV)
description: Confirmed column names, data types, and sample values for the Demand OIR CSV. Locked as part of SP0-001.
author: GitHub Copilot
ms.date: 2026-04-29
ms.topic: reference
source-file: "Demand OIR.csv"
---

# Demand Schema — Demand OIR Data

> **Status:** Locked (SP0-001 complete)
> **Source:** `Demand OIR.csv`
> **Total records in source:** 19 rows (open demands)

---

## Column Definitions

| # | Column Name | Logical Field | Data Type | Required | Nulls in Source | Sample Value | Notes |
|---|-------------|---------------|-----------|----------|-----------------|--------------|-------|
| 1 | `GROUP_CUSTOMER_NAME` | Business Unit / Customer | `string` | Yes | 0 / 19 | `"Customer2"` | Anonymized customer/business unit name. Maps to "business unit" in PRD. |
| 2 | `SR_ID` | Demand ID | `integer` | Yes | 0 / 19 | `1` | Unique Service Request identifier. Primary key for the demand record. |
| 3 | `ESSENTIAL_SKILL` | Required Essential Skill | `string` | Yes | 0 / 19 | `".NET"` | Single primary/essential skill required for the role. Used as a key matching signal. |
| 4 | `DERIVED_SR_CITY` | Location (City) | `string` | Yes | 0 / 19 | `"HYDERABAD"` | City where the resource is required. Stored in UPPER case. |
| 5 | `SR_CREATED_ON` | SR Created Date | `string` | Yes | 0 / 19 | `"17 April 2026"` | Date the service request was raised. Format: `DD Month YYYY`. |
| 6 | `DEM_ST_DATE` | Demand Start Date | `string` | Yes | 0 / 19 | `"30-04-2026"` | Date by which the resource is needed. Format: `DD-MM-YYYY`. |
| 7 | `DEM_END_DATE` | Demand End Date | `string` | Yes | 0 / 19 | `"25-05-2026"` | Expected end date of the demand/engagement. Format: `DD-MM-YYYY`. |
| 8 | `ROLE_DESCRIPTION` | Role Description | `string` | Yes | 0 / 19 | `"Developer L3"` | Short role label (e.g., `Developer L3`, `Project Manager L2`). |
| 9 | `ONS/OFF` | Onsite / Offshore | `string` (enum) | Yes | 0 / 19 | `"OFFSHORE"` | Values: `ONSITE`, `OFFSHORE`. Must match `ONSITE_OFFSHORE` in supply. |
| 10 | `DERIVED_SR_COUNTRY` | Country | `string` | Yes | 0 / 19 | `"INDIA"` | Country where the resource is required. |
| 11 | `SR_BAND` | Required Experience Band | `string` | Yes | 0 / 19 | `"GROUP B2"` | Required Wipro band level (e.g., `GROUP B2`, `GROUP C1`). Must align with supply `BAND` values. |
| 12 | `OPEN_POS` | Open Positions | `integer` | Yes | 0 / 19 | `1` | Number of open headcount positions for this demand. Values: `1` or `2` in source. |
| 13 | `JD` | Job Description (Full Text) | `string` (long text) | Yes | 0 / 19 | `"overall experience and 4 years on MSPP..."` | Full free-text job description. Primary source for semantic embedding of the demand. Contains skill requirements, responsibilities, tools, and context. |
| 14 | `SR_ROLE_CLUSTER_NAME` | Role Cluster | `string` | Yes | 0 / 19 | `"DEVELOPER L3"` | Wipro role cluster. Maps to `ROLE_CLUSTER_NAME` in supply for cluster-level pre-filter. |

---

## Ingestion Model Mapping

The `DemandRecord` ingestion model maps CSV columns as follows:

```python
class DemandRecord:
    demand_id: int                 # SR_ID
    customer_name: str             # GROUP_CUSTOMER_NAME (business unit)
    essential_skill: str           # ESSENTIAL_SKILL
    location: str                  # DERIVED_SR_CITY
    country: str                   # DERIVED_SR_COUNTRY
    created_on: date               # SR_CREATED_ON
    start_date: date               # DEM_ST_DATE
    end_date: date                 # DEM_END_DATE
    role_description: str          # ROLE_DESCRIPTION
    work_mode: str                 # ONS/OFF
    band: str                      # SR_BAND
    open_positions: int            # OPEN_POS
    job_description: str           # JD (full text)
    role_cluster: str              # SR_ROLE_CLUSTER_NAME
```

---

## Embedding Text Representation

For vectorization, use the `JD` (full job description) as the primary embedding source, supplemented by structured fields:

```
Role: {ROLE_DESCRIPTION}.
Role Cluster: {SR_ROLE_CLUSTER_NAME}.
Essential Skill: {ESSENTIAL_SKILL}.
Band: {SR_BAND}.
Location: {DERIVED_SR_CITY}.
Country: {DERIVED_SR_COUNTRY}.
Work Mode: {ONS/OFF}.
Job Description: {JD}.
```

The `JD` field contains the richest semantic signal (skills, tools, responsibilities). The structured fields (`ESSENTIAL_SKILL`, `SR_BAND`, `ROLE_CLUSTER_NAME`, etc.) provide explicit attribute anchors for multi-attribute matching.

---

## Completeness Validation

Per FR-008 / NFR-008: demand records below **70% field completeness** are rejected before matching.

Completeness is computed as:

```
completeness = (count of non-null fields / 14 total fields) × 100
```

Since all 14 columns are non-null across all 19 source records, every source record currently meets the threshold. Validation is enforced during ingestion for future uploads.

| Field count populated | Completeness | Decision |
|----------------------|--------------|----------|
| 14 / 14 | 100% | ✅ Accepted |
| 10 / 14 | 71.4% | ✅ Accepted |
| 9 / 14 | 64.3% | ❌ Rejected (`IncompleteDemandError`) |
| < 9 | < 64.3% | ❌ Rejected |

---

## Matching Key — Demand ↔ Supply Field Alignment

| Demand Column | Supply Column | Match Type | Notes |
|---------------|---------------|------------|-------|
| `JD` (full text) | `Skills_from_iAspire` (P1) → `CERTIFIED_SKILLS` (P2) → `TRAINED_SKILLS` (P3 fallback) → `RECENT_SKILL` (P4 fallback) | Semantic (dense/hybrid embedding) | Priority-resolved: P3/P4 used only when P1 and P2 are both null |
| `ESSENTIAL_SKILL` | `Skills_from_iAspire` (P1) → `CERTIFIED_SKILLS` (P2) | Keyword / semantic signal | Matched against primary skill fields only |
| `SR_BAND` | `BAND` | Exact / range filter |
| `DERIVED_SR_CITY` | `Location` | Exact / soft filter |
| `DERIVED_SR_COUNTRY` | `COUNTRY` | Exact filter |
| `ONS/OFF` | `ONSITE_OFFSHORE` | Exact filter |
| `SR_ROLE_CLUSTER_NAME` | `ROLE_CLUSTER_NAME` | Cluster-level pre-filter |
| `ROLE_DESCRIPTION` | `ROLE_NAME` | Semantic signal |

---

## Ambiguous / Flagged Columns

| Column | Issue | Resolution |
|--------|-------|------------|
| `ONS/OFF` | Column name contains `/` — not a valid Python identifier | Rename to `work_mode` in the `DemandRecord` model on ingest |
| `SR_CREATED_ON` | Stored as text `DD Month YYYY` (e.g. `17 April 2026`) | Parse to `date` on ingest |
| `DEM_ST_DATE`, `DEM_END_DATE` | Stored as text `DD-MM-YYYY` (e.g. `30-04-2026`) | Parse to `date` on ingest |
| `JD` | Very long free text (up to several KB per row); contains embedded newlines | Normalize whitespace and truncate to max token limit before embedding if required |
| `OPEN_POS` | Values `1` or `2` in current source data (SR_IDs 14, 15 have `2`) | Ingest as-is; may vary in future uploads |
| `GROUP_CUSTOMER_NAME` | Anonymized in source (`Customer2`, `Customer4`, etc.) | Use anonymized value; do not attempt to de-anonymize |

---

## Open Questions (OQ-03 — Resolved)

- ✅ **Demand ID** is `SR_ID` (integer, primary key)
- ✅ **Role title / description** is `ROLE_DESCRIPTION` (short) + full text in `JD`
- ✅ **Required skills** are `ESSENTIAL_SKILL` (single primary) + full detail in `JD`
- ✅ **Location** is `DERIVED_SR_CITY` (city) + `DERIVED_SR_COUNTRY` (country)
- ✅ **Experience band** is `SR_BAND` (Wipro band string, e.g., `GROUP B2`)
- ✅ **Business unit** is `GROUP_CUSTOMER_NAME` (anonymized customer name)
- ✅ **Onsite/Offshore** is `ONS/OFF` — normalize key to `work_mode` in model
- ✅ **Role cluster** is `SR_ROLE_CLUSTER_NAME` — maps directly to supply `ROLE_CLUSTER_NAME`
