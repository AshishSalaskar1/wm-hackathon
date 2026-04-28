# Meeting Notes: Wipro Connect — HVE Workshop Prep

## Meeting Information
- **Date:** 2026-04-14
- **Time:** 12:47 PM – 1:33 PM (45m 41s)
- **Meeting Type:** Scope Conversations / Problem Statement Refinement

- **Current Design Thinking Method:** Method 1: Scope Conversations
- **Meeting Facilitator:** Pinki Dutta
- **Participants:**
  - Rupali Agarwal – Wipro (Product Owner / Use Case Lead)
  - Rishabh Mehrotra – Wipro (Developer)
  - Ankit Manjrekar – Wipro (Developer)
  - Manoj (Wipro) — joined briefly
  - Pinki Dutta – ISE/Microsoft (Engagement Lead)
  - Shinoj Zacharias – ISE/Microsoft (Technical Lead)
  - Ginette Vellera – ISE/Microsoft
  - Deepthi Sebastian – ISE/Microsoft
  - Jahan J – ISE/Microsoft
  - Anshuman Bhadauria – ISE/Microsoft (Data Scientist)

## Context & Objectives
- **Primary Objective:** Refine the problem statement with technical depth — clarify inputs, outputs, data structure, interaction channels, latency expectations, and the two-stage architecture (retrieval vs. ranking)
- **Secondary Objectives:** Understand the underlying system (SuccessFactors); request a demo for tomorrow; confirm environment and tooling readiness; begin planning the workshop agenda
- **Pre-meeting State:** Apr 13 standup had confirmed team composition, tentative dates (22-24), and outstanding items (sample data, demo, access). Today's call expanded to include ISE developers for the first joint technical discussion.

## Key Insights & Discoveries

### Stakeholder Insights
- **End users are not recruiters** — they are internal **project managers and account managers** who have open roles and want to fill them internally rather than going to external hiring
- Rupali will conduct an internal connect with these personas to understand their current workflow and whether they need a UI/UX front-end
- Manoj (Wipro senior) joined briefly — he may provide input on Day 1 of the workshop

### User Needs & Behaviors
- Hiring managers expect **real-time (or near-real-time) results** when they search against an open role — no defined SLA yet, but "as fast as the system allows"
- Two interaction channels envisioned: (1) upload/paste a JD and system extracts relevant parameters, (2) a chat interface where the recruiter types natural language queries (e.g., "give me candidates with 10 years DSM experience in Bangalore")
- When no suitable candidates are found in the first batch, the hiring manager returns to the system for the next set of matches — implying **pagination or iterative retrieval** is needed
- Profile updates by employees should eventually trigger re-matching, but real-time event-driven matching is not feasible at 150K scale; a **frequency-based background re-indexing** (e.g., every 15 days or monthly) is more practical

### Problem Space Insights
- **Critical clarification on the two-stage problem:**
  1. **Retrieval stage (main hackathon focus):** From 150,000 internal profiles, narrow down to ~200-500 relevant candidates per role using semantic matching — this is a **new problem with no existing implementation**
  2. **Ranking stage (existing OptiFit territory):** Screen and rank the narrowed set against the JD in detail — OptiFit handles this for external hiring, might be reusable
- **Internal profiles are fundamentally different from external resumes:** Internal data is sparse — just skills, role, location, project details (structured fields in SuccessFactors). External resumes are 1-2 page documents. This distinction changes the matching approach entirely
- The **JDs for internal roles are also sparse** — not full job descriptions but rather short parameter sets: role, location, skills. This is closer to search parameters than a traditional JD
- The underlying data system is **SAP SuccessFactors**, accessed via APIs
- **No implementation exists yet** for the internal SuccessFactors-based matching system — this is greenfield

### Solution Space Insights
- **Hybrid processing architecture emerged:**
  - **Background pre-computation:** Periodically (every 15 days or monthly) scan and pre-index the full 150K database, creating pre-computed buckets/clusters so that when a new role comes in, the system doesn't scan from scratch
  - **On-demand real-time matching:** When a hiring manager submits a role, match only against the pre-computed relevant pool, not the full database
- Jahan J proposed that if nothing has changed (no profile updates, no JD changes), previously computed matches should be **cached and reused** — no need to re-run
- Two trigger types for re-computation: (1) time-based frequency (background), (2) event-based (profile update, JD update) — Rupali confirmed a hybrid approach is preferred
- Anshuman framed it as a **retrieval + ranker two-tower architecture** — retrieval extracts the top ~200 semantically relevant candidates, ranker scores and orders them
- The matching must be **contextual and semantic**, not keyword-based — multiple parameters must be considered simultaneously
- Rupali is open to the hackathon team proposing an entirely new approach: "If you feel we want to use [OptiFit], we are open. If the solution is so unique we don't need it, we are fine with that also"
- For the workshop, the team will take **one slice** of the problem (likely the retrieval stage) and use HVE approaches to build a prototype

### Implementation Space Insights
- Data access will be through **SuccessFactors APIs** — Deepthi requested an anonymized schema of how talent details are structured for an individual
- The workshop deliverable will be a **prototype**, not a production deployment — the team will also provide an **evaluation framework** for Wipro to use post-workshop
- Shinoj and Pinki clarified the workshop goal: use HVE techniques to build a solution slice, demonstrate multiple approaches for evaluation, and give Wipro the skills to apply HVE to future projects
- Anshuman will present **evaluation approaches and multiple retrieval strategies** in upcoming prep calls
- Sample data (JDs, resumes) still not available — Rishabh confirmed they need to gather it from the team; demo planned for tomorrow

## Decisions Made

### Methodology Decisions
- **Decision:** The workshop will focus on **one slice of the problem** using HVE approaches — specifically the retrieval stage (150K → ~200 candidates)
- **Rationale:** Three days is limited; focusing on one well-defined slice allows depth over breadth while demonstrating HVE techniques
- **Impact:** The ranking/screening stage (OptiFit territory) is explicitly out of scope for the workshop but may be incorporated as a second step if the existing solution can be reused

- **Decision:** Workshop deliverable is a **prototype + evaluation framework**, not a production system
- **Rationale:** The goal is to demonstrate HVE approaches and give Wipro skills to build the full solution, not to deploy
- **Impact:** Sets realistic expectations; Wipro gets reusable techniques and frameworks to continue post-workshop

### Scope Decisions
- **Decision:** Support **both interaction channels** in the long-term vision: JD upload with extraction and chat/natural language query — for the workshop, start with one simple channel
- **Rationale:** Both are needed by different personas; starting simple allows focus during the constrained workshop time
- **Impact:** Future solution will need NLP extraction from JDs and also a conversational interface

- **Decision:** Matching must be **semantic and contextual**, not keyword-based — multiple parameters simultaneously
- **Rationale:** Rupali explicitly stated keyword search is not the problem they're solving; the real challenge is contextual matching similar to how a human recruiter evaluates fit
- **Impact:** Solution design must incorporate embedding-based or semantic search approaches rather than simple text matching

### Next Steps Decisions
- **Decision:** **Demo of the existing process/system** scheduled for tomorrow (April 15)
- **Rationale:** The team needs to see how things work today before designing the solution; multiple questions will be answered by seeing the actual workflow
- **Impact:** Tomorrow's standup is prioritized for the demo walkthrough

- **Decision:** Document and circulate the **refined problem statement** after tomorrow's discussion
- **Rationale:** Shinoj proposed capturing the problem context in a shared document for all stakeholders
- **Impact:** Creates a single source of truth; will be shared via the Teams channel

## Action Items & Next Steps

### Immediate Actions (Next 1-2 days)
- [ ] **Prepare and deliver demo of current process** – Assigned to: Rupali Agarwal / Rishabh Mehrotra – Due: 2026-04-15
- [ ] **Share sample JDs and resumes** (at minimum, show during demo) – Assigned to: Rupali Agarwal – Due: 2026-04-15
- [ ] **Provide anonymized SuccessFactors schema** (how talent data is structured per individual) – Assigned to: Rupali Agarwal – Due: 2026-04-15
- [ ] **Share Wipro team details** (format previously requested) – Assigned to: Rupali Agarwal – Due: 2026-04-14 (today)
- [ ] **Create shared MS Teams channel and share access** – Assigned to: Rupali Agarwal – Due: 2026-04-14 (today)
- [ ] **Share ISE team details on email** – Assigned to: Pinki Dutta – Due: 2026-04-14 (already sent)
- [ ] **Conduct internal connect with PMs/account managers** to understand current workflow – Assigned to: Rupali Agarwal – Due: before workshop
- [ ] **Prepare evaluation approaches presentation** – Assigned to: Anshuman Bhadauria – Due: during this week's prep calls
- [ ] **Plan and share workshop agenda** – Assigned to: Pinki Dutta / Shinoj Zacharias – Due: 2026-04-17
- [ ] **Document refined problem statement and circulate** – Assigned to: Shinoj Zacharias / Pinki Dutta – Due: 2026-04-15

### Method Progression
- [ ] **Complete Current Method:** See demo, validate problem statement, define success metrics, confirm the retrieval-stage focus
- [ ] **Prepare for Next Method:** Internal ISE planning — Anshuman to prepare multiple approach options for retrieval and evaluation; plan HVE intro session
- [ ] **Stakeholder Follow-up:** Tomorrow's demo is the key milestone; internal connect with end users (PMs/account managers) needed before workshop

### Research & Validation
- [ ] **Research Tasks:** Explore semantic retrieval approaches for structured/sparse profile data (SuccessFactors schema); investigate embedding strategies for short-text parameter matching
- [ ] **Validation Activities:** Validate data access patterns via SuccessFactors APIs; verify what pre-processing is feasible given data sparsity
- [ ] **Documentation:** Capture refined problem statement in shared doc; upload all prep materials to Teams channel

## Questions & Assumptions

### Open Questions
- What does the SuccessFactors data schema look like for an individual employee? (anonymized)
- How frequently are internal profiles updated in SuccessFactors?
- What is the acceptable SLA for returning match results? (Rupali says "real-time" but no defined threshold)
- Do project managers / account managers need a UI, or is an API/chat interface sufficient?
- How many open roles exist at any given time? What's the volume of concurrent matching requests?
- Can the OptiFit ranker be reused as the second stage after the new retrieval layer?
- What does the existing Wipro tooling environment look like? (GitHub Copilot usage, VS Code config, Azure services — walkthrough deferred to later this week)

### Key Assumptions
- The hackathon targets the **retrieval stage** only (150K → ~200 candidates), not the full ranking pipeline
- Internal profile data is sparse (skills, role, location, projects) — not full resumes
- JDs for internal roles are also sparse — short parameter sets, not structured documents
- The underlying system is SuccessFactors, accessed via APIs
- A hybrid approach (background pre-computation + on-demand matching) is the likely architecture
- The workshop will produce a prototype and evaluation framework, not a production-ready system

### Risks & Concerns
- **No sample data available yet** — the team is refining the problem statement in the abstract, which limits the depth of technical design
- **Sparse internal profiles** may make semantic matching harder than traditional resume-JD matching — the signal is weaker with fewer text fields
- **SLA undefined** — "real-time" is aspirational but no concrete threshold exists, making it hard to set performance success criteria
- **Demo readiness** — Rupali is unsure what can be shown; if no demo materializes, understanding of the current process remains theoretical
- **Background re-indexing frequency** — needs to be defined but depends on data change patterns that are not yet understood

## Stakeholder Feedback & Alignment

### Positive Feedback
- Rupali is fully open to new approaches: "If you feel the solution is so unique that we don't even need [OptiFit], we are fine with that also"
- Jahan J and Anshuman brought strong technical framing (two-tower retrieval + ranker, hybrid caching, event-driven vs. frequency-based refresh) that Rupali validated
- The team converged on the hybrid architecture concept quickly — strong technical alignment

### Concerns Raised
- Deepthi confirmed this is a **greenfield problem** (no prior implementation for internal matching) — the workshop cannot build on existing code
- Shinoj emphasized that the **workshop is about learning HVE techniques**, not just solving this one problem — need to balance outcome delivery with skills transfer
- Pinki cautioned against over-scoping: start simple, take one slice, demonstrate the approach, then expand

### Alignment Status
- **High Alignment:** Problem is retrieval from 150K profiles with semantic matching; two-stage architecture (retrieval + ranking); hybrid pre-computation approach
- **High Alignment:** Workshop delivers a prototype + evaluation framework using HVE; Wipro takes learnings forward
- **High Alignment:** Demo tomorrow is the priority for the next standup
- **Medium Alignment:** Exact interaction channel for the workshop slice (JD upload vs. chat) — to be decided after seeing the demo
- **Medium Alignment:** How to handle accuracy/evaluation — Anshuman will present approaches, but specifics TBD
