# Open Questions & Scope Gaps — Job Agent

> **Purpose:** Track every known gap, unresolved question, and assumption in the project scope. Each item has a severity, status, and clear description of what needs to be decided or built. Nothing ships until the "Resolve Before Building" items are closed.
> **Created:** 2026-03-17
> **Complements:** PROJECT_NOTES.md (scoping), FEATURE_LANDSCAPE.md (tools), OPTIMIZATION_NOTES.md (token/cost)

---

## How to Use This Document

- **Severity levels:** `BLOCKING` (must resolve before any code), `HIGH` (must resolve before the affected feature), `MEDIUM` (should resolve during build), `LOW` (can defer to later phase)
- **Status:** `OPEN` (unresolved), `IN DISCUSSION` (actively being worked), `RESOLVED` (decision made — documented inline), `DEFERRED` (intentionally postponed with rationale)
- Items are numbered for easy reference in conversations and commits (e.g., "Resolves OQ-3")

---

## BLOCKING — Resolve Before Building

### OQ-1: User Profile & Identity Model

**Status:** RESOLVED (2026-03-17)
**Affects:** Resume tailoring, skill gap analysis, OSINT, job matching, dashboard — essentially everything

**The gap:** The system knows what features to build but hasn't defined who it's serving. Joseph's background spans multiple career domains — React/Next.js development, SOX audit and compliance, security research, legacy system maintenance, automation engineering, and contract/freelance work. This is not a single-persona job search.

**What needs to be defined:**

- [ ] **Master profile schema** — A structured representation of the user: skills (with proficiency levels), work history, education, certifications, target roles, preferences (remote/hybrid/onsite, salary range, location, W-2 vs. 1099), and career goals
- [ ] **Multi-persona support** — Can the user have multiple "search profiles" active simultaneously? (e.g., "Senior React Developer" profile vs. "IT Auditor" profile vs. "Freelance Automation Consultant" profile)
- [ ] **Profile ingestion** — How does the master profile get created? Manual entry? Parse an existing resume? Import from LinkedIn? Conversational setup wizard?
- [ ] **Profile evolution** — How does the profile update over time as the user learns new skills, completes projects, or changes goals?

**Why this is blocking:** Every downstream feature depends on knowing who the user is. The resume tailoring engine generates different output for a dev role vs. an audit role. The job matching scorer weights different skills. OSINT targets different companies and people. Without a profile model, we're building blind.

**Proposed schema (starting point):**

```yaml
user_profile:
  name: string
  email: string
  location: string
  
  # Career identity — supports multiple active personas
  personas:
    - id: string
      label: "Senior React Developer"
      target_roles: ["Frontend Engineer", "React Lead", "Full-Stack Developer"]
      target_industries: ["Tech", "Finance", "Healthcare"]
      work_arrangement: ["remote", "hybrid"]
      salary_range: { min: 120000, max: 180000, currency: "USD" }
      employment_type: ["W-2"]
      resume_version: "resume_react_v3.md"
      priority: "active"
      
    - id: string
      label: "IT Auditor / SOX Compliance"
      target_roles: ["IT Auditor", "SOX Analyst", "Compliance Analyst"]
      target_industries: ["Entertainment", "Finance", "Healthcare"]
      work_arrangement: ["onsite", "hybrid"]
      salary_range: { min: 90000, max: 140000, currency: "USD" }
      employment_type: ["W-2"]
      resume_version: "resume_audit_v2.md"
      priority: "active"
      
    - id: string
      label: "Freelance Automation Consultant"
      target_roles: ["Automation Engineer", "Python Developer", "Data Pipeline Engineer"]
      rate_range: { min: 75, max: 120, currency: "USD", unit: "hourly" }
      employment_type: ["1099", "contract"]
      resume_version: "resume_freelance_v1.md"
      priority: "passive"

  # Unified skill inventory (shared across personas)
  skills:
    - name: "React / Next.js"
      category: "Frontend Development"
      proficiency: 4  # 1-5 scale
      years: 3
      evidence: ["OpenClaw dashboard", "current W-2 role"]
    - name: "SOX Audit"
      category: "Compliance"
      proficiency: 3
      years: 1
      evidence: ["current W-2 role — transaction coding, tax compliance"]
    # ... etc

  # Work history (structured, used by tailoring engine)
  experience: [...]
  education: [...]
  certifications: [...]
```

**Decision needed from Joseph:**
1. Does the multi-persona approach match how you think about your job search?
2. Which personas are active right now?
3. Do you have a master resume (any format) we can use as the initial data source?

---

### OQ-2: Data Model / Schema Design

**Status:** OPEN
**Affects:** Every feature — this is the foundation

**The gap:** FEATURE_LANDSCAPE.md includes an entity-relationship sketch, but we have no actual SQLite schema, no foreign key relationships, no column types, no indexes, no migration strategy. Every feature writes to or reads from this data layer.

**What needs to be defined:**

- [ ] **Core entities and their columns** — Job, Application, Resume, Company, Person, Skill, SkillGap, Communication, Task, UserProfile, SearchPersona
- [ ] **Relationships** — Job→Application (1:many), Application→Resume (1:1 tailored version), Job→Company (many:1), Company→Person (1:many), Skill→SkillGap (1:many per JD comparison)
- [ ] **Status enums** — Application stages (discovered, saved, tailoring, ready, applied, phone_screen, interview, offer, accepted, rejected, withdrawn), Communication types (email, linkedin, phone, in_person)
- [ ] **Audit trail** — Every state change logged with timestamp, trigger (user/system), and context
- [ ] **Migration strategy** — How do we evolve the schema as features are added? Alembic? Manual versioned SQL scripts?
- [ ] **Soft deletes vs. hard deletes** — Job postings expire. Do we archive or delete?

**Why this is blocking:** If we start building features against ad-hoc data structures, we'll spend more time refactoring than building. The data model is the contract between all modules.

**Dependencies:** Resolving OQ-1 (user profile) feeds directly into this — we can't design the schema without knowing the profile structure.

---

### OQ-3: Master Resume Strategy

**Status:** OPEN
**Affects:** Resume tailoring (Feature 2), skill gap analysis (Feature 6), profile ingestion (OQ-1)

**The gap:** The resume tailoring pipeline is the highest-value Phase 1 feature, but we've never established:

- [ ] **What format is your current resume in?** (Word, PDF, plain text, Markdown, LaTeX, Google Docs?)
- [ ] **Do you have one resume or multiple versions?** (dev-focused, audit-focused, etc.)
- [ ] **What's the canonical source of truth?** Should the system treat a Markdown file as the master, or should it maintain a structured database representation that renders to any format?
- [ ] **What sections does your resume include?** (Summary, experience, skills, education, certifications, projects — we need to know what the parser must handle)
- [ ] **How do we handle "master resume" vs. "tailored resume"?** The master is the full kitchen-sink version. Tailored versions are subsets optimized for specific JDs. We need clear versioning.

**Proposed approach (pending your input):**

```
Master Resume (Markdown)          Tailored Versions (generated)
┌─────────────────────┐           ┌─────────────────────────┐
│ resume_master.md    │──parse──▶│ Structured JSON (DB)    │
│                     │           │ - sections[]            │
│ Full work history,  │           │ - skills[]              │
│ all skills, all     │           │ - experience[]          │
│ projects, every     │           │ - education[]           │
│ bullet point ever   │           └──────────┬──────────────┘
└─────────────────────┘                      │
                                    ┌────────┴────────┐
                                    │  Tailoring Engine │
                                    │  (Ollama + rules) │
                                    └────────┬────────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                        tailored_v1.md  tailored_v2.md  tailored_v3.md
                        (React Lead)   (IT Auditor)   (Freelance)
                              │              │              │
                              ▼              ▼              ▼
                        tailored_v1.pdf tailored_v2.pdf tailored_v3.pdf
```

**Decision needed from Joseph:**
1. What format is your resume in today?
2. Are you comfortable with Markdown as the canonical source?
3. How many distinct resume versions do you currently maintain?

---

### OQ-4: Integration Architecture (How Modules Connect)

**Status:** OPEN
**Affects:** Orchestration layer, browser automation ("Hand"), all features working together

**The gap:** We've researched tools in isolation — JobSpy for scraping, Camoufox for browser automation, Ollama for LLM, n8n for workflows, LangGraph for agent chains — but we haven't defined:

- [ ] **Who calls whom?** Does n8n trigger Python scripts? Does a Python orchestrator call n8n via webhook? Does LangGraph wrap everything?
- [ ] **How does the browser hand connect?** With Crawlee as the crawling framework (see FEATURE_LANDSCAPE.md §9), browser automation is now a `PlaywrightCrawler` invocation rather than a raw `browser_hand.py` call. But how does n8n or LangGraph trigger a Crawlee crawl? Subprocess? HTTP API? Message queue?
- [ ] **Where does Ollama sit in the call chain?** Is it called directly by Python modules, or routed through an abstraction layer (our existing `token_tracker.py`)?
- [ ] **How do modules share data?** Through SQLite directly? Through an internal API? Through filesystem (JSON files)?
- [ ] **Error propagation** — If JobSpy fails mid-scrape, how does the orchestration layer know? Retries? Dead letter queue? Dashboard alert?

**Proposed architecture (for discussion):**

```
                        ┌──────────────────┐
                        │   n8n (webhooks,  │
                        │   schedules,      │
                        │   email triggers) │
                        └────────┬─────────┘
                                 │ HTTP webhook / REST
                                 ▼
                        ┌──────────────────┐
                        │  Python Core     │
                        │  (CLI + API)     │
                        │                  │
                        │  Orchestrates:   │
                        │  - job_discovery │
                        │  - resume_tailor │
                        │  - osint_recon   │
                        │  - skill_gap     │
                        │  - browser_hand  │
                        └──┬───┬───┬───┬───┘
                           │   │   │   │
              ┌────────────┘   │   │   └────────────┐
              ▼                ▼   ▼                ▼
        ┌──────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Ollama   │   │ SQLite   │  │ Browser  │  │ OSINT    │
        │ (LLM)   │   │ (data)   │  │ Hand     │  │ Tools    │
        │          │   │          │  │          │  │          │
        │ via      │   │ direct   │  │ Camoufox │  │CrossLinked│
        │ token_   │   │ access   │  │ Nodriver │  │SpiderFoot│
        │ tracker  │   │          │  │ Pwright  │  │Harvester │
        └──────────┘   └──────────┘  └──────────┘  └──────────┘
```

**Key question:** Should the Python core be a **CLI tool** (invoke commands), a **FastAPI server** (always running, receives webhooks from n8n), or a **LangGraph agent** (decides its own actions)?

**Note (2026-03-17):** The adoption of Crawlee simplifies this decision. Crawlee crawlers are standalone async Python scripts that can be invoked from CLI, wrapped in a FastAPI endpoint, or called from a LangGraph node. They don't impose an architectural opinion on the caller.

**Decision needed from Joseph:**
1. Do you prefer starting with CLI commands (simple, testable) and adding the API/agent layer later?
2. Or do you want LangGraph orchestration from day one?

---

### OQ-5: Ethical & Legal Boundaries

**Status:** OPEN
**Affects:** Browser automation, application submission, OSINT, communication

**The gap:** Section 2.3 of PROJECT_NOTES flags this but we never resolved it. This isn't just a nice-to-have — it determines what features we build and how they behave.

**Specific questions to resolve:**

- [ ] **Automated application submission** — LinkedIn, Indeed, and most boards explicitly prohibit automated submissions in their ToS. Accounts get banned. What's the policy?
  - Option A: **"Prepare, don't submit"** — System does everything up to the submit button, then hands off to the human. Safest.
  - Option B: **"Submit with approval"** — System fills forms, human reviews in browser, human clicks submit. Middle ground.
  - Option C: **"Full auto with guardrails"** — System submits automatically but with rate limits, human review of first N applications, and kill switch. Riskiest.

- [ ] **OSINT data collection** — CrossLinked enumerates employees via Google/Bing dorking of LinkedIn. This is legal (public data) but ethically gray. SpiderFoot can go much deeper. Where's the line?
  - What data do we collect? (Name + title? Email? Social profiles? Phone?)
  - How long do we retain it?
  - Do we have a "right to forget" mechanism for people in our graph?

- [ ] **Recruiter communication** — Automated emails can violate CAN-SPAM if not careful. Even non-automated outreach at scale can damage reputation.
  - Always human-approved before sending?
  - Rate limits on outreach?

- [ ] **OPSEC / Identity compartmentalization** — You have security research interests (OpenClaw). Should this system use a separate identity/email from your OSINT work? Should browsing sessions be isolated?

**Proposed default policy (conservative):**

```
PHASE 1 POLICY:
- Applications: PREPARE ONLY. Never auto-submit. Dashboard shows 
  "ready to apply" with direct link to the application page.
- OSINT: Public data only (name, title, company, LinkedIn URL). 
  No email enumeration. No phone numbers. No social media scraping 
  beyond professional profiles.
- Communication: DRAFT ONLY. System generates email/message drafts. 
  Human copies and sends manually.
- Browser automation: Used for data COLLECTION only (reading job 
  postings, extracting company info). Never for form submission.
- Data retention: OSINT data auto-expires after 90 days unless 
  linked to an active pipeline entry.
- Logging: Every external action logged with timestamp and source.

PHASE 2+ (revisit after MVP):
- Consider "submit with approval" workflow
- Consider email sending via n8n (with human approval gate)
- Consider deeper OSINT with explicit user opt-in per scan
```

**Decision needed from Joseph:**
1. Does the conservative "prepare only" default match your comfort level for Phase 1?
2. Are there specific ethical lines you want drawn differently?
3. Should we compartmentalize identities (separate email/browser profile for job search vs. security research)?

---

## HIGH — Resolve Before Affected Feature Ships

### OQ-6: Deployment Topology

**Status:** OPEN
**Affects:** Browser automation, n8n hosting, Ollama connectivity, dashboard access
**Relevant phase:** Phase 1

**The gap:** We estimated "$10-20/mo for a VPS" but never decided where each component actually runs.

**Options:**

| Topology | Pros | Cons |
|----------|------|------|
| **A: All local** (your machine) | Zero cost, fast Ollama, easy debugging | Must be running to work, no remote dashboard access, browser automation needs your machine on |
| **B: Hybrid** (Ollama local + VPS for n8n/dashboard/browser) | Ollama stays free/fast, dashboard accessible anywhere, scheduled jobs run 24/7 | Split architecture complexity, Ollama needs network tunnel or API exposure |
| **C: All remote** (VPS for everything) | Always-on, clean separation | Ollama on a VPS = slow (no GPU) or expensive (GPU VPS), higher cost |
| **D: Hybrid with Tailscale/WireGuard** | Best of both: local Ollama + remote services connected via VPN | Setup complexity, depends on local machine uptime for LLM tasks |

**Compute Options (for VPS / on-demand workloads):**

| Provider | Spec | Cost | Best For |
|----------|------|------|----------|
| **Docker (local)** | Uses host resources | $0 | Phase 1 default — SpiderFoot, Crawlee workers, n8n all containerized alongside Ollama |
| **Hetzner Cloud CX22** | 2 vCPU, 4GB RAM, 40GB SSD | ~$4.50/mo (hourly billing) | Best price/performance for a dedicated VPS — handles n8n + SpiderFoot + browser automation |
| **Oracle Cloud Free Tier** | 4 ARM vCPU, 24GB RAM | $0 (always-free) | Incredible specs at zero cost — ARM requires verifying tool compatibility (SpiderFoot, Camoufox) |
| **Fly.io Machines** | On-demand, configurable | ~$0.003/hr (pay-per-second) | True ephemeral compute — spin up for OSINT scan, tear down after. Cheapest for infrequent workloads |
| **DigitalOcean Droplet** | 1 vCPU, 1GB RAM | ~$6/mo | Solid fallback, good API, slightly pricier than Hetzner |

**Additional considerations:**
- Camoufox on a VPS needs Xvfb (virtual display) for headed mode — 83% bypass headless, ~100% bypass headed
- n8n self-hosted needs 1-2GB RAM minimum
- Dashboard (Next.js) could be static export on Vercel (free) or VPS-hosted
- SQLite is a single file — works great locally, problematic for multi-service remote access
- SpiderFoot has an official Docker image — easiest path to local or remote deployment
- Oracle free tier ARM instances need compatibility testing but the 24GB RAM is unbeatable at $0

**Recommended phased approach:**
1. **Phase 1:** All local via Docker (Ollama + SpiderFoot + Crawlee + n8n in containers). Zero cost, fastest iteration.
2. **Phase 2:** Hybrid — Ollama stays local, move n8n + browser workers to Hetzner CX22 ($4.50/mo) or Oracle free tier for always-on scheduling.
3. **Phase 2+:** Fly.io Machines for on-demand OSINT scans if scan frequency is low (cheaper than a persistent VPS).

**Decision needed from Joseph:**
1. Do you have a preference? Your local machine has Ollama already.
2. Do you need the dashboard accessible from your phone/other devices?
3. How important is "always-on" (scheduled job checks even when your machine is off)?
4. Are you open to Oracle Cloud free tier (requires sign-up, ARM compatibility testing)?

---

### OQ-7: Multi-Role Search Pipeline

**Status:** OPEN
**Affects:** Job discovery, resume tailoring, dashboard
**Relevant phase:** Phase 1

**The gap:** You might search for React dev roles, audit roles, and freelance gigs simultaneously. The current pipeline design assumes one search at a time — one set of keywords, one matching profile, one resume template.

**What needs to be defined:**

- [ ] **Parallel pipelines** — Does each persona (OQ-1) get its own independent discovery → match → tailor pipeline?
- [ ] **Shared vs. separate dashboards** — One unified Kanban board with persona tags? Or separate boards per persona?
- [ ] **Cross-persona intelligence** — If a company shows up in both the "dev" and "audit" search, do we merge them? Show the overlap?
- [ ] **Resource allocation** — If running 3 personas, scraping frequency triples. Rate limit implications?

**Proposed approach:**
Each persona runs as a named pipeline with its own search config, but all data flows into one shared SQLite database with `persona_id` as a foreign key. The dashboard shows a unified view with persona filters.

---

### OQ-8: The Handoff UX ("Ready to Apply" → Human Action)

**Status:** OPEN
**Affects:** Dashboard, application tracking, user experience
**Relevant phase:** Phase 1

**The gap:** Phase 1's core value proposition is: "System prepares everything, human reviews and submits." But we haven't designed that handoff moment.

**When a job reaches "ready to apply" status, what does the user see?**

- [ ] **Dashboard card** — Tailored resume preview, match score, company OSINT summary, direct link to application page, "Mark as Applied" button?
- [ ] **Email/notification** — Daily digest of "ready to apply" jobs?
- [ ] **CLI output** — Print a formatted summary with links?
- [ ] **All of the above?**

**What information does the user need at the moment of decision?**

- Tailored resume (rendered PDF preview)
- Match score with explanation ("87% match — strong on React, missing Kubernetes experience")
- Company quick-look (size, industry, key people from OSINT, Glassdoor rating?)
- Application URL (direct link to the job posting's apply page)
- Cover letter draft (if applicable — see OQ-11)
- Any red flags ("This posting is 30 days old" or "Salary below your minimum")

**Decision needed from Joseph:**
1. What's your preferred "review and go" workflow?
2. Do you want to review on your phone, desktop, or both?

---

## MEDIUM — Resolve During Build

### OQ-9: Feedback Loop / Learning From Outcomes

**Status:** OPEN (deferred to Phase 2)
**Affects:** Job matching accuracy, resume tailoring quality
**Relevant phase:** Phase 2

**The gap:** The system tracks applications but never learns from outcomes. "I applied to 50 jobs, got 5 interviews — what made those 5 different?" This is where the system transitions from a tool to an intelligent agent.

**What a feedback loop would look like:**

```
Applied ──▶ Got Response? ──▶ Interview? ──▶ Offer?
  │              │                │              │
  ▼              ▼                ▼              ▼
Log outcome   Log outcome     Log outcome    Log outcome
  │              │                │              │
  └──────────────┴────────────────┴──────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │ Outcome Analyzer    │
              │                     │
              │ Correlate outcomes  │
              │ with:               │
              │ - Match score       │
              │ - Resume version    │
              │ - Keywords used     │
              │ - Company size      │
              │ - Time of apply     │
              │ - Referral vs cold  │
              │ - Tailoring quality │
              └─────────────────────┘
                          │
                          ▼
              Adjust scoring weights,
              resume templates, and
              targeting strategy
```

**Deferral rationale:** We need enough data (50+ applications with outcomes) before a feedback loop is meaningful. Phase 1 focuses on collecting that data correctly.

---

### OQ-10: Inbound Communication Tracking

**Status:** OPEN (deferred to Phase 2)
**Affects:** Communication management (Feature 5), pipeline tracking
**Relevant phase:** Phase 2

**The gap:** We draft outbound messages but don't monitor inbound responses. If a recruiter replies to your email, the system doesn't know about it. The application stays in "applied" status even though you're now in conversation.

**What would need to happen:**

- [ ] Gmail/Outlook API integration to monitor inbox
- [ ] Pattern matching to link incoming emails to pipeline entries (by company name, recruiter name, job title)
- [ ] Auto-update application status based on email content ("We'd like to schedule an interview" → move to "interviewing")
- [ ] Privacy implications of scanning personal email

**Deferral rationale:** This requires email API integration and NLP parsing — significant scope. Phase 1 relies on manual status updates.

---

### OQ-11: Cover Letter Generation

**Status:** OPEN
**Affects:** Resume tailoring pipeline, application readiness
**Relevant phase:** Phase 1 (simple) or Phase 2 (advanced)

**The gap:** FEATURE_LANDSCAPE.md covers resume tailoring extensively but doesn't mention cover letters. Many applications require them, and they're a separate generation task from the resume.

**Options:**

- **Phase 1 (simple):** Ollama generates a cover letter draft alongside the tailored resume. Same pipeline, extra output. Template-based with JD-specific customization.
- **Phase 2 (advanced):** Cover letter references OSINT data ("I noticed [Company] recently [news event], and my experience in [X] aligns well with..."). Personalized per company, not just per JD.

**Proposed:** Include basic cover letter generation in Phase 1. It's low incremental effort since the tailoring engine already has the JD parsed and the user profile loaded.

---

### OQ-12: OpenClaw Pattern Reuse

**Status:** OPEN
**Affects:** Graph DB (Kuzu), dashboard patterns (Next.js), document management
**Relevant phase:** Phase 1-2

**The gap:** We reference "reuse Kuzu + CocoIndex patterns from OpenClaw" but haven't specified what actually carries over vs. what's new.

**What OpenClaw has that might transfer:**

| OpenClaw Component | Job Agent Equivalent | Reusable? |
|--------------------|---------------------|-----------|
| Next.js dashboard | Pipeline dashboard | Yes — layout, auth, component patterns |
| Kuzu graph DB | Relationship graph (OSINT) | Yes — connection patterns, Cypher queries |
| CocoIndex | ? | Unclear — CocoIndex is for data indexing/retrieval, could be useful for JD similarity search |
| 800+ document management | Resume/JD storage | Possibly — document indexing patterns |
| Gephi visualization | Network visualization | Yes — export format, layout algorithms |

**Decision needed from Joseph:**
1. Is there specific code from OpenClaw you want to port?
2. Or is it more about applying the architectural patterns (Kuzu schema design, Next.js project structure)?

---

## LOW — Can Defer to Later Phases

### OQ-13: Salary / Compensation Intelligence

**Status:** OPEN (deferred)
**Affects:** Job matching, negotiation prep
**Relevant phase:** Phase 2-3

**The gap:** We score jobs by skill match but don't factor in compensation data. Many postings don't include salary. Tools like Levels.fyi, Glassdoor, and LinkedIn Salary Insights have data, but integrating it adds scope.

**What it would enable:**
- Filter jobs below salary minimum
- "This role typically pays $X at this company level"
- Negotiation ammunition when offers come

**Deferral rationale:** Salary data APIs are paid or unreliable. For MVP, the user can manually set salary expectations per persona (OQ-1) and the system filters against posted ranges when available.

---

### OQ-14: Interview Preparation Module

**Status:** OPEN (deferred)
**Affects:** Pipeline management, learning recommendations
**Relevant phase:** Phase 2-3

**The gap:** When an application moves to "interviewing," the system currently does nothing to help prepare. A future module could:
- Generate likely interview questions based on JD + company + role
- Create study guides for technical interviews
- Pull common questions from Glassdoor interview section
- Schedule prep reminders

**Deferral rationale:** Out of scope for MVP. The dashboard can show a simple "Interview prep needed" task for now.

---

### OQ-15: Rate Limiting & Anti-Ban Strategy

**Status:** OPEN
**Affects:** Browser automation, job scraping, OSINT
**Relevant phase:** Phase 1 (basic), Phase 2 (advanced)

**The gap:** We identified stealth browser tools but haven't defined:
- How many requests per hour per job board?
- Backoff strategy when rate limited?
- Proxy rotation policy?
- IP/fingerprint rotation frequency?
- Account health monitoring?

**Proposed defaults (conservative for Phase 1):**

| Source | Max Requests/Hour | Delay Between Requests | Proxy Required? |
|--------|-------------------|----------------------|-----------------|
| LinkedIn | 20 | 15-30 sec (random) | Recommended |
| Indeed | 30 | 10-20 sec (random) | Optional |
| Glassdoor | 20 | 15-30 sec (random) | Recommended |
| Greenhouse APIs | 60 | 5-10 sec | No |
| Company career pages | 30 | 10-20 sec | No |
| CrossLinked (OSINT) | 10 | 30-60 sec | Recommended |

---

### OQ-16: Data Privacy & GDPR Considerations

**Status:** OPEN (deferred)
**Affects:** OSINT data storage, communication tracking
**Relevant phase:** Phase 2

**The gap:** If this tool is ever open-sourced for others to use (or even for your own use in regulated industries), storing personal data about recruiters, hiring managers, and employees has GDPR/CCPA implications.

**What would need to happen:**
- Data retention policies (auto-expire OSINT data)
- Right to deletion (remove a person from the graph)
- Consent tracking (if contacting people, record basis for contact)
- Data export (user can export all their data)

**Deferral rationale:** For a single-user tool, this is low priority. Becomes important if the project is shared or commercialized.

---

## Resolution Log

> When an open question is resolved, move it here with the decision and date.

| OQ # | Resolved Date | Decision | Rationale |
|------|---------------|----------|-----------|
| OQ-1 | 2026-03-17 | Multi-persona YAML profile with O*NET integration. 4 personas (2 active, 2 passive), 30+ skills mapped to O*NET entities. File: `config/user_profile.yaml` | Bootstrapped from resume PDF + session context. User confirmed O*NET integration and multi-persona approach. |

---

## Cross-References

- **PROJECT_NOTES.md §2.3** — Original open questions list (subset of what's here)
- **FEATURE_LANDSCAPE.md** — Tool recommendations that depend on these decisions
- **OPTIMIZATION_NOTES.md** — Token/cost considerations that feed into OQ-6 (deployment)
- **Session log** — PROJECT_NOTES.md §9 tracks when these were discussed
