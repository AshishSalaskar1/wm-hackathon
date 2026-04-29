---
title: Similarity Score Contract
description: Contract describing similarity score formats and normalization rules for matching results.
author: GitHub Copilot
ms.date: 2026-04-28
ms.topic: reference
keywords:
  - similarity
  - contract
  - matching
---

# Similarity Score & Cache Contract

## Purpose

Defines the canonical formats and normalization rules for similarity scores, the cache key format used by the matching API, and the required cache invalidation events.

## Similarity score schema

- **Internal stored value (`similarity`)**: float, range 0.0–1.0 (inclusive). This is the canonical score used in DB and downstream services.
- **Displayed value (`score_percent`)**: integer, range 0–100. Calculated as `round(similarity * 100)`.
- **Raw source score (`similarity_raw`)**: float as returned by the retrieval engine (may be in a different domain such as -1..1). Store this value for auditing and debugging but do not use it directly for UI.

### Normalization rules

1. Determine the domain of `similarity_raw`:
   - If retrieval engine documents raw in `[-1, 1]` (cosine similarity), convert to canonical range with:

     $$ similarity = \\frac{similarity\_raw + 1.0}{2.0} $$

   - If retrieval engine returns values in `[0, 1]`, use:

     $$ similarity = similarity\_raw $$

   - If the retrieval engine documents a different raw range (e.g., [raw_min, raw_max]) use min-max normalization:

     $$ similarity = \\frac{similarity\_raw - raw\_min}{raw\_max - raw\_min} $$

2. Clamp `similarity` to [0.0, 1.0].
3. Compute `score_percent = round(similarity * 100)`.
4. Negative or NaN `similarity_raw` values map to `similarity = 0.0` and `score_percent = 0`.

Document the retrieval engine and the raw domain in the ADR and test fixtures used for integration testing.

## Result item schema (example JSON)

```json
{
  "demand_id": "DMD-0001",
  "employee_id": "EMP-00001",
  "similarity_raw": 0.871234,
  "similarity": 0.871234,
  "score_percent": 87,
  "rank": 1,
  "retrieval_strategy": "dense",
  "timestamp": "2026-04-28T15:40:00Z"
}
```

Field types:
- `similarity_raw`: number (float)
- `similarity`: number (float, 0.0–1.0)
- `score_percent`: integer (0–100)
- `rank`: integer (1..N)

## Operational notes

- Store both `similarity_raw` and `similarity` to enable post-hoc analysis and evaluation.
- Add unit tests and integration tests asserting normalization formulas and result serialization behavior.
- Record the retrieval engine name and raw score domain in the ADR (`docs/adr/`) and keep test fixtures aligned.

## Open questions

- If retrieval engine semantics differ between environments, document `raw_min`/`raw_max` per environment so normalization remains deterministic.

## Changelog

- 2026-04-28 — Initial contract created by GitHub Copilot.
