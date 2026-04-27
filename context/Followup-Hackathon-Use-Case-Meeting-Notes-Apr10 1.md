# Meeting Notes: Follow-up — Hackathon Use Case

## Meeting Information
- **Date:** 2026-04-10
- **Time:** 9:01 AM – 9:33 AM (32m 30s)
- **Meeting Type:** Scope Conversations / Logistics Planning

- **Current Design Thinking Method:** Method 1: Scope Conversations
- **Meeting Facilitator:** Pinki Dutta
- **Participants:**
  - Rupali Agarwal – Wipro (Talent Matching / Optifit Lead)
  - Raju VN – Wipro (Senior Stakeholder / Decision Maker) — joined late, brief attendance
  - Pinki Dutta – ISE/Microsoft (Engagement Lead)
  - Ginette Vellera – ISE/Microsoft
  - Shinoj Zacharias – ISE/Microsoft (Technical Lead)
  - Mark D'Souza – ISE/Microsoft
  - Deepthi Sebastian – ISE/Microsoft

## Context & Objectives
- **Primary Objective:** Walk through the readiness checklist shared after the Apr 7 call; align on hackathon dates, team composition, environment access, and logistics
- **Secondary Objectives:** Clarify the relationship between OptiFit and the hackathon problem; confirm the single use case (resume-JD matching at scale) for the hackathon
- **Pre-meeting State:** Following the Apr 7 scoping call, Pinki had shared a readiness checklist with Wipro. Rupali had shared the use case document. Team composition and final dates were still pending. No environment onboarding had started.

## Key Insights & Discoveries

### Stakeholder Insights
- Raju VN confirmed strong commitment: "We really want to make it work" — he and Rupali spent significant time deliberating on the use case before this call
- Raju directed Rupali to leverage existing onboarding processes via Vinay and Samik, who have done vendor onboarding multiple times
- Raju is open to the team working at the Microsoft FERNS office for most of the hackathon days, as long as all development uses the Wipro environment (per the co-pilot innovation agreement clause)

### User Needs & Behaviors
- Rupali clarified the two-stage architecture need: the hackathon problem is the **pre-screening step** — narrowing 150,000 resumes down to ~200 focused candidates per JD, before OptiFit-style detailed screening kicks in
- "Practically it is not possible that against one JD I try and scan all 150,000 resumes" — the scale problem is about intelligent filtering, not brute-force scanning
- Business outcome and success metrics still need to be jointly defined; Rupali will update the use case document with proposed outcomes for joint finalization

### Problem Space Insights
- The hackathon problem is explicitly the **step before OptiFit**: how to filter 150,000 profiles down to a manageable set (~200-400) per JD at scale
- OptiFit handles the detailed screening/ranking of the narrowed set — that is a separate, parallel track
- There is no existing solution for this pre-screening/filtering step at scale; OptiFit only addresses the screening part
- The problem requires understanding what pre-processing or structuring of resume data can enable fast narrowing

### Solution Space Insights
- Deepthi noted that even OptiFit did some pre-processing and structuring of resumes to avoid scanning everything — there may be reusable patterns
- Shinoj requested an internal sync with the ISD team who built OptiFit before next discussions with Wipro, to understand what already exists
- The ISE team plans to introduce Wipro's team to the AI development lifecycle and HVE tooling (open source) during the prep phase

### Implementation Space Insights
- **Environment:** Wipro has VS Code, GitHub Copilot, Teams, sandbox/dev environment, and Azure available. All development must reside in the Wipro environment per contractual agreement
- **Onboarding process:** Samik and Vinay at Wipro know the vendor onboarding process; existing VDIs, Teams channels, and IDs from prior ISE engagements can be leveraged
- **Venue:** Primarily Microsoft FERNS office in Bangalore; Day 1 possibly at Wipro office for input from Manoj, then remaining days at Microsoft office. Rooms need to be booked
- **Data sensitivity:** Raju advised Rupali to create separate environments for sensitive data rather than mixing with existing setups

## Decisions Made

### Methodology Decisions
- **Decision:** Single use case confirmed for the hackathon — **resume-JD matching at scale** (the pre-screening/filtering problem)
- **Rationale:** Both use cases are priorities for Wipro, but the resume screening team is more likely to be in Bangalore; this is also Wipro's first co-engineering engagement, so starting with one use case is pragmatic
- **Impact:** The second use case is deferred to a subsequent hackathon or engagement

### Scope Decisions
- **Decision:** The hackathon focuses on the **pre-screening step** (150K → ~200 resumes per JD), not the detailed screening/ranking step (which OptiFit handles)
- **Rationale:** Rupali clarified that the scalability bottleneck is in narrowing the full database, not in the per-resume scoring
- **Impact:** Solution design should target intelligent filtering/bucketing approaches rather than improving per-profile scoring time

- **Decision:** Business outcomes and success metrics will be **jointly defined** — Rupali to propose, ISE to provide input
- **Rationale:** The proposed solution in the document is one-sided; quantified outcomes make success measurable
- **Impact:** The use case document will be updated with measurable outcomes before the hackathon

### Next Steps Decisions
- **Decision:** Hackathon dates likely shifting to **April 27-28-29** (from the originally tentative week of April 20th)
- **Rationale:** Deepthi flagged that proper prep (problem context alignment, data review, tooling intro, environment setup) requires more lead time; week of 27th gives two full prep weeks
- **Impact:** Final confirmation on Monday, April 13th, after team composition is known

- **Decision:** Daily standup calls starting week of April 13th, **30 min at 11:30 AM**, Monday through Friday until hackathon
- **Rationale:** Original 2 PM slot is during lunch for many team members; daily syncs ensure preparation stays on track
- **Impact:** Provides consistent touchpoint for both teams during the compressed prep window

- **Decision:** Venue will primarily be the **Microsoft FERNS office** (Bangalore), with possible Day 1 at Wipro
- **Rationale:** Customers at the Microsoft office are freed from day-to-day work distractions; Wipro agreed as long as all data/development stays in Wipro environment
- **Impact:** Room booking and logistics arrangements needed at FERNS office

## Action Items & Next Steps

### Immediate Actions (Next 1-2 weeks)
- [ ] **Finalize team members and share list** – Assigned to: Rupali Agarwal – Due: 2026-04-13 (Monday)
- [ ] **Confirm hackathon dates (20th vs 27th week)** – Assigned to: Rupali Agarwal – Due: 2026-04-13 (Monday)
- [ ] **Share Microsoft team email addresses for onboarding** – Assigned to: Pinki Dutta / Mark D'Souza – Due: 2026-04-10 (today)
- [ ] **Initiate environment onboarding via Vinay/Samik** – Assigned to: Rupali Agarwal – Due: 2026-04-13
- [ ] **Share OptiFit architecture/documentation (latest deployment state)** – Assigned to: Rupali Agarwal – Due: 2026-04-14
- [ ] **Gather existing OptiFit documentation from ISE side** – Assigned to: Pinki Dutta – Due: 2026-04-14
- [ ] **Schedule daily standup calls (11:30 AM) for week of April 13th** – Assigned to: Pinki Dutta – Due: 2026-04-10 (today)
- [ ] **Update use case document with proposed business outcomes/success metrics** – Assigned to: Rupali Agarwal – Due: before next call
- [ ] **Internal ISE sync with ISD team on OptiFit solution** – Assigned to: Pinki Dutta / Shinoj Zacharias – Due: before Monday standup
- [ ] **Book multi-purpose room at FERNS office for hackathon days** – Assigned to: Deepthi Sebastian – Due: after dates are confirmed

### Method Progression
- [ ] **Complete Current Method:** Finalize problem statement quantification and success metrics in the use case document
- [ ] **Prepare for Next Method:** Conduct internal ISE review of OptiFit architecture; introduce Wipro team to AI development lifecycle and HVE tooling during prep standups
- [ ] **Stakeholder Follow-up:** Monday standup with Rupali to freeze dates and team; connect with Vinay/Samik for onboarding process

### Research & Validation
- [ ] **Research Tasks:** Review OptiFit's pre-processing and data structuring approach for reusable patterns; understand the current filtering pipeline
- [ ] **Validation Activities:** Verify what sample data (resumes, JDs) Wipro can provide and in what format; test environment access once onboarding starts
- [ ] **Documentation:** Maintain shared checklist for preparation tracking; update use case document with joint outcomes

## Questions & Assumptions

### Open Questions
- What is the latest deployed state of OptiFit, and what architectural documentation exists?
- What pre-processing or data structuring does OptiFit already do that could be leveraged for the pre-screening step?
- What specific licenses and Azure services are available in the Wipro environment?
- Who from Wipro's team has data science skill sets vs. pure engineering?
- Can existing VDIs and Teams channels from prior ISE engagements be reused?
- What does Manoj need to provide as input on Day 1 at Wipro?

### Key Assumptions
- Hackathon dates are most likely April 27-28-29 (final confirmation Monday)
- Team size: 5-8 from Wipro, 4-6 from Microsoft ISE
- All development and data will reside in the Wipro environment per contractual agreement
- OptiFit's detailed screening is a parallel, separate track — not part of the hackathon deliverable
- A senior decision-maker from Wipro (Rupali or equivalent) will be present throughout the hackathon

### Risks & Concerns
- **Environment onboarding delays:** Access provisioning historically involves back-and-forth; with only ~2 weeks to hackathon, this is critical path
- **Team composition uncertainty:** Wipro team members not yet identified — skill mix (data science vs. engineering) will affect what can be accomplished
- **OptiFit knowledge gap:** The ISE hackathon team (Shinoj, Ginette) has not worked on OptiFit; an internal knowledge transfer is needed before the hackathon
- **Venue split:** Doing Day 1 at Wipro and rest at Microsoft adds logistical complexity
- **Business outcomes not quantified:** Without clear success metrics, it will be hard to evaluate hackathon outcomes

## Stakeholder Feedback & Alignment

### Positive Feedback
- Raju VN expressed strong commitment: "We really want to make it a good thing" — invested personal time deliberating with Rupali
- Rupali confirmed this is the start of a longer partnership: "This is not the only thing I hope we will be doing together. Many more to come"
- Wipro is cooperative on logistics — willing to come to Microsoft office, share documentation, and fast-track onboarding

### Concerns Raised
- Shinoj emphasized the need for an **internal ISE sync with ISD** before further Wipro discussions, to understand what was already built
- Deepthi flagged that starting the hackathon on the 20th may be too soon — proper prep (environment, tooling, problem alignment) requires more time
- Environment onboarding is a known friction point — Rupali asked about existing contacts to fast-track

### Alignment Status
- **High Alignment:** Single use case selected (resume-JD matching at scale); daily standups to begin; co-engineering model embraced by both sides
- **High Alignment:** Venue preference for Microsoft FERNS office with Wipro environment for development
- **Medium Alignment:** Hackathon dates — leaning toward April 27-28-29 but final decision pending team availability (Monday)
- **Medium Alignment:** Need to jointly define business outcomes and success metrics — Rupali to propose first draft
