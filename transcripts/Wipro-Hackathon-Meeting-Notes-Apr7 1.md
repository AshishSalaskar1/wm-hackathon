# Meeting Notes: Follow-up with Wipro – Hackathon Use Case

## Meeting Information
- **Date:** 2026-04-07
- **Time:** 9:12 AM – 10:34 AM (1h 22m)
- **Meeting Type:** Stakeholder Interview / Scope Conversations

- **Current Design Thinking Method:** Method 1: Scope Conversations
- **Meeting Facilitator:** Pinki Dutta
- **Participants:**
  - Rupali Agarwal – Wipro (Talent Matching / Optifit Lead)
  - Raju VN – Wipro (Senior Stakeholder / Decision Maker)
  - Shinoj Zacharias – ISE/Microsoft (Technical Lead)
  - Pinki Dutta – ISE/Microsoft (Engagement Lead)
  - Ginette Vellera – ISE/Microsoft
  - Ajay Pal Singh Chauhan – ISE/Microsoft
  - Akshay Kumar Singh – ISE/Microsoft
  - Mark D'Souza – ISE/Microsoft
  - Deepthi Sebastian – ISE/Microsoft

## Context & Objectives
- **Primary Objective:** Clarify the hackathon problem statement, scope, and expected outcomes for the Wipro Intelligent Talent Screening use case
- **Secondary Objectives:** Align on hackathon logistics (dates, participants, tech stack, data access); distinguish the hackathon effort from the existing Optifit solution
- **Pre-meeting State:** Wipro had shared an initial use case document describing the talent-matching problem at scale (~150,000 employees). The existing Optifit system was known to be slow (2 min/profile, max 200 profiles) and only ~50-60% accurate. This was the first deep-dive call to scope the hackathon engagement.

## Key Insights & Discoveries

### Stakeholder Insights
- Raju VN (senior stakeholder) is the primary decision maker on Wipro's side; Rupali Agarwal is the operational lead managing the Optifit system and data
- Raju emphasized this is a **co-innovation** engagement — not a one-sided delivery. Both Microsoft and Wipro should contribute to the proposed solution
- Wipro's business stakeholders (talent acquisition leadership) have already expressed the need for massive scale: the original ask was to scan 500,000 resumes, later scoped down to 2,000 in the pilot
- Demand prioritization is handled by Wipro's talent supply chain team (star-rating mechanism) — this is out of scope for the hackathon

### User Needs & Behaviors
- For any open job role, the system needs to scan all employee profiles and suggest ranked candidates based on top 3-4 criteria
- Business expects **top-10 ranked candidates per JD** with a **70-75% match threshold** below which resumes are not considered
- Recruiter workflow: receive bucketed results (90%+, 80-90%, <80%) and make final selection decisions from the top bucket
- A feedback mechanism from project managers is needed but currently nonexistent

### Problem Space Insights
- **Scale is the primary problem:** The current Optifit system is bottlenecked at 200 profiles × 2 min/profile — not feasible for 150K employees
- **Data quality is a known issue but explicitly out of scope for this hackathon.** The focus is on scaling, not data cleaning or accuracy fine-tuning
- Optifit has not been tested on the internal employee database; accuracy (~50-60%) was estimated, not validated at scale
- JD completeness is also a challenge — JDs are assumed to be at minimum 70% complete
- Skill representation is highly variable and fragmented across profiles

### Solution Space Insights
- Raju proposed a **resume specialization** concept: for a senior employee with 25 years of experience who could fill 6 different roles, generate 5 distinct role-specific resume versions so matching is more targeted — open for debate with the technical team
- Target outcome: **50X to 100X improvement** over current processing capability (e.g., scanning 100K+ resumes in a day)
- Pre-filtering/bucketing approach preferred: filter before deep scanning to reduce the candidate pool to a manageable number for detailed ranking
- Accuracy vs. scaling tension: Ajay raised that even for top-10 ranking, some labelled data or quality benchmark is needed. Raju acknowledged this is an open question, to be addressed with a feedback mechanism post-implementation

### Implementation Space Insights
- This is a **separate track from Optifit** — the hackathon should treat this as a fresh scaling problem, not an improvement of the existing system
- Optifit production testing will proceed in parallel on a separate track (Sumankar's team demoing to talent acquisition leadership)
- An evaluation framework for accuracy was previously proposed to the ISD team for Optifit's external candidate flow — not carried into this effort
- Duplicate/overlapping candidates across multiple JDs is a very likely real-world problem (e.g., 100+ React developers in Bangalore all ranking the same for similar JDs). Handling this is deferred as out of scope but flagged for future consideration

## Decisions Made

### Methodology Decisions
- **Decision:** Focus the hackathon on **scaling the matching capability**, not on data quality or accuracy fine-tuning
- **Rationale:** Business stakeholders have prioritized the ability to scan a much larger pool of resumes. Accuracy improvements can be iteratively addressed once the system can process at scale
- **Impact:** The hackathon solution design will center on throughput and performance rather than data normalization or model fine-tuning

### Scope Decisions
- **Decision:** The hackathon is a **separate effort from Optifit**; treat as a fresh solution for the scaling problem
- **Rationale:** Optifit is on a parallel track with its own production testing timeline and team. Conflating the two would slow both efforts
- **Impact:** The hackathon team is free to propose entirely new architectures without being constrained by Optifit's existing design

- **Decision:** Demand prioritization (multi-JD candidate overlap) is **out of scope**
- **Rationale:** This is handled by Wipro's existing talent supply chain team's prioritization mechanism
- **Impact:** The hackathon solution assumes a single-JD-at-a-time matching model

### Next Steps Decisions
- **Decision:** Target hackathon dates of **April 20-22 (week of April 20th)**, 3-day workshop
- **Rationale:** Hard constraint — all workshops must conclude before April 29th due to team allocation changes
- **Impact:** Only ~2 weeks for preparation; requires rapid coordination on data access, environment setup, and team identification

- **Decision:** At least **50% of technical participants should be in-person in Bangalore**
- **Rationale:** Hands-on co-innovation is more effective with physical co-location
- **Impact:** Travel logistics needed for remote participants

## Action Items & Next Steps

### Immediate Actions (Next 1-2 weeks)
- [ ] **Send readiness checklist to Wipro** – Assigned to: Pinki Dutta – Due: 2026-04-07
- [ ] **Share ISE team member names for onboarding** – Assigned to: Pinki Dutta – Due: 2026-04-07
- [ ] **Share the use case document with ISE team for offline brainstorming** – Assigned to: Rupali Agarwal – Due: 2026-04-08
- [ ] **Confirm follow-up call date/time (Thursday or Friday)** – Assigned to: Rupali Agarwal – Due: 2026-04-08
- [ ] **Identify Wipro hackathon participants (names, roles, skill sets)** – Assigned to: Rupali Agarwal / Raju VN – Due: 2026-04-10
- [ ] **Confirm final hackathon dates (week of April 20th)** – Assigned to: Rupali Agarwal – Due: 2026-04-10
- [ ] **Set up series of daily standup calls leading up to April 21st** – Assigned to: Rupali Agarwal – Due: 2026-04-11

### Method Progression
- [ ] **Complete Current Method:** Finalize scope and problem statement through readiness checklist and follow-up calls
- [ ] **Prepare for Next Method:** Gather sample data, confirm dev environment access, determine tech stack and licensing
- [ ] **Stakeholder Follow-up:** Follow-up call with Rupali to walk through the readiness checklist; coordinate access and logistics

### Research & Validation
- [ ] **Research Tasks:** Explore Azure AI Search and other Azure services for high-throughput resume-JD semantic matching at scale
- [ ] **Validation Activities:** Determine if Wipro has data science personnel who can participate; assess whether sample data is available and accessible
- [ ] **Documentation:** Maintain shared document (checklist) where both teams track preparation completeness

## Questions & Assumptions

### Open Questions
- What is the actual tech stack Wipro's team will be working on, and what licenses do they have?
- What sample data (resumes, JDs) will be available for the hackathon, and in what format?
- Is resume specialization (generating role-specific views of a single profile) a viable pre-processing step, or does it add unnecessary complexity?
- How will accuracy be measured without labelled data or a feedback mechanism in place?
- What environment access is needed and what is the coordination process for provisioning?

### Key Assumptions
- Job descriptions are at least 70% complete
- The hackathon targets a single-JD matching scenario (not multi-JD simultaneous matching)
- Optifit production testing will proceed independently on a parallel track
- The hackathon aims for a 50-100X throughput improvement as the success metric
- Wipro's demand prioritization mechanism handles candidate overlap across JDs

### Risks & Concerns
- **Tight timeline:** Only ~2 weeks to prepare for a 3-day workshop; access provisioning and data readiness are critical-path items
- **Data readiness:** Unstructured, fragmented employee data may not be available in a usable format for the hackathon
- **Accuracy vs. scale trade-off:** Deferring accuracy validation could result in a fast but unreliable solution that doesn't gain stakeholder trust
- **In-person attendance:** Uncertainty on whether Rupali (key Wipro lead) can travel to Bangalore for the workshop

## Stakeholder Feedback & Alignment

### Positive Feedback
- Strong alignment that this is a **co-innovation** effort — both teams contributing
- Wipro leadership (Raju) is decisive and pragmatic about scoping: clear on what's in and out of scope
- Business case is well understood and supported at the talent acquisition leadership level

### Concerns Raised
- Akshay raised that **scaling without accuracy benchmarks** risks delivering unusable results — flagged but deferred
- Ajay highlighted the need for **labelled data** to validate ranking quality — acknowledged as an open question
- Shinoj questioned whether **data quality issues** need to be addressed first — Raju directed focus to scale, quality to follow

### Alignment Status
- **High Alignment:** The hackathon is about scaling resume-JD matching throughput, not improving Optifit
- **High Alignment:** 3-day workshop format, week of April 20th, with in-person preference in Bangalore
- **Medium Alignment:** How to handle accuracy validation — Wipro wants to defer, ISE team sees risk in doing so
- **Low Alignment:** Resume specialization concept (Raju's proposal) — needs technical debate and validation
