# Meeting Notes: Wipro — HVE Workshop Daily Connect

## Meeting Information
- **Date:** 2026-04-13
- **Time:** 12:02 PM – 12:28 PM (25m 46s)
- **Meeting Type:** Scope Conversations / Logistics Planning

- **Current Design Thinking Method:** Method 1: Scope Conversations
- **Meeting Facilitator:** Pinki Dutta
- **Participants:**
  - Rupali Agarwal – Wipro (Product Owner / Use Case Lead)
  - Rishabh Mehrotra – Wipro (Developer, prediction analysis & agents)
  - Aritra Sengupta (Aniruddha) – Wipro (Developer, Python expertise)
  - Ankit Manjrekar – Wipro (Developer, AI/GenAI/agents, AI CIO team)
  - Rohan Verma – Wipro (Developer, ML/time-series forecasting, LangChain/agents) — remote
  - Pinki Dutta – ISE/Microsoft (Engagement Lead)
  - Shinoj Zacharias – ISE/Microsoft (Technical Lead)
  - Ginette Vellera – ISE/Microsoft
  - Ajay Pal Singh Chauhan – ISE/Microsoft

## Context & Objectives
- **Primary Objective:** First daily standup of the prep week — verify hackathon dates, meet the Wipro developer team, confirm access onboarding progress, and align on data and documentation needs
- **Secondary Objectives:** Request sample data (resumes, JDs) and OptiFit architecture docs; confirm team availability for daily recurring standups; set up shared MS Teams channel
- **Pre-meeting State:** Apr 10 follow-up had established daily standups from this week; Rupali was to finalize team composition and dates by Monday; environment onboarding had not yet started

## Key Insights & Discoveries

### Stakeholder Insights
- Wipro's preference is the **week of April 21st** for the hackathon, but contingent on environment access being sorted — fallback is week of April 27th
- Rupali will be the **product owner** for the use case; she needs to arrange travel to Bangalore (rest of the team is already Bangalore-based)
- Only Rupali was previously involved with OptiFit (early-phase discussions with MST); none of the developers have prior OptiFit experience

### User Needs & Behaviors
- Pinki emphasized the need for a **demo or workflow walkthrough** of the current process — how JD-to-resume matching happens today, what the input/output looks like, and where the challenges are
- Sample JDs and resumes from the internal database are needed to contextualize the problem and start defining queries, database structures, and NLP approaches
- A representative sample database is needed for the workshop itself

### Problem Space Insights
- The current process for internal talent matching may be entirely manual — Rupali was unsure and committed to checking
- The team needs to shape the use case using design thinking: define success metrics, quantitative outcomes, and the tangible result expected from the hackathon

### Solution Space Insights
- Wipro developer team has relevant skills: Python, agents, LangChain, GenAI, ML/time-series — well-suited for the hackathon's technical work
- ISE plans to introduce the **AI SDLC** and **HVE tooling** to the Wipro team, potentially through one of the daily prep calls before the workshop
- The HVE open-source deck has already been shared with Rupali for team self-study

### Implementation Space Insights
- **Access onboarding not yet initiated** — Rupali needs to connect with Samik's team today to start the process
- Conference rooms already booked at Microsoft FERNS office for whiteboarding and interactive sessions
- Most Wipro team members (Rishabh, Aritra, Ankit) are in Bangalore and can attend in-person; Rohan is remote

## Decisions Made

### Methodology Decisions
- **Decision:** Target hackathon date of **April 22-23-24** (shifted from 27th), with 21st also possible if access is ready
- **Rationale:** Wipro prefers the earlier week; Pinki proposed 22nd to allow one extra day for access provisioning over starting on 21st
- **Impact:** Travel planning for Rupali can proceed; room bookings at Microsoft FERNS confirmed

### Scope Decisions
- **Decision:** Use case shaping (success metrics, outcomes, parameters) will happen during this week's daily standups, informed by sample data and the demo
- **Rationale:** High-level scope is known but quantification and design thinking structuring still needed before the workshop
- **Impact:** Wipro to share sample JDs, resumes, and outcomes this week; technical deep-dives start once ISE devs join calls from tomorrow

### Next Steps Decisions
- **Decision:** Daily recurring standups at **12:00-12:30 PM** for the rest of this week with full team
- **Rationale:** All team members confirmed availability; ISE devs join from tomorrow for joint technical discussions
- **Impact:** Efficient use of limited prep time before workshop

- **Decision:** Set up a **shared MS Teams channel** for both teams to upload recordings, transcripts, and working documents
- **Rationale:** Email is impractical for large recordings; centralized channel improves collaboration
- **Impact:** Rupali to check if an existing channel can be reused or create a new one

## Action Items & Next Steps

### Immediate Actions (Next 1-2 days)
- [ ] **Initiate environment onboarding via Samik's team** – Assigned to: Rupali Agarwal – Due: 2026-04-13 (today)
- [ ] **Share Wipro team member details (name, role, location, in-person/remote)** – Assigned to: Rupali Agarwal – Due: 2026-04-13 (today)
- [ ] **Share sample resumes and JDs from internal database** – Assigned to: Rupali Agarwal – Due: 2026-04-14
- [ ] **Prepare demo or workflow walkthrough of current process** – Assigned to: Rupali Agarwal – Due: 2026-04-14
- [ ] **Share OptiFit latest architecture documentation** – Assigned to: Rupali Agarwal / Pinki Dutta (from ISE side) – Due: 2026-04-14
- [ ] **Confirm or create shared MS Teams channel** – Assigned to: Rupali Agarwal – Due: 2026-04-13
- [ ] **Share meeting recording/transcript with Wipro team** – Assigned to: Pinki Dutta – Due: 2026-04-13
- [ ] **Plan internal HVE/AI-SDLC intro session** – Assigned to: Shinoj Zacharias / Pinki Dutta – Due: during this week

### Method Progression
- [ ] **Complete Current Method:** Gather sample data, see demo, define success metrics and quantified outcomes for the use case
- [ ] **Prepare for Next Method:** Internal ISE planning for workshop agenda; schedule HVE intro session for Wipro developers
- [ ] **Stakeholder Follow-up:** Tomorrow's standup to include ISE developers; demo from Wipro expected

### Research & Validation
- [ ] **Research Tasks:** Understand current manual talent-matching process through demo; review representative data structures
- [ ] **Validation Activities:** Test environment access once onboarding is initiated
- [ ] **Documentation:** Upload all prep materials to shared Teams channel once created

## Questions & Assumptions

### Open Questions
- Is the current internal talent-matching process entirely manual, or is there an existing tool/workflow?
- What does the representative sample database look like (schema, volume, format)?
- Can the existing MS Teams channel from prior ISE-Wipro engagements be reused?
- When will environment access be provisioned — is the 22nd start date realistic?

### Key Assumptions
- Hackathon tentatively targeted for April 22-23-24, pending access readiness
- Wipro team: ~5 developers in Bangalore (in-person) + Rohan (remote) + Rupali (traveling)
- Workshop will be primarily at Microsoft FERNS office
- The HVE open-source materials shared earlier are being reviewed by the Wipro team

### Risks & Concerns
- **Access onboarding still not started** — Rupali hasn't yet connected with Samik's team; this is the critical-path blocker
- **No sample data yet** — discussions remain abstract without actual JDs and resumes to ground the technical approach
- **No demo of current process** — the team is designing a solution without seeing how things work today
- **Rupali's travel** — only team member not in Bangalore; needs to book travel once dates are firm

## Stakeholder Feedback & Alignment

### Positive Feedback
- Wipro developers expressed enthusiasm — Rohan: "Looking forward to it"; team has relevant agent/GenAI/Python experience
- Wipro team confirmed availability for all daily standups this week
- Rupali committed to prioritizing all action items today

### Concerns Raised
- Rishabh requested meeting recordings be shared so late-joining or absent team members stay informed
- Environment access is a recurring concern — still the top risk item carried forward from prior meetings

### Alignment Status
- **High Alignment:** Team composition finalized; daily standup cadence agreed; Microsoft FERNS office as venue
- **High Alignment:** Need for sample data, demo, and design thinking-based structuring before the workshop
- **Medium Alignment:** Exact hackathon dates — Wipro prefers 21st week, ISE prefers 22nd+ to allow access buffer
- **Medium Alignment:** HVE training for Wipro team — agreed in principle, timing to be determined this week
