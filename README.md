# wm-hackathon

> **Disclaimer:** *This application was created during a HVE workshop to demonstrate a Job Description (JD) matching use case. It is intended solely as a prototype and is not a production-ready solution.*

## Business Use Case

Large enterprises maintain two structured internal datasets: an Internal Demand dataset representing open roles (role title, required skills, location, experience band, business unit) and an Internal Supply dataset representing employee profiles (skills, designation, location, experience, project history, availability). Matching demand to the full supply pool, which can exceed 150,000 records, is currently a manual process that does not scale.

### The Problem

Hiring managers and talent leads rely on keyword searches and personal networks to find internal candidates for open roles. This approach is slow, inconsistent, and cannot cover the full employee pool. The result is that qualified employees go unmatched, internal mobility stalls, and organizations incur avoidable external hiring costs.

### The Solution

This prototype delivers an intelligent, semantic matching solution that evaluates the full supply pool against each open demand record and returns a ranked, similarity-scored shortlist per role in near real-time. Key capabilities include:

- Semantic multi-attribute matching across skills, designation, location, experience band, and project history
- Ranked top-10 shortlist per demand record with a minimum 70-75% match score
- 50X to 100X throughput improvement over manual processes
- Event-driven indexing that keeps the supply index current as employee profiles change
- Support for both structured field input and natural language queries
- An evaluation framework for ongoing accuracy measurement (precision, recall, throughput)

### Expected Outcomes

| Dimension | Current State | Expected Improvement |
|-----------|---------------|----------------------|
| Scale | Ad hoc / limited | Full supply pool evaluated per demand record |
| Speed | Hours to days | Near real-time (seconds) |
| Throughput | 1X (manual) | 50X to 100X |
| Consistency | Network-dependent | Systematic, attribute-based, bias-reduced |
| Internal fills | Not tracked | Measurable increase in internal mobility rate |
