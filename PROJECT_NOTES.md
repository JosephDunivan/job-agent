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

## 6. Next Steps

- [ ] Finalize Phase 1 scope (answer the open questions in §2.3)
- [ ] Choose orchestration layer (n8n vs LangGraph vs custom)
- [ ] Set up the GitHub repo with this document
- [ ] Create initial project structure (even if mostly empty)
- [ ] Start with the simplest useful feature (likely: resume tailoring + job matching)

---

## 7. Session Log

### 2026-03-17 — Initial Scoping Session

- Captured full vision from user prompt
- Researched existing open-source job agents: AIHawk, ApplyPilot, job-app, ai-job-apply-agent
- Researched OSINT tools: SpiderFoot, Maltego, Gephi, theHarvester, OSINTBuddy, Recon-ng
- Researched orchestration: n8n (self-hosted), LangGraph, Temporal
- Identified key differentiator: OSINT + networking intelligence combined with job automation (no existing project does this)
- Proposed 3-phase approach: MVP → automation → full autonomous pipeline
- Created this PROJECT_NOTES.md as living document
- **Open:** Need to answer scoping questions before architecture decisions
