# Feature Landscape — Job Agent

> **Purpose:** Map every planned feature to available open-source tools, APIs, and solution patterns so we can make informed build-vs-integrate decisions.
> **Created:** 2026-03-17
> **Complements:** PROJECT_NOTES.md (scoping), OPTIMIZATION_NOTES.md (token/cost)

---

## How to Read This Document

Each feature section follows the same structure:

1. **What it does** — the capability from the user's perspective
2. **Tool landscape** — open-source tools, APIs, and libraries available today
3. **Recommended approach** — our proposed solution given the constraints (OSS-first, ~$50/mo, flexible orchestration, Ollama-local)
4. **Build vs. integrate** — what we write ourselves vs. what we adopt
5. **Phase** — when this lands (Phase 1 MVP, Phase 2, Phase 3)

---

## Feature 1: Job Discovery & Matching

### What It Does
Automatically discover job postings across multiple boards, deduplicate, score relevance against the user's profile, and surface the best matches.

### Tool Landscape

| Tool | Type | What It Offers | License / Cost | Stars | Notes |
|------|------|----------------|---------------|-------|-------|
| **JobSpy** (`python-jobspy`) | Python library | Scrapes LinkedIn, Indeed, Glassdoor, Google Jobs, ZipRecruiter. Returns structured data (title, company, location, salary, description, URL). Proxy/pagination support. | MIT | 2.4k+ | Most mature OSS job aggregator. Active community. FastAPI wrapper also available (`benpmeredith/jobspy`). |
| **Apify Job Board Aggregator** | SaaS API | Managed scraping with anti-bot handling. REST API. | Freemium (~$5/mo for light use) | N/A | Fallback if self-hosted scraping gets blocked. |
| **Greenhouse API** | Public API | JSON endpoints for company job boards (no auth needed). | Free | N/A | Good for targeted company-level scraping. Many companies use Greenhouse. |
| **Bright Data Job APIs** | SaaS API | Structured job data from all major boards. Handles anti-bot. | Paid (~$10/mo minimum) | N/A | Enterprise option if we need scale later. |
| **RSS Feeds** | Standard | Many company career pages and niche boards offer RSS. | Free | N/A | Lightweight, no scraping needed. Good for long-tail sources. |

### Recommended Approach

**Primary:** JobSpy as the core scraper. It's MIT-licensed, Python-native (fits our stack), and covers the 5 biggest job boards. We wrap it with our own matching/scoring layer.

**Scoring engine:** Custom Python module using Ollama for semantic similarity between user profile and JD. Simpler keyword/TF-IDF scoring as a fast first pass, LLM-based deep matching for top candidates.

**Deduplication:** Fuzzy matching on (title + company + location) to catch cross-board duplicates. Store canonical job ID in SQLite.

**Fallback:** Greenhouse public API for company-specific deep dives. RSS for niche boards.

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Job fetching | **Integrate** — JobSpy library |
| Deduplication | **Build** — custom fuzzy matching |
| Profile matching / scoring | **Build** — custom (TF-IDF + Ollama) |
| Job data storage | **Build** — SQLite schema |
| Rate limiting / retry | **Build** — backoff decorator |

### Phase: 1 (MVP)

---

## Feature 2: Resume Tailoring & ATS Optimization

### What It Does
Given a master resume (Markdown) and a job description, generate a tailored version that highlights relevant skills/experience, uses JD keywords, and passes ATS parsers. Render to PDF.

### Tool Landscape

| Tool | Type | What It Offers | License / Cost | Stars | Notes |
|------|------|----------------|---------------|-------|-------|
| **OpenResume** | Web app | Open-source resume builder with real-time ATS compatibility preview. React-based. | MIT | Popular | Good for understanding ATS rules. Parser we can study/extract. |
| **ATS-Scorer** (`Saanvi26/ATS-Scorer`) | Web app | Scores a resume against a JD for ATS compatibility (keyword match %, formatting). React + Vite. | Open source | Growing | Could extract scoring logic or use as validation step. |
| **pyresume** (`wespiper/pyresume`) | Python library | Simple, accurate resume parser — extracts structured fields from resumes. | MIT | Early | Useful for parsing existing resumes into structured data. |
| **markdown-resume-generator** | CLI tool | Markdown → styled PDF resume rendering. Multiple themes. | MIT | Niche | Direct fit for our MD→PDF pipeline. |
| **MarkdownResume.app** | Web app | Open-source Markdown-to-resume tool with live preview. | MIT | Growing | Design reference; could borrow CSS/templates. |
| **Pandoc + WeasyPrint** | CLI tools | Markdown → HTML → PDF pipeline. Full control over styling. | GPL / BSD | Mature | Most flexible option for programmatic rendering. |
| **LaTeX + moderncv** | Templates | Professional resume templates with fine typographic control. | LaTeX (free) | Classic | Higher quality output but harder to automate. |

### Recommended Approach

**Resume format:** Markdown as the canonical source. It's version-controllable, easy to manipulate programmatically, and diffs cleanly.

**Tailoring engine:**
1. Parse master resume → structured JSON (sections, bullets, skills)
2. Parse JD → required skills, keywords, seniority level, must-haves
3. Ollama generates tailored bullets, reorders sections, injects keywords
4. Validate: no hallucinated experience, all claims traceable to master resume
5. ATS check: run through keyword-match scoring (adapted from ATS-Scorer logic)

**Rendering:** Pandoc + WeasyPrint for MD → HTML → PDF. Custom CSS for professional styling. Multiple templates (dev, audit, freelance).

**Validation:** LLM-as-judge to score tailored resume against JD (relevance, accuracy, no hallucination). ATS-Scorer style keyword analysis as secondary check.

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Resume parser (MD → structured) | **Build** — custom Markdown parser |
| JD parser (extract requirements) | **Build** — Ollama-powered extraction |
| Tailoring logic | **Build** — Ollama prompts + template system |
| ATS scoring | **Integrate + adapt** — extract logic from ATS-Scorer |
| PDF rendering | **Integrate** — Pandoc + WeasyPrint |
| Resume templates | **Build** — custom CSS, borrow design ideas from OpenResume |

### Phase: 1 (MVP)

---

## Feature 3: OSINT for Career Networking & Relationship Mapping

### What It Does
Use open-source intelligence tools to discover who works at target companies, map relationship networks, find mutual connections, identify warm introduction paths, and recommend outreach opportunities.

### Tool Landscape

| Tool | Type | What It Offers | License / Cost | Stars | Notes |
|------|------|----------------|---------------|-------|-------|
| **SpiderFoot** | OSINT platform | 200+ modules for people, company, domain, email, social profile enumeration. Web UI + CLI + API. | MIT | 12k+ | Best general-purpose OSINT tool. Python. Self-hostable. |
| **CrossLinked** (`m8sec/CrossLinked`) | CLI tool | LinkedIn employee enumeration via search engine scraping (Google/Bing dorking). Outputs employee names + titles. | GPL-3 | 1.4k+ | Focused on the exact use case we need. No LinkedIn auth required. |
| **theHarvester** | CLI tool | Email, subdomain, and name enumeration for target companies. | GPL | 12k+ | Quick company recon. Good complement to CrossLinked. |
| **Gephi** | Desktop app | Network visualization, community detection, centrality analysis. | GPL | 5k+ | User already knows this from OpenClaw project. |
| **Kuzu** | Embedded graph DB | Lightweight graph database, Python bindings, Cypher-compatible. | MIT | 1.5k+ | Already explored with CocoIndex in OpenClaw. Could store relationship graphs. |
| **Cytoscape** | Desktop/web | Complex network analysis and visualization. | LGPL | Mature | Alternative to Gephi for network viz. Web version (Cytoscape.js) for dashboards. |
| **Recon-ng** | Framework | Modular web recon framework with marketplace of modules. | GPL | 3k+ | More hands-on but very flexible for custom pipelines. |
| **OSINTBuddy** | Web platform | Open-source Maltego alternative with node graphs. | Open source | Newer | Promising but less mature. |

### Recommended Approach

**Phase 1 (MVP) — Basic people lookup:**
1. CrossLinked for employee enumeration at target companies (lightweight, fast, no auth)
2. theHarvester for email/domain recon
3. Store results in SQLite (people table with company, title, source)
4. Simple "who works here" report per target company

**Phase 2 — Relationship mapping:**
1. SpiderFoot for deeper OSINT (social profiles, mutual connections, shared history)
2. Kuzu graph DB for relationship storage (person→company, person→person, person→event)
3. Cytoscape.js embedded in dashboard for interactive network visualization
4. "Warm path" algorithm: shortest path from user's network to target person/company

**Privacy controls:** All OSINT data is local-only. No data leaves the user's machine unless explicitly shared. Clear logging of what data was collected and from where.

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Employee enumeration | **Integrate** — CrossLinked |
| Domain/email recon | **Integrate** — theHarvester |
| Deep OSINT scanning | **Integrate** — SpiderFoot (Phase 2) |
| Relationship graph storage | **Integrate** — Kuzu (reuse OpenClaw pattern) |
| Network visualization | **Integrate** — Cytoscape.js (web) or Gephi (export) |
| "Warm path" analysis | **Build** — custom graph traversal on Kuzu |
| Data normalization / dedup | **Build** — custom entity resolution pipeline |

### Phase: 1 (basic), 2 (relationship mapping + graph viz)

---

## Feature 4: Dashboard & Pipeline Tracking

### What It Does
Visual dashboard showing the full application pipeline: discovered jobs, applied, interviewing, offers, rejected. Task management, deadline tracking, analytics on application performance.

### Tool Landscape

| Tool | Type | What It Offers | License / Cost | Stars | Notes |
|------|------|----------------|---------------|-------|-------|
| **JobTracker** (`kaitranntt/jobhunt`) | Web app | Glass-morphism UI, Kanban board, application tracking. | Open source | Small | Good design reference. |
| **JobTracker** (`letanure/JobTracker`) | Web app | Local-first, privacy-focused. Runs entirely in browser. No backend. | Open source | Small | Interesting local-first approach. |
| **ApplyTrak** | Web app | Analytics, goals, smart organization for job search. | Open source | Growing | Feature reference for analytics. |
| **Plane** | Project mgmt | Modern Kanban/list/calendar views, real-time collab, GitHub sync, self-hosted (Docker). | AGPL-3 | 25k+ | Overkill for us but excellent design patterns to study. |
| **n8n UI** | Workflow UI | Built-in execution viewer, but not a custom dashboard. | Fair code | 50k+ | Our orchestration layer, not the dashboard itself. |
| **Next.js** | Framework | User knows Next.js well. Full SSR/SSG/API routes. | MIT | 130k+ | Natural choice given user's skills. |

### Recommended Approach

**Custom Next.js dashboard** — the user knows Next.js well, and no existing job tracker combines all our features (OSINT data, LLM-tailored resumes, pipeline management). Better to build exactly what we need.

**Key views:**
- **Kanban pipeline:** Discovered → Applied → Phone Screen → Interview → Offer → Accepted/Rejected
- **Job detail:** JD, company OSINT intel, tailored resume preview, match score, notes
- **Analytics:** Application velocity, response rate, time-in-stage, skill match trends
- **Task/deadline list:** Follow-ups due, interview prep needed, application deadlines
- **OSINT panel:** People at company, warm paths, recent company news

**Data layer:** SQLite via Prisma or Drizzle ORM. API routes in Next.js.

**State transitions:** Enforce valid pipeline transitions. Log every state change with timestamp for analytics.

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Frontend dashboard | **Build** — Next.js + Tailwind |
| Kanban board | **Build** — use `@dnd-kit` or similar drag-and-drop library |
| Pipeline state machine | **Build** — custom state transitions |
| Analytics / charts | **Integrate** — Recharts or Chart.js |
| Data layer / ORM | **Integrate** — Prisma or Drizzle with SQLite |
| Notifications | **Build** — simple email or webhook alerts |

### Phase: 1 (MVP — basic pipeline view + job detail), 2 (analytics, OSINT panel, rich interactions)

---

## Feature 5: Communication Management & Outreach

### What It Does
Draft, send, and track communications with recruiters and hiring managers. Manage follow-ups, templates, and response tracking.

### Tool Landscape

| Tool | Type | What It Offers | License / Cost | Stars | Notes |
|------|------|----------------|---------------|-------|-------|
| **Email-automation** (`PaulleDemon/Email-automation`) | Python tool | Open-source cold outreach tool. Schedule, personalize, and send emails to multiple recipients. | Open source | Small | Good reference for email template + scheduling pattern. |
| **Mautic** | Marketing automation | Full email automation platform. Sequences, templates, tracking. Self-hosted. | GPL-3 | 7k+ | Very powerful but complex setup. Overkill for personal use. |
| **n8n email workflows** | Workflow | Gmail/SMTP integration, scheduling, conditional follow-ups. | Fair code | N/A | Natural fit since we already use n8n. Pre-built templates exist for job application pipelines. |
| **Reply.io** | SaaS | Multi-channel sequences (email, LinkedIn, SMS). A/B testing, analytics. | Paid | N/A | Commercial reference for feature ideas. |
| **Lemlist** | SaaS | Visual personalization, email warm-up, delivery optimization. | Paid | N/A | Commercial reference. |

### Recommended Approach

**Phase 1 (MVP):** No automated sending. System generates draft emails/messages that the user reviews and sends manually. Templates stored in Markdown.

**Phase 2:**
1. n8n workflows for email automation (Gmail integration, scheduled sends, follow-up reminders)
2. Ollama generates personalized outreach drafts based on OSINT data (company info, person's background, mutual connections)
3. Response tracking: monitor inbox for replies, link to pipeline entry
4. Follow-up cadence: configurable reminders (3 days, 7 days, 14 days)

**Key principle:** Human-in-the-loop for all external communication. The system drafts, the user approves and sends.

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Email templates | **Build** — Markdown templates with variable injection |
| Draft generation | **Build** — Ollama prompts using OSINT context |
| Email sending | **Integrate** — n8n Gmail node (Phase 2) |
| Follow-up scheduling | **Integrate** — n8n cron triggers (Phase 2) |
| Response tracking | **Build** — inbox monitor script (Phase 2) |
| Communication log | **Build** — SQLite table linked to pipeline entries |

### Phase: 1 (draft templates only), 2 (automated sending + tracking)

---

## Feature 6: Skill Gap Analysis & Learning Recommendations

### What It Does
Compare the user's skills against target job requirements. Identify gaps. Recommend specific courses, certifications, projects, or learning paths to close those gaps.

### Tool Landscape

| Tool / Concept | Type | What It Offers | License / Cost | Notes |
|----------------|------|----------------|---------------|-------|
| **O*NET OnLine** | Public data | Standardized occupational skills taxonomy. 1,000+ occupations with detailed skill requirements. | Free (US DOL) | Gold standard for skill ontologies. API available. |
| **Skills ontology approach** (AIHR) | Framework | Structured skill maps with proficiency levels, relationships, and prerequisites. | Concept | Best practice for building skill gap analysis. Proficiency scale 1-5. |
| **PathPilot** (`sinsniwal/PathPilot-recommendation-system`) | Research project | Learning path recommendation using ML (scikit-learn, TensorFlow). Django + SQLite backend. | MIT | Academic reference. Interesting ML approach but likely overkill for MVP. |
| **Unified Candidate Skill Graph** (IEEE paper) | Research | Skill ontology from O*NET + course catalogs. Graph-based career path recommendations. | Academic | Great architecture reference. Uses prerequisite graphs between skills. |
| **beam.ai Skill Gap Analysis** | SaaS | Automated profile vs. JD comparison with training recommendations. | Paid | Commercial reference for feature design. |
| **LinkedIn Learning** | SaaS | 16,000+ courses. API for content recommendations. | Paid subscription | Potential learning resource to recommend (not integrate). |
| **Coursera / edX / Udemy APIs** | APIs | Course catalog search. Some have free public APIs. | Free APIs | Good for recommending specific courses. |

### Recommended Approach

**Skill extraction:**
1. Parse user's master resume → skill list with estimated proficiency (based on years, context)
2. Parse target JDs → required skills with importance weighting
3. Use O*NET taxonomy as the normalization layer (map "React" → "Front-End Development", etc.)

**Gap analysis:**
1. For each required skill: compare required proficiency vs. user's proficiency
2. Weight by importance to the role
3. Produce ranked list of gaps: "You need X at level Y, you're at level Z"

**Learning recommendations:**
1. Maintain a curated mapping of skills → learning resources (courses, certs, projects)
2. Start with manual curation, later enrich with course API searches (Coursera, Udemy)
3. Ollama generates personalized learning plans: "Given your background in X, to learn Y you should..."
4. Track progress: user marks courses complete → skill proficiency updates

**Skill ontology:** Start simple — a YAML/JSON file mapping skills to categories, levels, and relationships. Evolve toward O*NET integration in Phase 2.

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Skill extraction from resume | **Build** — Ollama-powered extraction |
| Skill extraction from JD | **Build** — Ollama-powered extraction |
| Skill taxonomy | **Build** — start with curated YAML, later **Integrate** O*NET API |
| Gap calculation | **Build** — custom scoring logic |
| Learning resource database | **Build** — curated YAML + Ollama for personalized plans |
| Course search | **Integrate** — Coursera/Udemy public APIs (Phase 2) |
| Progress tracking | **Build** — SQLite table |

### Phase: 1 (basic gap analysis — resume vs. JD comparison), 2 (skill ontology, learning paths, course API integration)

---

## Feature 7: Portfolio Project Generation

### What It Does
Recommend and help scaffold portfolio projects that demonstrate skills relevant to target roles. Generate README templates, project structures, and even starter code.

### Tool Landscape

| Tool | Type | What It Offers | License / Cost | Notes |
|------|------|----------------|---------------|-------|
| **GitHub Pages** | Hosting | Free static site hosting. Automatic deployment from repos. | Free | Natural home for portfolio projects. |
| **Portfolio generators** (various) | CLI/Web | Generate portfolio sites from YAML/JSON config. Next.js, Astro, Hugo options. | MIT | Many options. User knows Next.js so can build custom. |
| **Astro** | SSG | Content-focused static site generator. Fast, modern, component islands. | MIT | Strong option for portfolio site. |
| **isBio** | Web engine | Open-source personal website engine with portfolio, resume, and blog. | MIT | All-in-one portfolio solution. |
| **Cookiecutter** / **Copier** | CLI | Project scaffolding from templates. Can generate entire project structures. | MIT | Good for generating starter projects programmatically. |

### Recommended Approach

**Project recommendation:**
1. Analyze skill gaps from Feature 6
2. Ollama suggests project ideas that demonstrate the missing skills
3. Projects are tagged by: skill demonstrated, difficulty, estimated time, relevance to target roles

**Project scaffolding:**
1. Maintain a library of project templates (Cookiecutter or custom)
2. Generate README with problem statement, learning objectives, and suggested approach
3. Create GitHub repo with starter structure
4. Bonus: Ollama generates code scaffolding for each project

**Portfolio site:**
1. Generate from project metadata (GitHub repos, descriptions, skills)
2. Deploy to GitHub Pages
3. Auto-update when new projects are added

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Project recommendation engine | **Build** — Ollama + skill gap data |
| Project templates | **Build** — Cookiecutter templates |
| Repo scaffolding | **Integrate** — GitHub API for repo creation |
| Portfolio site generation | **Build** — Next.js or Astro static site |
| Portfolio hosting | **Integrate** — GitHub Pages |

### Phase: 3

---

## Feature 8: Freelance & Contract Management

### What It Does
Track freelance gigs, manage contracts, generate invoices, log time, and manage payments.

### Tool Landscape

| Tool | Type | What It Offers | License / Cost | Stars | Notes |
|------|------|----------------|---------------|-------|-------|
| **Invoice Ninja** | Full platform | Invoicing, quotes, expenses, projects, tasks, time tracking, client portal, recurring invoices. Self-hosted Docker. | AAL / Free OSS | 8k+ | Most feature-complete OSS invoicing tool. Handles everything. |
| **Invoicerr** | Web app | Lightweight invoicing for freelancers. EU-compliant. Docker Compose deployment. Clean UI. | Open source | New | Simpler alternative to Invoice Ninja. |
| **Plane** | Project mgmt | Issue tracking, Kanban, timeline. Could track freelance projects. | AGPL-3 | 25k+ | Overkill for freelance tracking alone but good if we need project management. |
| **TimeTracker** | Web app | Time tracking + basic invoicing. Self-hosted. | Open source | Niche | Lightweight option for time + invoice. |

### Recommended Approach

**Integrate Invoice Ninja** rather than building invoicing from scratch. It's a solved problem with Invoice Ninja — they handle invoicing, time tracking, expenses, client management, and have a full API.

**Our integration layer:**
1. Auto-create Invoice Ninja clients from pipeline entries that convert to freelance gigs
2. Link freelance projects to the dashboard pipeline
3. Time tracking synced between our dashboard and Invoice Ninja
4. Basic contract template storage (Markdown → PDF via Pandoc)

### Build vs. Integrate

| Component | Approach |
|-----------|----------|
| Invoicing | **Integrate** — Invoice Ninja (self-hosted) |
| Time tracking | **Integrate** — Invoice Ninja |
| Contract templates | **Build** — Markdown templates + Pandoc rendering |
| Gig pipeline tracking | **Build** — extend dashboard with freelance states |
| Payment tracking | **Integrate** — Invoice Ninja |

### Phase: 3

---

## Orchestration Strategy

Our system intentionally avoids single-orchestrator lock-in. Here's how each tool fits:

| Orchestration Tool | Best Used For | In Our System |
|--------------------|---------------|---------------|
| **n8n** (self-hosted) | Visual workflows, integrations with external services (Gmail, Sheets, webhooks), scheduled tasks, non-technical users | Email workflows, scheduled job scraping, notification pipelines, external service integrations |
| **LangGraph** | Multi-step AI agent workflows with state management, conditional branching, tool use | Resume tailoring pipeline, skill gap analysis, OSINT analysis chains |
| **Ollama** (local) | Direct LLM inference with minimal latency and zero API cost | All LLM tasks: tailoring, drafting, scoring, extraction. Managed through our token_tracker.py |
| **Custom Python** | Simple scripts where a framework is overhead | Data transforms, scrapers, CLI tools, one-off utilities |
| **n8n + LangGraph** combined | Complex workflows that need both external integrations AND AI reasoning | End-to-end pipeline: n8n triggers job scan → LangGraph agent scores + tailors → n8n sends notification |

### Existing Infrastructure

We already have in the repo:
- `src/utils/token_tracker.py` — Ollama wrapper with automatic token/latency/cost tracking to SQLite
- `tests/token_benchmark/test_token_baseline.py` — V1 vs. V2 prompt benchmarks (9/9 pass, 60.4% avg input savings)
- `scripts/run_benchmark.py` — CLI for benchmark reports, comparisons, and CSV export

---

## Cost Model (Monthly Estimate)

| Component | Cost | Notes |
|-----------|------|-------|
| VPS (n8n + services) | $10–20/mo | DigitalOcean or Hetzner 2-4GB |
| Ollama (local) | $0 | Runs on user's machine |
| JobSpy scraping | $0 | Self-hosted, respects rate limits |
| OSINT tools | $0 | All MIT/GPL self-hosted |
| OpenRouter API (fallback) | $5–15/mo | Only for tasks Ollama can't handle |
| GitHub | $0 | Free for public repos |
| SQLite | $0 | Embedded |
| **Total** | **$15–35/mo** | Well under $50/mo budget |

---

## Data Model Overview (Preview)

These are the core entities that span all features:

```
┌──────────┐     ┌───────────┐     ┌──────────┐
│   Job    │────▶│Application│────▶│  Resume   │
│          │     │           │     │ (tailored)│
│ title    │     │ status    │     │ version   │
│ company  │     │ applied_at│     │ match_%   │
│ jd_text  │     │ notes     │     │ pdf_path  │
│ source   │     │ stage     │     │           │
│ score    │     │           │     │           │
└────┬─────┘     └─────┬─────┘     └──────────┘
     │                 │
     │                 ▼
     │           ┌───────────┐     ┌──────────┐
     │           │   Comms   │     │  Skill   │
     │           │           │     │          │
     │           │ type      │     │ name     │
     │           │ direction │     │ category │
     │           │ content   │     │ level    │
     │           │ sent_at   │     │ source   │
     │           └───────────┘     └────┬─────┘
     │                                  │
     ▼                                  ▼
┌──────────┐     ┌───────────┐     ┌──────────┐
│ Company  │────▶│  Person   │     │ SkillGap │
│          │     │           │     │          │
│ name     │     │ name      │     │ required │
│ domain   │     │ title     │     │ current  │
│ industry │     │ email     │     │ gap      │
│ osint_   │     │ linkedin  │     │ priority │
│ data     │     │ company_id│     │ resource │
└──────────┘     └───────────┘     └──────────┘
```

---

## Summary: Build Priority Matrix

| Feature | Phase | Effort | Impact | Key Tool(s) |
|---------|-------|--------|--------|-------------|
| Resume Tailoring | 1 (MVP) | Medium | High | Ollama, Pandoc, WeasyPrint |
| Job Discovery & Matching | 1 (MVP) | Medium | High | JobSpy, Ollama |
| OSINT People Lookup (basic) | 1 (MVP) | Low | Medium | CrossLinked, theHarvester |
| Dashboard (basic pipeline) | 1 (MVP) | Medium | High | Next.js, SQLite |
| Skill Gap Analysis (basic) | 1 (MVP) | Low | Medium | Ollama, custom scoring |
| Communication Drafts | 1 (MVP) | Low | Medium | Ollama, Markdown templates |
| Automated Email Outreach | 2 | Medium | Medium | n8n, Gmail integration |
| Relationship Mapping | 2 | High | High | SpiderFoot, Kuzu, Cytoscape.js |
| Learning Path Recommendations | 2 | Medium | Medium | O*NET API, Coursera/Udemy APIs |
| Dashboard Analytics | 2 | Medium | Medium | Next.js, Recharts |
| Portfolio Generation | 3 | Medium | Low | Cookiecutter, GitHub API, Astro |
| Freelance Management | 3 | Low | Low | Invoice Ninja |
| Full Autonomous Pipeline | 3 | High | High | n8n + LangGraph + browser automation |

---

## Next Steps

1. Review this document together — refine feature scope, adjust priorities
2. Define SQLite data models for Phase 1 entities (Job, Application, Resume, Company, Person, Skill)
3. Create module stubs for Phase 1 features
4. Build resume tailoring engine first (highest standalone value)
5. Wire up JobSpy integration for job discovery
6. Basic CLI before dashboard (validate logic before building UI)

---

## References

- [JobSpy on GitHub](https://github.com/speedyapply/JobSpy)
- [CrossLinked on GitHub](https://github.com/m8sec/CrossLinked)
- [SpiderFoot on GitHub](https://github.com/smicallef/spiderfoot)
- [OpenResume](https://www.open-resume.com)
- [ATS-Scorer on GitHub](https://github.com/Saanvi26/ATS-Scorer)
- [Invoice Ninja on GitHub](https://github.com/invoiceninja/invoiceninja)
- [Plane on GitHub](https://github.com/makeplane/plane)
- [LangGraph Docs](https://docs.langchain.com/oss/python/langgraph/workflows-agents)
- [n8n Job Application Workflow](https://n8n.io/workflows/5906-automated-job-applications-and-status-tracking-with-linkedin-indeed-and-google-sheets/)
- [O*NET OnLine](https://www.onetonline.org/)
- [AIHR Skills Ontology Guide](https://www.aihr.com/blog/skills-ontology/)
- [Kuzu Graph DB](https://kuzudb.com/)
- [n8n Automated Job Pipeline (Reddit)](https://www.reddit.com/r/n8n/comments/1r95t1k/i_built_a_fully_automated_job_application/)
