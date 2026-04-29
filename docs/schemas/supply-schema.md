---
title: Supply Schema — Employee Data (Excel Dump)
description: Confirmed column names, data types, and sample values for the Supply Excel Dump (Employee Data sheet). Locked as part of SP0-001.
author: GitHub Copilot
ms.date: 2026-04-28
ms.topic: reference
source-file: "Consolidated Demand Supply Data with JD.xlsx"
source-sheet: "Employee Data"
---

# Supply Schema — Employee Data

> **Status:** Locked (SP0-001 complete)
> **Source:** `Consolidated Demand Supply Data with JD.xlsx` → sheet **Employee Data**
> **Total records in source:** 8,335 rows

---

## Column Definitions

| # | Column Name | Logical Field | Data Type | Required | Nulls in Source | Sample Value | Notes |
|---|-------------|---------------|-----------|----------|-----------------|--------------|-------|
| 1 | `EMP_NO` | Employee ID (anonymized) | `string` | Yes | 0 / 8335 | `"1"` | Anonymized identifier; treated as opaque string. No real employee IDs. |
| 2 | `EMP_NAME` | Employee Name (anonymized) | `string` | Yes | 0 / 8335 | `"Employee1"` | Anonymized display name; no real PII. |
| 3 | `BAND` | Experience Band | `string` | Yes | 0 / 8335 | `"GROUP D1"` | Wipro band hierarchy (e.g., GROUP B2, GROUP C2, GROUP D1). Maps to experience level. |
| 4 | `NB_FROM` | Availability From Date | `string` (date `DD-MM-YYYY`) | Yes | 0 / 8335 | `"02-01-2026"` | Date the employee became/becomes available (bench start). Parse as date during ingestion. |
| 5 | `AGEING_BUCKET` | Availability Ageing Bucket | `string` (enum) | Yes | 0 / 8335 | `"31-60 DAYS"` | Categorical bucket: `0-30 DAYS`, `31-60 DAYS`, `61-90 DAYS`, `91-180 DAYS`, `>180 DAYS`. |
| 6 | `ONSITE_OFFSHORE` | Onsite / Offshore | `string` (enum) | Yes | 0 / 8335 | `"OFFSHORE"` | Values: `ONSITE`, `OFFSHORE`. |
| 7 | `Location` | Location (City) | `string` | Yes | 0 / 8335 | `"MUMBAI"` | City name. Note mixed case in source — normalize to UPPER during ingestion. |
| 8 | `EXPERIENCE` | Total Experience | `string` | Yes | 0 / 8335 | `"33Years 0Months"` | Free-form string (e.g., `"25Years 8Months"`). Parse years/months during ingestion for numeric comparison. |
| 9 | `ROLE_NAME` | Designation / Role | `string` | No ⚠️ | 36 / 8335 | `"Cluster Delivery Head (CDH) L1"` | Current role title. **36 records have null values** — treat as sparse; omit from embedding text if null. |
| 10 | `COUNTRY` | Country | `string` | Yes | 0 / 8335 | `"INDIA"` | Country of posting (e.g., `INDIA`, `GERMANY`). |
| 11 | `Skills_from_iAspire` | Skills (iAspire) | `string` (comma-separated with proficiency) | No ⚠️ | 503 / 8335 | `"Python(L4), Azure(L3), Agile-Scrum(L1)"` | Primary skills list from Wipro iAspire platform, with proficiency levels (L1–L5). **503 records null** — treat as sparse. |
| 12 | `CERTIFIED_SKILLS` | Certified Skills | `string` (comma-separated with level) | No ⚠️ | 1741 / 8335 | `"DELIVERY MANAGEMENT(L1), ENGLISH LANGUAGE(L1)"` | Skills for which employee holds certifications. **1,741 records null** (~20.9%). Flag as optional. |
| 13 | `TRAINED_SKILLS` | Trained Skills | `string` (comma-separated with level) | No ⚠️ | 987 / 8335 | `"Generative AI(L1), Project Management(L2)"` | Skills completed via training (not yet certified). **987 records null** (~11.8%). Flag as optional. |
| 14 | `RECENT_SKILL` | Recently Used Skills | `string` (comma-separated) | No ⚠️ | 6422 / 8335 | `"MAINFRAME, PROJECT MANAGEMENT"` | Skills actively used in recent projects. **6,422 records null** (~77%) — highly sparse; include if populated, omit if null. |
| 15 | `LANGUAGE_SKILL` | Language Skills | `string` (comma-separated) | No ⚠️ | 5961 / 8335 | `"English, Hindi, Telugu"` | Spoken/written language competencies. **5,961 records null** (~71.5%) — highly sparse; include if populated, omit if null. |
| 16 | `ROLE_CLUSTER_NAME` | Role Cluster | `string` | No ⚠️ | 1445 / 8335 | `"CLUSTER DELIVERY HEAD (CDH) L1"` | Wipro role cluster grouping (maps to demand's `SR_ROLE_CLUSTER_NAME`). **1,445 records null** (~17.3%). Used for cluster-level matching. |

---

## Ingestion Model Mapping

The `SupplyProfile` ingestion model maps Excel columns as follows:

```python
class SupplyProfile:
    employee_id: str               # EMP_NO
    employee_name: str             # EMP_NAME (anonymized)
    band: str                      # BAND
    availability_from: date        # NB_FROM (parsed from DD-MM-YYYY)
    ageing_bucket: str             # AGEING_BUCKET
    work_mode: str                 # ONSITE_OFFSHORE
    location: str                  # Location (normalized to UPPER)
    experience: str                # EXPERIENCE (raw); parse for numeric use
    role_name: str | None          # ROLE_NAME (nullable)
    country: str                   # COUNTRY
    skills_iaspire: str | None     # Skills_from_iAspire (nullable)
    certified_skills: str | None   # CERTIFIED_SKILLS (nullable)
    trained_skills: str | None     # TRAINED_SKILLS (nullable)
    recent_skills: str | None      # RECENT_SKILL (nullable)
    language_skills: str | None    # LANGUAGE_SKILL (nullable)
    role_cluster: str | None       # ROLE_CLUSTER_NAME (nullable)
```

---

## Skill Priority Resolution

Skill fields are resolved in strict priority order before embedding. Only the **highest-priority available field(s)** are included in the matching embedding. `TRAINED_SKILLS` and `RECENT_SKILL` are excluded from primary matching criteria and used only as fallbacks when both primary fields are absent.

| Priority | Field | Condition | Role in Matching |
|----------|-------|-----------|------------------|
| 1 (Highest) | `Skills_from_iAspire` | Always use when populated | **Primary matching signal** |
| 2 | `CERTIFIED_SKILLS` | Use when populated (alongside Priority 1 if both present) | **Primary matching signal** |
| 3 (Fallback) | `TRAINED_SKILLS` | Use only when both `Skills_from_iAspire` and `CERTIFIED_SKILLS` are null | Fallback only — not in primary match |
| 4 (Last resort) | `RECENT_SKILL` | Use only when Priority 1, 2, and 3 are all null | Last-resort fallback — not in primary match |

> `TRAINED_SKILLS` and `RECENT_SKILL` are **removed from matching criteria**. They participate only when no primary skill data exists.

---

## Embedding Text Representation

For vectorization, populate fields using the skill priority resolution above. Omit null/empty fields:

```
Skills: {Skills_from_iAspire [Priority 1 — include when populated]}.
Certified: {CERTIFIED_SKILLS [Priority 2 — include when populated]}.
Role: {ROLE_NAME}.
Role Cluster: {ROLE_CLUSTER_NAME}.
Band: {BAND}.
Location: {Location}.
Country: {COUNTRY}.
Experience: {EXPERIENCE}.
Work Mode: {ONSITE_OFFSHORE}.
```

**Fallback embedding** (used only when both `Skills_from_iAspire` and `CERTIFIED_SKILLS` are null):

```
Trained Skills: {TRAINED_SKILLS [Priority 3 — fallback only]}.
Recent Skills: {RECENT_SKILL [Priority 4 — last resort only]}.
Role: {ROLE_NAME}.
Role Cluster: {ROLE_CLUSTER_NAME}.
Band: {BAND}.
Location: {Location}.
Country: {COUNTRY}.
Experience: {EXPERIENCE}.
Work Mode: {ONSITE_OFFSHORE}.
```

A profile must have **at least one skill field populated** (via any priority level) to produce a valid embedding; otherwise raise `InsufficientDataError`.

---

## Sparse Profile Handling

| Condition | Handling |
|-----------|----------|
| `Skills_from_iAspire` present | **Use as Priority 1 skill signal** in primary matching embedding |
| `Skills_from_iAspire` null, `CERTIFIED_SKILLS` present | **Use `CERTIFIED_SKILLS` as Priority 2 skill signal** in primary matching embedding |
| Both primary fields null, `TRAINED_SKILLS` present | Use `TRAINED_SKILLS` as Priority 3 fallback — excluded from primary match criteria |
| All above null, `RECENT_SKILL` present | Use `RECENT_SKILL` as Priority 4 last-resort fallback — excluded from primary match criteria |
| All four skill fields null | Raise `InsufficientDataError` — profile cannot be embedded |
| `ROLE_NAME` is null | Omit from embedding text; valid profile |
| `LANGUAGE_SKILL` is null (~71%) | Omit silently — not used in matching |
| `ROLE_CLUSTER_NAME` is null (~17%) | Omit from embedding; degrades cluster match quality |

---

## Ambiguous / Flagged Columns

| Column | Issue | Resolution |
|--------|-------|------------|
| `NB_FROM` | Stored as string `DD-MM-YYYY` not native datetime | Parse explicitly during ingestion with `datetime.strptime(val, "%d-%m-%Y")` |
| `EXPERIENCE` | Free-form string (e.g., `"25Years 8Months"`) — not numeric | Parse with regex `(\d+)Years\s+(\d+)Months` for numeric operations; keep raw string for embedding |
| `Location` | Mixed case in source (some UPPER, some Title Case) | Normalize to UPPER on ingest |
| `Skills_from_iAspire` | Proficiency levels embedded in string `(L1)`–`(L5)` — not separate fields | Parse with regex `([^(,]+)\(L(\d)\)` if per-skill proficiency scoring is needed |
| `RECENT_SKILL` | 77% null — effectively optional | Treat as enrichment signal; never gate matching on it |
| `LANGUAGE_SKILL` | 71% null — effectively optional | Include only when populated |

---

## Open Questions (OQ-03 — Resolved)

- ✅ **Column names confirmed** from `Employee Data` sheet of `Consolidated Demand Supply Data with JD.xlsx`
- ✅ **Skill priority** is `Skills_from_iAspire` (Priority 1) → `CERTIFIED_SKILLS` (Priority 2) → `TRAINED_SKILLS` (Priority 3, fallback only) → `RECENT_SKILL` (Priority 4, last resort). `TRAINED_SKILLS` and `RECENT_SKILL` are excluded from primary matching criteria.
- ✅ **Experience field** is free-form string in `EXPERIENCE` column; numeric parse required
- ✅ **Availability** represented by `NB_FROM` (bench start date) + `AGEING_BUCKET` (categorical)
- ✅ **Employee ID** is `EMP_NO` — already anonymized in source data
- ✅ **Project history** is not a dedicated column; closest signal is `RECENT_SKILL` (highly sparse)
