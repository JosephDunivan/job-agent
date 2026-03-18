# LinkedIn Profile Optimization Guide

> **Purpose:** Prepare Joseph's LinkedIn presence for an active job search across three
> target lanes: full-stack engineering, AI/LLM tooling, and front-end design / unique
> product experiences. This document is also a seed artifact for the job-agent system —
> the profile fields, tone notes, and keyword lists here feed directly into the resume
> tailoring and job-matching modules.
>
> **Philosophy:** Same as the project's — no hype, no buzzword stacking, everything earns
> its place. Position with specificity. Generic profiles get filtered out; precise ones
> get read.

---

## 1. Profile Positioning Strategy

There are three distinct lanes to target. The LinkedIn profile should be set up for
**flexible positioning** — a headline and About section that signal all three without
feeling scattered. The key is leading with the engineering identity and letting the
specializations emerge as natural extensions of it.

### Target Lanes

| Lane | What Recruiters Are Looking For | Your Differentiators |
|------|---------------------------------|----------------------|
| **Full-stack engineering** | Python/JS depth, product delivery, system design | End-to-end ownership; comfort from DB schema to UI; self-hosted systems at real scale |
| **AI / LLM tooling** | Prompt engineering, agent frameworks, LLM integration, evaluation | LangGraph, Ollama, LLM-as-judge eval harnesses, agent orchestration pipelines |
| **Front-end / unique product experiences** | UI craft, interaction design, creative problem-solving | Next.js depth, graph visualization (Gephi/network maps), building interfaces that go beyond generic dashboards |

### Recommended Primary Positioning

> **Senior Full-Stack Engineer — AI Integration, Automation & Intelligent Systems**

This framing:
- Opens doors in all three lanes
- Doesn't pigeonhole as "just backend" or "just AI"
- Signals seniority without requiring a traditional title
- Is accurate to what the work actually is

### When Applying for Specific Roles

For **AI/LLM-heavy roles**: Lead with agent frameworks, eval methodology, Ollama/LangGraph
pipeline work, and the job-agent project as a live example of autonomous system design.

For **front-end / design-forward roles**: Lead with Next.js, UI craft, graph visualization
work (Gephi, network mapping dashboards), and the unique-experience angle — you don't
just build forms, you build systems people actually want to interact with.

For **full-stack generalist roles**: Lead with delivery — end-to-end systems, self-hosted
infrastructure, clean architecture decisions, and the ability to own a product from DB
schema to deployed UI.

---

## 2. Headline Variants

LinkedIn headline = 220 characters max. Recruiters see it in search results before they
click your profile. It needs to communicate lane + differentiator in one line.

### Option A — Full-time engineering role (recommended default)
```
Full-Stack Engineer | AI Agents · Workflow Automation · Next.js | Building systems that think, not just execute
```

### Option B — Freelance / contract emphasis
```
Independent Software Engineer | Python · Next.js · LLM Integration | Open to contract & full-time
```

### Option C — Broad / all three lanes
```
Full-Stack Engineer | AI/LLM Tooling · Front-End Craft · Automation Systems | Python · Next.js · OSINT
```

**Recommendation:** Start with **Option A**. It's the strongest signal for inbound
recruiter search (Python, Next.js, AI are high-volume terms) while differentiating with
"systems that think, not just execute." Switch to Option B if you shift toward contract
mode. Option C works if you're sending it directly in applications.

**What to avoid:**
- "Passionate developer looking for opportunities" — says nothing
- Listing 10 technologies with no connective tissue — keyword spam, no story
- Vague terms like "innovative" or "results-driven" — every profile says this

---

## 3. About / Summary Section

### Tone Notes (Derived from Project Voice)

The project docs are written in a specific voice: direct, analytical, claim-then-prove,
no hype. The About section should match:

- **Lead with what you build**, not how you feel about building it
- **Name specific tools and outcomes**, not generic "I work with modern technologies"
- **Acknowledge complexity honestly** — the job-agent README says "most job automation
  tools are apply bots that spam applications" — that's the kind of specificity that
  reads as expertise
- **First person, active voice**: "I built", "I architected", not "responsible for"

### Draft (~2,100 characters — fits within LinkedIn's 2,600 char limit)

---

I build full-stack systems that go beyond the obvious solution. My work sits at the
intersection of software engineering, AI integration, and workflow automation — the kind
of problems where the interesting challenge isn't just writing code, but deciding what
the system should actually do.

Recent focus areas:

**AI & LLM Integration** — I design and build agent pipelines using LangGraph, Ollama,
and custom orchestration layers. That includes not just hooking up an LLM, but building
evaluation harnesses (LLM-as-judge), prompt versioning systems, and fallback behavior
that actually degrades gracefully. If it touches an LLM in production, it needs to be
testable and auditable.

**Full-Stack Development** — Python on the backend, Next.js on the front. I'm comfortable
owning a feature from data model through deployed UI. I've worked with SQLite, PostgreSQL,
and graph databases (Kuzu, Neo4j) depending on what the problem actually calls for.

**Workflow Automation & Orchestration** — Self-hosted n8n, LangGraph pipelines, and
custom Python. I prefer the tool that fits the job over the tool that's most familiar.

**Front-End Craft** — I care about how interfaces feel, not just whether they function.
I've built graph visualization systems, network mapping dashboards, and custom UX for
complex data — Next.js is my primary environment.

I lean toward open-source, self-hosted solutions. Privacy-aware architecture is a design
constraint, not an afterthought.

Currently building a career intelligence system (job-agent) that combines OSINT-powered
networking with AI resume tailoring — an autonomous agent that treats job search as an
intelligence problem, not a volume problem.

Open to full-time engineering roles and contract engagements.

---

**Editing notes:**
- Swap in a real project name/outcome once Phase 1 ships (e.g., "reduced time-to-tailored-resume from 2 hours to 4 minutes")
- Add a link to the job-agent GitHub repo once it's public
- If applying to security/OSINT-adjacent roles, add a sentence on SpiderFoot and network analysis

---

## 4. Skills Section

LinkedIn allows pinning 5 "top skills" that appear prominently. Choose these based on
what recruiters in your target lanes are actually searching for.

### Top 5 (Pin These)

1. **Python** — highest search volume for backend/automation/AI roles
2. **JavaScript / TypeScript** — front-end + full-stack signal
3. **Next.js** — specific enough to differentiate, common enough to surface in searches
4. **Large Language Models (LLM)** — LinkedIn's canonical term for this skill cluster
5. **Workflow Automation** — covers n8n, LangGraph, orchestration pipelines

### Secondary Skills (Add, Don't Pin)

- React
- Node.js
- PostgreSQL / SQLite
- Graph Databases
- OSINT (Open Source Intelligence)
- SpiderFoot
- LangGraph
- Prompt Engineering
- Docker / Self-Hosted Infrastructure
- REST APIs
- AI Agents
- Software Testing / QA
- SOX Compliance (if targeting fintech/audit-adjacent roles)
- Gephi / Network Analysis

### Skills to Avoid Adding

Don't pad with: "Communication", "Teamwork", "Problem Solving", "Agile". Every profile
has these. They add no signal and crowd out space for real skills.

---

## 5. Experience Framing Guidelines

### The Formula

Replace: *"Responsible for X"*
With: *"[Action verb] [what you built] that [outcome/impact]"*

### Verb Selection by Role Type

| For engineering/build work | For automation/AI work | For analysis/architecture work |
|---------------------------|------------------------|-------------------------------|
| Architected | Automated | Designed |
| Built | Orchestrated | Evaluated |
| Shipped | Integrated | Audited |
| Refactored | Reduced | Mapped |
| Deployed | Eliminated | Identified |

### Seniority Signals

Junior engineers describe what they did. Senior engineers describe **why** and **what
changed because of it**. To signal seniority:

- Include the decision, not just the outcome: *"Chose Kuzu over Neo4j Community for
  embedded graph storage — avoided external service dependency and reduced operational
  complexity"*
- Reference trade-off analysis: *"Evaluated n8n, LangGraph, and custom Python
  orchestration; chose flexible multi-tool approach to avoid vendor lock-in"*
- Mention quality gates: *"Built LLM-as-judge evaluation harness; zero hallucinated
  credentials in tailored resumes across 500 test runs"*

### The Job-Agent Project as Portfolio Evidence

Even in early phase, the project is citable. Frame it as:

> **Job Agent** *(Open Source, 2026 — present)*
> Designing and building an autonomous career intelligence system that combines
> OSINT-powered networking, AI resume tailoring, and pipeline management. Replacing
> the "apply bot" model with a system that maps relationship networks, identifies
> warm paths to target roles, and learns which strategies convert.
>
> **Stack:** Python, Next.js, LangGraph, Ollama, n8n (self-hosted), SpiderFoot,
> Kuzu (graph DB), SQLite, Docker

Update this entry as modules ship with specific metrics (e.g., match score accuracy,
tailoring time reduction).

---

## 6. Featured Section Strategy

The Featured section sits prominently on your profile — above the experience section
for most visitors. Use it deliberately.

### What to Feature (Priority Order)

1. **Link to job-agent GitHub repo** — as soon as it's public with a clean README.
   A well-written README reads as thought leadership. The current README is already
   strong: "Most job automation tools are apply bots that spam applications" is a
   hook that stops scrolling.

2. **Any write-up or notes published externally** — if you post a technical article
   about the OSINT architecture, the LLM eval methodology, or the graph database
   decision rationale, feature it here. Even a LinkedIn post with 200+ impressions
   is worth featuring if it's substantive.

3. **A live demo or screenshot walkthrough** — once the dashboard ships, a short
   walkthrough (Loom or GIF) showing the pipeline in action is more memorable than
   any bullet point.

### What Not to Feature

- Generic certificates that don't signal expertise in your target lanes
- Projects that are significantly older than your current focus
- Links that require sign-in to view

---

## 7. LinkedIn Voice & Content Strategy

### Post Style

You don't need to post frequently. A few high-quality posts that demonstrate genuine
expertise outperform daily motivational content.

Patterns that work well for your positioning:

**The Decision Walkthrough** — *"I evaluated three orchestration options for job-agent.
Here's what I found and why I chose flexible/multi-tool over a single lock-in:"* +
actual comparison table. This mirrors exactly how your PROJECT_NOTES.md documents
decisions. Readers who find this valuable are exactly the people you want to talk to.

**The Contrarian Observation** — *"Most job automation tools are apply bots. Here's
what a career intelligence system looks like instead:"* — you've already written the
framing; it just needs to be published.

**The Specific Problem / Specific Solution** — *"LLM-as-judge for resume quality:
why 'does it sound good' isn't a pass criteria and what I use instead"*. Specific >
general, always.

### What to Avoid

- Motivational posts ("Excited to announce I'm starting a new chapter!")
- Vague technical claims without substance ("Working with cutting-edge AI every day")
- Excessive hashtags (2–3 per post maximum; more reads as spam)
- Engagement bait ("Comment YES if you agree")

### Engagement (Comments)

Substantive comments on other people's posts — adding a real data point, a counterpoint,
or a specific tool recommendation — build profile visibility faster than posting alone.
Target 3–5 substantive comments per week in the AI/LLM tooling and developer tooling
spaces.

---

## 8. Keyword Optimization for Search Discoverability

LinkedIn's search algorithm weights keywords in: (1) headline, (2) current job title,
(3) About section, (4) skills, (5) experience entries. Put high-priority terms in
multiple locations.

### High-Priority Search Terms (Place in Headline + About + Skills)

| Term | Target Lane | Notes |
|------|-------------|-------|
| Python | Full-stack, AI/ML | Highest volume for backend/automation |
| Next.js | Front-end, full-stack | Specific enough to filter well |
| LLM / Large Language Models | AI tooling | LinkedIn's canonical term |
| AI Agents | AI tooling | Fast-rising search term in 2026 |
| Workflow Automation | All lanes | Covers n8n, LangGraph, pipelines |
| Full-Stack Engineer | All lanes | Title-level search term |
| React | Front-end | Implied by Next.js but worth stating |

### Secondary Terms (Place in About + Skills + Experience)

| Term | Notes |
|------|-------|
| LangGraph | Specific enough to surface in niche AI agent searches |
| Prompt Engineering | High volume, relevant to AI tooling |
| Graph Database | Differentiator; low competition |
| OSINT | Niche but very specific signal for the right roles |
| Self-Hosted / Open Source | Values signal; attracts certain company cultures |
| Software Testing / QA | Signals rigor; valued at senior level |

### ATS-Aware Language

When applying directly via LinkedIn, the application goes through ATS before a human
reads it. Mirror exact phrasing from job descriptions:

- If JD says "TypeScript", use "TypeScript" not just "JavaScript"
- If JD says "LLM integration", use "LLM integration" not just "AI"
- If JD says "React", include React explicitly even if you primarily use Next.js

The job-agent resume tailoring module will automate this alignment — but until that's
built, do it manually for each application.

---

## 9. Job-Agent Integration Notes

This guide is designed to serve double duty: personal optimization resource *and*
structured seed data for the job-agent system.

### Fields to Extract for User Profile Schema

```json
{
  "name": "Joseph Dunivan",
  "email": "josephdunivanucf@gmail.com",
  "positioning": {
    "primary_title": "Full-Stack Engineer",
    "specializations": ["AI/LLM Integration", "Workflow Automation", "Front-End Design"],
    "target_lanes": ["full-stack-engineering", "ai-llm-tooling", "frontend-ux"]
  },
  "skills": {
    "primary": ["Python", "JavaScript", "TypeScript", "Next.js", "LLM Integration"],
    "secondary": ["LangGraph", "n8n", "Ollama", "React", "PostgreSQL", "SQLite",
                  "Kuzu", "Graph Databases", "SpiderFoot", "OSINT", "Docker",
                  "Pytest", "Software Testing"],
    "domain_specific": ["Workflow Automation", "AI Agents", "Prompt Engineering",
                        "SOX Compliance", "Network Analysis"]
  },
  "work_modes": ["full-time", "contract", "freelance"],
  "preferences": {
    "open_source_first": true,
    "self_hosted": true,
    "privacy_aware": true
  },
  "portfolio": [
    {
      "name": "job-agent",
      "description": "Autonomous career intelligence system combining OSINT networking with AI resume tailoring",
      "status": "early-phase",
      "url": null
    }
  ]
}
```

### Notes for Resume Tailoring Module

- **Headline variant selection:** Module should map job type → headline Option A/B/C
  based on role classification (full-time vs. contract, AI-heavy vs. front-end-heavy)
- **About section parameterization:** The OSINT paragraph should be injected/removed
  based on whether the target role is security/intelligence-adjacent
- **Skill ordering:** When generating resumes, order skills based on JD keyword
  frequency — most-mentioned skills from the JD should appear first

### Notes for OSINT / Relationship Intelligence Module

- This profile document defines the "who am I" side of relationship mapping
- Use specializations and target lanes to seed "warm path" scoring: a contact at a
  company building LLM tooling is a higher-priority warm path than a contact at a
  generic enterprise software firm
- The front-end/UX lane should be treated as a separate target cluster for event
  discovery (design conferences, React/Next.js meetups are relevant)

---

## 10. Immediate Action Checklist

Work through these in order — each one independently improves discoverability or
conversion before the next is done.

- [ ] **Update headline** to Option A (or chosen variant)
- [ ] **Replace About section** with the draft above (edit to personalize)
- [ ] **Pin top 5 skills** in the order listed in Section 4
- [ ] **Add secondary skills** from the list in Section 4
- [ ] **Add job-agent as a project** in the Experience or Projects section
- [ ] **Feature the job-agent GitHub repo** once README is polished and repo is public
- [ ] **Update profile photo** (professional, clear, recent — if not already done)
- [ ] **Set "Open to Work"** with specific role types selected (not public badge unless
  you don't mind current employer seeing it — use "Share with recruiters only")
- [ ] **Write one substantive post** using the Decision Walkthrough or Contrarian
  Observation format from Section 7
- [ ] **Extract JSON profile fields** from Section 9 into the job-agent user profile seed

---

*Last updated: 2026-03-18*
*Feeds into: job-agent user profile schema, resume tailoring module, OSINT warm-path scoring*
