# Job Agent — Project Scoping & Notes

> **Status:** Early scoping — refining prompt and defining scope before architecture decisions.
> **Last updated:** 2026-03-17
> **Owner:** josephdunivanucf@gmail.com

---

## 1. Vision (Original Prompt, Preserved)

An autonomous agent system that manages the full lifecycle of a job search:

- **Application automation** — discover, filter, tailor, and submit job applications
- **Recruiter communication** — own email/message threads with recruiters and hiring managers
- **Dashboard & task management** — track pipeline, statuses, deadlines, action items
- **Learning recommendations** — identify skill gaps and recommend courses, projects, or certifications
- **OSINT-powered networking** — use open-source intelligence tools to map relationship networks, recommend social outreach, discover relevant events, and find warm paths to target roles
- **Resume alignment** — automatically tailor resume to each individual job posting
- **Portfolio project generation** — recommend and help complete projects that demonstrate key learnings and translatable skills
- **Freelance/contract management** — in some cases, take on actual work for portfolio use, managing payments and contracts
- **Open source first, low cost** — prioritize self-hosted OSS tools over paid SaaS

---

## 2. Scope Refinement — Questions & Decisions Needed

### 2.1 Core vs. Stretch Goals

The vision covers a huge surface area. We should define what's **MVP** (Phase 1) vs. what's **Phase 2+**.

**Proposed Phase 1 (MVP):**
1. Job discovery & filtering (scrape boards, match against profile)
2. Resume tailoring per job (auto-align resume to JD)
3. Application tracking dashboard (status pipeline, deadlines)
4. Basic OSINT people lookup (who's at the company, who do I know nearby)
5. Skill gap analysis (compare my resume to JD, recommend learning)

**Proposed Phase 2:**
6. Automated application submission (browser automation, form filling)
7. Recruiter communication management (email drafts, follow-ups)
8. Event/meetup discovery and outreach recommendations
9. Relationship graph visualization (Gephi-style network maps)

**Proposed Phase 3:**
10. Portfolio project generation & completion assistance
11. Freelance contract/payment management
12. Full autonomous apply-to-interview pipeline

### 2.2 Key Decisions to Make

| # | Question | Options | Notes |
|---|----------|---------|-------|
| 1 | **Orchestration layer** | n8n (self-hosted) vs. custom Python pipelines vs. LangGraph | n8n has 400+ integrations, visual builder, AI agent nodes, self-hostable, free. LangGraph is more code-native. Custom Python is most flexible but most work. |
| 2 | **OSINT toolkit** | SpiderFoot (Python, MIT, 200+ modules) vs. custom OSINT scripts vs. OSINTBuddy | SpiderFoot is the most mature open-source option. Can search people, companies, emails, social profiles. |
| 3 | **Graph/relationship DB** | Kuzu (embedded, open source) vs. Neo4j Community vs. SQLite + custom | You already explored Kuzu with CocoIndex for OpenClaw. Could reuse that pattern. |
| 4 | **Resume format & tailoring** | Markdown → PDF pipeline vs. LaTeX vs. DOCX generation | Markdown is most flexible for programmatic manipulation. Can render to PDF via Pandoc or weasyprint. |
| 5 | **LLM backend** | Ollama (local) vs. OpenRouter (cheap API) vs. hybrid | You have Ollama locally. Good for resume tailoring and analysis. API fallback for heavy lifting. |
| 6 | **Frontend** | Next.js dashboard vs. n8n's built-in UI vs. CLI-first | You know Next.js well. Could start CLI → add dashboard later. |
| 7 | **Job board sources** | LinkedIn, Indeed, Glassdoor, Wellfound, company career pages, GitHub Jobs | ApplyPilot covers 5+ boards. Could study their approach. |
| 8 | **Data storage** | SQLite (simple) vs. PostgreSQL (scalable) vs. Supabase (free tier) | SQLite for MVP, migrate later if needed. |

### 2.3 Open Questions

- **Ethical/legal boundaries:** Automated applying can get accounts flagged. What's the risk tolerance? Should Phase 1 be "prepare everything, human clicks submit"?
- **Identity/OPSEC:** You have OPSEC interests — should this system compartmentalize identities or operate transparently?
- **Target job types:** Software dev roles? Audit/compliance roles? Freelance gigs? All of the above?
- **Resume source:** Do you have a master resume in a specific format already?
- **Existing accounts:** Which job boards do you already have accounts on?
- **Budget:** What's the monthly budget ceiling for hosting/APIs? ($0? $20? $50?)

---

## 3. Landscape Analysis — Existing Projects

### 3.1 Job Application Agents (Open Source)

| Project | What It Does | Stack | Status |
|---------|-------------|-------|--------|
| **AIHawk** (feder-cr/Jobs_Applier_AI_Agent_AIHawk) | Auto-applies to jobs on LinkedIn and other boards. Core is open source but provider plugins removed. Commercial version at laboro.co. | Python, AI-powered | Active, partially commercialized |
| **ApplyPilot** (Pickle-Pixel/ApplyPilot) | 6-stage autonomous pipeline: discover → score → tailor resume → write cover letter → submit. 1,000 apps in 2 days. | Python, browser automation | Active (v0.3.0, Feb 2026) |
| **job-app** (AloysJehwin/job-app) | n8n workflow: extract resume data, match jobs, rewrite resume, store in Google Drive/Sheets. | n8n, LangChain, DeepSeek | Active |
| **ai-job-apply-agent** (chapagainmanoj) | Claude-powered: resume parse → skill match → cover letter → recruiter Q&A. LangGraph workflow. | Python, Claude, LangGraph | Early stage |

**Key takeaway:** None of these combine OSINT/networking intelligence with job application. That's our differentiator.

### 3.2 OSINT Tools (Open Source, Relevant to Job Agent)

| Tool | Use For Us | License | Notes |
|------|-----------|---------|-------|
| **SpiderFoot** | People search, company recon, social profile discovery, email/domain enumeration | MIT | Python, 200+ modules, web UI, CLI. Best general-purpose OSINT tool. |
| **Maltego CE** | Graph-based link analysis, relationship mapping | Freemium (Community Edition free) | Visual graph tool. Not fully open source but free tier available. |
| **Gephi** | Network visualization, community detection, centrality analysis | GPL | You already know this from OpenClaw work. Great for relationship graphs. |
| **theHarvester** | Email and subdomain enumeration for target companies | GPL | Quick company recon tool. |
| **OSINT Framework** | Curated directory of OSINT tools by category | Free | Good reference for finding specialized tools. |
| **OSINTBuddy** | Open source Maltego alternative with node graphs | Open source | Newer, less mature but promising. |
| **Recon-ng** | Modular web reconnaissance framework | GPL | Good for automated data collection pipelines. |

### 3.3 Orchestration / Workflow

| Tool | Fit | Cost |
|------|-----|------|
| **n8n** (self-hosted) | Visual workflow builder, 400+ integrations, AI agent nodes, webhook support | Free (self-hosted), ~$20/mo server |
| **LangGraph** | Code-native agent orchestration, good for multi-step AI workflows | Free (Python library) |
| **Temporal** | Durable workflow execution, retries, long-running tasks | Free (self-hosted), complex setup |
| **Custom Python** | Maximum flexibility, minimum dependencies | Free |

---

## 4. Proposed Architecture Direction (Draft — Not Final)

```
┌─────────────────────────────────────────────────┐
│                  Job Agent System                │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌───────────┐  ┌───────────┐  ┌────────────┐  │
│  │ Discovery │  │  OSINT    │  │  Resume    │  │
│  │ Engine    │  │  Recon    │  │  Tailorer  │  │
│  │           │  │           │  │            │  │
│  │ Job boards│  │SpiderFoot │  │ LLM-based  │  │
│  │ RSS feeds │  │People map │  │ alignment  │  │
│  │ Career pg │  │Company    │  │ MD → PDF   │  │
│  └─────┬─────┘  └─────┬─────┘  └──────┬─────┘  │
│        │              │               │         │
│        ▼              ▼               ▼         │
│  ┌─────────────────────────────────────────┐    │
│  │         Orchestration Layer             │    │
│  │    (n8n self-hosted OR LangGraph)       │    │
│  └─────────────────┬───────────────────────┘    │
│                    │                            │
│        ┌───────────┼───────────┐                │
│        ▼           ▼           ▼                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │ SQLite / │ │ Graph DB │ │ Next.js  │        │
│  │ Postgres │ │ (Kuzu)   │ │Dashboard │        │
│  │          │ │          │ │          │        │
│  │Jobs, apps│ │People,   │ │Pipeline  │        │
│  │comms,    │ │companies │ │viz, tasks│        │
│  │tasks     │ │networks  │ │analytics │        │
│  └──────────┘ └──────────┘ └──────────┘        │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │           LLM Layer (Ollama)            │    │
│  │  Resume tailoring, skill gap analysis,  │    │
│  │  cover letters, communication drafts    │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 5. What Makes This Different

Most existing job agents are **apply bots** — they spam applications. Our system is a **career intelligence agent** that:

1. **Maps the landscape** — uses OSINT to understand who's at target companies, what events are happening, what warm paths exist
2. **Builds relationships** — recommends outreach, tracks interactions, identifies mutual connections
3. **Develops the candidate** — identifies skill gaps, recommends projects, builds portfolio
4. **Manages the pipeline** — from discovery through negotiation, not just "click apply"
5. **Learns over time** — tracks what works (which tailoring gets responses, which outreach converts)

---

## 6. Decisions Made (2026-03-17)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **MVP Focus** | Balanced — resume tailoring + job matching + basic OSINT + dashboard | Get useful output fast without being just another apply bot |
| **Budget** | ~$50/mo | Comfortable for small VPS (n8n, services) + minimal API. Ollama local for heavy LLM work |
| **Target Roles** | User will specify per search | System should be flexible enough for dev, audit, and freelance |
| **Orchestration** | Flexible / best tool per job | No single orchestration lock-in. Use n8n where visual workflows help, LangGraph where code-native agents make sense, Ollama for local LLM tasks, simple Python scripts where that's sufficient |

## 7. Testing Strategy

Our testing approach follows the same philosophy you used in your SOX audit work and automation projects: define expected outcomes, simulate realistic scenarios (both valid and invalid), capture evidence, and validate that every component behaves correctly under real-world conditions.

### 7.1 Testing Principles

1. **Simulated data first** — Every module gets a set of synthetic test fixtures (fake job postings, fake resumes, fake company profiles) before touching real data. This lets us iterate fast without side effects.
2. **Happy + unhappy paths** — For each feature, test what should work AND what should fail/degrade gracefully (bad input, API down, rate limited, no results found).
3. **Audit trail on everything** — Every action the agent takes gets logged with timestamp, input, output, and outcome. This is both a testing aid and a core product feature.
4. **Human-in-the-loop checkpoints** — Before any external action (submitting an application, sending a message), the system pauses for review. Tests validate that this gate works.
5. **Regression via fixtures** — Save real-world inputs that caused bugs as permanent test fixtures so they never regress.

### 7.2 Testing by Module

#### Resume Tailoring Engine

| What to Test | Method | Pass Criteria |
|-------------|--------|---------------|
| Resume parsing (MD → structured data) | Unit tests with 5+ resume variants (different formats, lengths, missing sections) | All key fields extracted correctly |
| JD parsing (extract requirements, skills, keywords) | Unit tests with 10+ real job descriptions across dev/audit/freelance | Skills, requirements, and seniority level correctly identified |
| Alignment quality | LLM-as-judge evaluation: feed original resume + JD + tailored resume to a second LLM, score on relevance, accuracy, no hallucinated experience | Score ≥ 8/10 on relevance; zero hallucinated credentials |
| ATS compatibility | Run output through open-source ATS simulators or parsers (e.g., pyresparser) | All key fields parse correctly; no formatting artifacts |
| Markdown → PDF rendering | Visual regression tests: render 10 tailored resumes, screenshot, diff against baseline | No broken layouts, truncated text, or missing sections |
| Edge cases | Empty resume, resume with no matching skills, JD in another language, extremely long JD | Graceful degradation with clear error messages |

#### Job Discovery & Matching

| What to Test | Method | Pass Criteria |
|-------------|--------|---------------|
| Board fetching | Integration tests against each source (with mocked HTTP responses for CI, live for manual) | Returns structured job objects with title, company, location, JD, URL |
| Deduplication | Feed identical jobs from multiple boards | No duplicates in output |
| Match scoring | Score 50 test jobs (manually labeled as good/bad fit) against a fixed profile | Precision ≥ 80%, recall ≥ 70% on "good fit" label |
| Filtering (location, salary, remote, seniority) | Unit tests with 20 jobs spanning all filter dimensions | Filters correctly applied, edge cases (missing salary, ambiguous location) handled |
| Rate limiting / anti-bot | Simulate blocked responses, CAPTCHAs, 429s | System backs off, logs the event, retries with delay, never crashes |

#### OSINT / People Intelligence

| What to Test | Method | Pass Criteria |
|-------------|--------|---------------|
| Company lookup | Query 10 known companies, verify returned data (size, industry, key people) | Core facts match public records |
| People search | Query 5 known professionals, verify profiles found | Correct person identified with ≥ 3 data points |
| Relationship mapping | Feed a known network (e.g., 3 companies with overlapping employees) | Graph correctly shows connections |
| Privacy / ethical boundaries | Attempt to query sensitive data (SSN-like patterns, private records) | System refuses with clear explanation |
| SpiderFoot integration | Run 3 scans (domain, email, company name), validate structured output | Results parse into our data model without errors |
| False positive rate | Review 20 OSINT results manually | < 20% false positives (wrong person, stale data) |

#### Dashboard & Pipeline Tracking

| What to Test | Method | Pass Criteria |
|-------------|--------|---------------|
| Application status transitions | Unit tests: move a job through every valid state (discovered → applied → interviewing → offer → rejected) | All transitions work; invalid transitions blocked |
| Data integrity | Create 100 test applications, verify counts, filters, and aggregations on dashboard | Numbers match, no orphaned records |
| Task/deadline management | Create tasks with due dates in past, today, future | Correct sorting, overdue flagging, notification triggers |
| Concurrent operations | Simulate 5 simultaneous updates to different applications | No data corruption or race conditions |

#### LLM Layer (Ollama)

| What to Test | Method | Pass Criteria |
|-------------|--------|---------------|
| Model availability | Health check: is Ollama running, is the expected model loaded | Returns model info within 5 seconds |
| Response quality | Run 20 standardized prompts (cover letter, skill gap, resume bullet rewrite), evaluate outputs | Coherent, relevant, no hallucinations, correct tone |
| Fallback behavior | Kill Ollama mid-request; test with wrong model name | Graceful error, retry logic, user notification |
| Token/cost tracking | Log token counts for 50 operations | Accurate counts; average cost per operation calculated |
| Prompt versioning | Change a prompt template, verify output changes | Old fixtures still produce acceptable output; new prompt logged with version |

#### Orchestration & Integration

| What to Test | Method | Pass Criteria |
|-------------|--------|---------------|
| End-to-end pipeline | Feed 1 real job URL → system discovers, parses, scores, tailors resume, creates dashboard entry | All steps complete; output is reviewable |
| Partial failure recovery | Kill a service mid-pipeline (e.g., Ollama dies during tailoring) | Pipeline pauses, logs error, resumes when service returns |
| Data flow between modules | Trace a job from discovery → OSINT → matching → tailoring | Data model consistent at every handoff point |
| Configuration changes | Change target role, location filters, model name | System picks up new config without restart |

### 7.3 Test Infrastructure

| Layer | Tool | Purpose |
|-------|------|---------|
| Unit tests | pytest | Core logic: parsers, scorers, data transforms |
| Integration tests | pytest + Docker Compose | Multi-service: DB + LLM + OSINT working together |
| LLM evaluation | Custom eval harness (LLM-as-judge) | Quality of generated content (resumes, cover letters, analysis) |
| Visual regression | Playwright + screenshot diffing | Dashboard UI and rendered PDF output |
| Load / stress | locust or custom scripts | How the system behaves under 100+ concurrent jobs |
| CI/CD | GitHub Actions | Run unit + integration tests on every push |
| Fixtures | `/tests/fixtures/` directory | Synthetic resumes, JDs, company profiles, OSINT results |
| Test data generator | Python script using Faker + LLM | Generate realistic but synthetic test data at scale |

### 7.4 Quality Gates

No feature ships to `main` unless:

1. All unit tests pass
2. Integration tests pass against Docker Compose test environment
3. LLM output quality score ≥ threshold for affected prompts
4. No regressions in existing fixture tests
5. Manual review of 3 sample outputs for any LLM-touching feature

### 7.5 Testing Phases (aligned with build phases)

- **Phase 1 (MVP):** Unit tests + fixtures + basic integration tests. Manual QA on LLM outputs. GitHub Actions CI for unit tests.
- **Phase 2 (Automation):** Add Playwright for browser automation tests. LLM-as-judge eval harness. Visual regression for dashboard.
- **Phase 3 (Full Pipeline):** End-to-end pipeline tests. Stress testing. Monitoring and alerting for production runs.

---

## 8. Next Steps

- [x] Finalize Phase 1 scope
- [x] Set up the GitHub repo with this document
- [ ] Define data models (jobs, applications, contacts, companies, skills)
- [ ] Create initial project structure with module stubs
- [ ] Set up local dev environment (Docker Compose for services)
- [ ] Build first feature: resume tailoring engine (Ollama + MD→PDF pipeline)
- [ ] Build second feature: job discovery + matching

---

## 9. Session Log

### 2026-03-17 — Initial Scoping Session

- Captured full vision from user prompt
- Researched existing open-source job agents: AIHawk, ApplyPilot, job-app, ai-job-apply-agent
- Researched OSINT tools: SpiderFoot, Maltego, Gephi, theHarvester, OSINTBuddy, Recon-ng
- Researched orchestration: n8n (self-hosted), LangGraph, Temporal
- Identified key differentiator: OSINT + networking intelligence combined with job automation (no existing project does this)
- Proposed 3-phase approach: MVP → automation → full autonomous pipeline
- Created this PROJECT_NOTES.md as living document
- **Open:** Need to answer scoping questions before architecture decisions
- **Resolved:** MVP = balanced (resume tailoring + job matching + basic OSINT + dashboard). Budget ~$50/mo. Orchestration = flexible, best tool per job. No single lock-in.
- Added comprehensive testing strategy (§7) covering all modules, test infrastructure, quality gates, and phased rollout

### 2026-03-17 — Feature Landscape Research (Session 2)

- Researched tool landscape across all 8 planned feature areas
- Identified key OSS tools: JobSpy (job scraping), CrossLinked/SpiderFoot (OSINT), OpenResume/ATS-Scorer (resume), Pandoc+WeasyPrint (rendering), Invoice Ninja (freelance), Plane (project mgmt reference)
- Researched orchestration patterns: n8n has pre-built job application pipeline templates, LangGraph provides agent workflow patterns (orchestrator-worker, evaluator loops)
- Investigated skill ontology approaches: O*NET public taxonomy, skills graph from IEEE research, PathPilot ML recommendation system
- Found active community building n8n job automation workflows (51-node pipeline example on Reddit with CV-as-code approach)
- Created comprehensive FEATURE_LANDSCAPE.md mapping all features → tools → build/integrate decisions → phasing
- Cost model estimate: $15–35/mo (well under $50/mo budget)
- Drafted data model entity relationships spanning all features
- **Key finding:** The n8n + LangGraph combo is well-validated in the community for job automation. Multiple real users have built end-to-end pipelines.
- **Next:** Review landscape doc together, refine priorities, then start building Phase 1 module stubs

### 2026-03-17 — Scope Gap Analysis & Crawlee Discovery (Session 3)

- Created comprehensive OPEN_QUESTIONS.md with 16 tracked items (OQ-1 through OQ-16)
- Identified 5 BLOCKING gaps: user profile model, data model/schema, master resume strategy, integration architecture, ethical/legal boundaries
- Identified 3 HIGH gaps: deployment topology, multi-role pipeline, handoff UX
- Identified 4 MEDIUM gaps: feedback loop, inbound comms tracking, cover letters, OpenClaw reuse
- Identified 4 LOW gaps: salary intelligence, interview prep, rate limiting strategy, GDPR
- **Key discovery: Crawlee for Python (Apify, Apache-2, 20k+ stars)**
  - Crawlee provides request queue, auto-scaling, proxy rotation, session management, dataset storage, fingerprint generation, error handling, and official Camoufox integration
  - Eliminates need to build custom `browser_hand.py`, request queue, proxy rotation, session manager, and data export pipeline
  - Estimated scope reduction: ~500-800 lines of custom plumbing reduced to ~100-200 lines of extraction logic
  - Updated FEATURE_LANDSCAPE.md §9 with Crawlee architecture, comparison tables, and revised build-vs-integrate decisions
  - Crawlee can run standalone (our MVP plan) or deploy to Apify cloud later without code changes
- Updated OPEN_QUESTIONS.md OQ-4 to reflect Crawlee's impact on integration architecture
- **Key insight:** Crawlee + Camoufox plugin is the exact combination shown in the Apify template — this is a well-trodden path, not experimental
- **Next:** Resolve blocking OQs (user profile, data model, master resume) before building
