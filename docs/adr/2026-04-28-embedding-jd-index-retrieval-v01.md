# Architecture Decision Record: Embedding Model, JD Index, and Retrieval Strategy

**Status:** Proposed
**Date:** 2026-04-28

## Context

This ADR documents key architecture decisions for the Intelligent Demand-Supply Matching POC:
- Embedding model selection
- JD index design
- Retrieval strategy

## Decision

### 1. Embedding Model Selection
- **Model:** Azure OpenAI text-embedding-3-small
- **Rationale:**
  - Lower cost and latency compared to larger models
  - Sufficient accuracy for POC and initial matching quality validation
  - Easy upgrade path to larger models if needed

### 2. JD Index Design
- **Choice:** Separate Azure AI Search Index for JD embeddings
- **Rationale:**
  - Optimized for vector search and semantic queries
  - Consistent with supply profile indexing approach
  - Scales well for retrieval workloads
  - Enables similarity search out-of-the-box
- **Trade-offs:**
  - Additional Azure resource to manage
  - Slightly higher cost if underutilized
  - Schema changes require index updates

### 3. Retrieval Strategy
- **Choice:** Hybrid Retrieval (Dense + Sparse)
- **How it works:**
  - Dense retrieval uses embedding vectors to find semantically similar profiles
  - Sparse retrieval uses keyword-based search (BM25)
  - Hybrid combines both using Reciprocal Rank Fusion (RRF) to blend rankings
  - Captures both semantic meaning and exact keyword matches, improving recall and precision
- **Rationale:**
  - Maximizes matching accuracy for diverse queries
  - Leverages strengths of both semantic and keyword search

## Consequences
- System will use text-embedding-3-small for all vectorization
- JD records will be indexed in a dedicated AI Search index
- Retrieval logic will support hybrid (dense + sparse) strategy by default

---

*ADR finalized on 2026-04-28. Version 01.*
