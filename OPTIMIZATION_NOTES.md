# Token & Resource Optimization — Research Notes

> **Purpose:** Collect and organize everything we know about optimizing LLM token usage, resource consumption, and cost management. This drives our iterative build process — every feature we build should be as token-efficient as possible from day one.
> **Last updated:** 2026-03-17

---

## 1. Why This Comes First

Before building any feature, we need to understand:
- How many tokens each operation costs (baseline measurement)
- Where tokens are wasted (prompt bloat, redundant context, uncompressed inputs)
- What optimization techniques exist and which apply to our use cases
- How to track and benchmark continuously so we catch regressions

This data informs every architecture decision: which model to use per task, how to structure prompts, whether to cache, when to compress.

---

## 2. Token Economics — What We Know

### 2.1 How Tokens Work

- 1 token ≈ 4 characters of English text ≈ ¾ of a word
- 100 words ≈ 133 tokens
- Cost formula: `cost = (input_tokens × input_price) + (output_tokens × output_price)`
- For Ollama (local): cost is compute time, not dollars — but token count still affects latency and memory

### 2.2 Ollama's Built-in Metrics

Ollama API responses include these metrics (per the [official docs](https://docs.ollama.com/api/usage)):

| Metric | What It Measures |
|--------|-----------------|
| `total_duration` | Total response generation time (nanoseconds) |
| `load_duration` | Time to load the model (nanoseconds) |
| `prompt_eval_count` | Number of input tokens processed |
| `prompt_eval_duration` | Time to evaluate the prompt (nanoseconds) |
| `eval_count` | Number of output tokens generated |
| `eval_duration` | Time to generate output tokens (nanoseconds) |

These are free — we just need to capture and store them.

### 2.3 Industry Benchmarks

From production case studies (sources: [Redis](https://redis.io/blog/llm-token-optimization-speed-up-apps/), [LinkedIn/Dedeoglu](https://www.linkedin.com/pulse/token-per-task-economics-6-techniques-cut-llm-spend-50-ercin-dedeoglu-x1o8f), [Glukhov](https://www.glukhov.org/post/2025/11/cost-effective-llm-applications/)):

| Technique | Typical Savings | Complexity | Our Priority |
|-----------|----------------|------------|-------------|
| Prompt compression (tighten wording) | 30-65% token reduction | Low | **Phase 1** |
| Model routing (small model for simple tasks) | 25-40% cost reduction | Medium | **Phase 1** |
| Semantic caching (reuse similar answers) | 10-30% fewer API calls | Medium | **Phase 2** |
| RAG optimization (fewer/better chunks) | 20-30% context reduction | Medium | **Phase 2** |
| Conversation history pruning | 15% context reduction | Low | **Phase 1** |
| Batch processing (group similar tasks) | 10-50% token reduction | Low | **Phase 1** |
| LLMLingua prompt compression | Up to 20x compression | Medium | **Evaluate** |
| max_tokens / output constraints | Prevents runaway generation | Low | **Phase 1** |

### 2.4 Compounding Effect

These techniques stack. Real-world example from Dedeoglu:
- Baseline: 5,000 tokens/task at $0.0125
- After all optimizations: ~2,700 tokens/task at $0.0034
- **73% cost cut**

---

## 3. Optimization Techniques — Detailed Notes

### 3.1 Prompt Engineering for Token Efficiency (Phase 1)

**Do:**
- Lead with keywords, not conversational padding
- Use structured output formats (JSON schemas) — models follow them tightly
- Set explicit output length constraints: "Answer in 50 words" + `max_tokens=100`
- Use few-shot examples only when zero-shot fails
- Remove system prompt redundancy across calls

**Don't:**
- Repeat instructions the model already knows from system prompt
- Include full conversation history when a summary suffices
- Send entire documents when you only need a section

**Before/After examples:**

| Task | Verbose Prompt (tokens) | Optimized Prompt (tokens) | Savings |
|------|------------------------|--------------------------|---------|
| Summarize JD | "Please provide a comprehensive summary of the following job description, highlighting the key requirements..." (~25 tokens) | "Extract: title, skills, requirements, seniority. JSON output." (~12 tokens) | 52% |
| Tailor resume bullet | "Given the following job description and my resume, please rewrite this bullet point to better align with..." (~22 tokens overhead) | "Rewrite bullet for this JD. Keep truthful. Max 20 words." (~12 tokens overhead) | 45% |

### 3.2 Model Routing (Phase 1)

Not every task needs the biggest model. Strategy:

| Task Type | Model Tier | Example Models |
|-----------|-----------|----------------|
| Classification, filtering, keyword extraction | Small/fast | gemma2:2b, phi3:mini, llama3.2:1b |
| Resume bullet rewriting, cover letter sections | Medium | llama3.1:8b, mistral:7b |
| Full resume tailoring, complex analysis | Large | llama3.1:70b, deepseek-coder-v2 |

**Routing logic:** Score task complexity → pick cheapest model that meets quality threshold → fall back to larger if quality check fails.

### 3.3 LLMLingua Prompt Compression (Evaluate)

[Microsoft LLMLingua](https://github.com/microsoft/LLMLingua) (MIT license) compresses prompts up to 20x using a small model to strip non-essential tokens.

- LLMLingua-2 uses a BERT-level encoder — fast (3-6x faster than v1)
- Works well for long contexts (RAG, document analysis)
- Not ideal for structured data / tables
- Python: `pip install llmlingua`

**Our evaluation plan:**
1. Measure baseline token counts for our top 5 prompt types
2. Apply LLMLingua-2 at 0.5 and 0.33 compression ratios
3. Compare output quality (LLM-as-judge) vs. token savings
4. Decision: use if quality loss < 5% at > 40% compression

### 3.4 Semantic Caching (Phase 2)

Use embedding similarity to cache LLM responses. If a new query is semantically similar to a cached one (cosine similarity > 0.85), return cached response.

**Tools:**
- [Redis + RedisVL SemanticCache](https://redis.io/docs/latest/develop/ai/redisvl/0.6.0/user_guide/llmcache/) — production-grade
- [GPTCache](https://github.com/zilliztech/GPTCache) — open source, supports multiple backends
- Custom: sentence-transformers + SQLite/FAISS for lightweight local option

**Our use cases:**
- Same company researched by multiple job postings → cache company OSINT
- Similar JDs from same employer → cache skill extraction
- Repeated skill gap analysis prompts → cache learning recommendations

### 3.5 Output Constraint Patterns (Phase 1)

Always set `max_tokens` in Ollama calls. Without it, models over-generate.

| Task | Recommended max_tokens | Rationale |
|------|----------------------|-----------|
| Skill extraction from JD | 200 | Short list of skills |
| Resume bullet rewrite | 100 | Single bullet point |
| Cover letter paragraph | 300 | One focused paragraph |
| Full cover letter | 800 | Complete letter |
| Skill gap analysis | 500 | Structured comparison |
| Company summary from OSINT | 400 | Key facts only |

---

## 4. What We Need to Measure

### 4.1 Baseline Metrics (Before Any Optimization)

For each prompt type in our system, capture:

| Metric | How |
|--------|-----|
| Input token count | Ollama `prompt_eval_count` |
| Output token count | Ollama `eval_count` |
| Total latency | Ollama `total_duration` |
| Prompt eval speed | `prompt_eval_count / prompt_eval_duration` (tokens/sec) |
| Generation speed | `eval_count / eval_duration` (tokens/sec) |
| Model load time | Ollama `load_duration` |
| Memory usage | `ollama ps` or system metrics |
| Quality score | LLM-as-judge on output |

### 4.2 Per-Operation Cost Model

Even though Ollama is local, we should track "equivalent API cost" so we can:
1. Estimate what it would cost if we switched to cloud APIs
2. Compare optimization techniques using a dollar metric
3. Set budgets and alerts

**Equivalent pricing (as of March 2026):**

| Model | Approx. equivalent $/1M input tokens | Approx. equivalent $/1M output tokens |
|-------|--------------------------------------|--------------------------------------|
| llama3.1:8b | $0.10 (Groq/Together pricing) | $0.10 |
| llama3.1:70b | $0.60 | $0.60 |
| gemma2:2b | $0.05 | $0.05 |
| mistral:7b | $0.10 | $0.10 |

### 4.3 Continuous Tracking

Every LLM call in our system should log:
```json
{
  "timestamp": "2026-03-17T14:30:00Z",
  "operation": "tailor_resume_bullet",
  "model": "llama3.1:8b",
  "input_tokens": 450,
  "output_tokens": 85,
  "total_duration_ms": 2340,
  "prompt_eval_ms": 890,
  "generation_ms": 1200,
  "quality_score": null,
  "cache_hit": false,
  "compression_applied": false,
  "equivalent_cost_usd": 0.0000535
}
```

---

## 5. Open Source Tools We'll Use

| Tool | Purpose | Install |
|------|---------|---------|
| **tiktoken** | Token counting (OpenAI-compatible, useful for cost estimates) | `pip install tiktoken` |
| **Ollama API metrics** | Native token counts + timing from every call | Built into Ollama responses |
| **LLMLingua-2** | Prompt compression (evaluate) | `pip install llmlingua` |
| **sentence-transformers** | Embeddings for semantic caching | `pip install sentence-transformers` |
| **SQLite** | Store benchmark data locally | Built into Python |
| **matplotlib / plotly** | Visualize token usage trends | `pip install matplotlib plotly` |
| **psutil** | System resource monitoring (CPU, RAM, GPU) | `pip install psutil` |

---

## 6. Our Data — What We're Collecting

### 6.1 Benchmark Database Schema

```sql
CREATE TABLE benchmark_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,           -- UUID for this benchmark run
    timestamp TEXT NOT NULL,
    operation TEXT NOT NULL,        -- e.g., 'tailor_resume', 'extract_skills'
    model TEXT NOT NULL,
    prompt_template TEXT,           -- which prompt version was used
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_duration_ms REAL,
    prompt_eval_ms REAL,
    generation_ms REAL,
    model_load_ms REAL,
    tokens_per_second REAL,
    equivalent_cost_usd REAL,
    quality_score REAL,            -- 1-10, from LLM-as-judge or manual
    compression_ratio REAL,        -- if LLMLingua was applied
    cache_hit BOOLEAN DEFAULT FALSE,
    notes TEXT,
    system_cpu_percent REAL,
    system_memory_mb REAL
);

CREATE TABLE prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    version INTEGER NOT NULL,
    template TEXT NOT NULL,
    token_count INTEGER,
    created_at TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE optimization_experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_name TEXT NOT NULL,
    description TEXT,
    baseline_avg_tokens REAL,
    optimized_avg_tokens REAL,
    token_savings_percent REAL,
    quality_delta REAL,            -- change in quality score
    started_at TEXT,
    completed_at TEXT,
    conclusion TEXT
);
```

### 6.2 Fixture Data for Benchmarks

We need consistent test inputs to produce comparable measurements:

- **5 sample resumes** (varying lengths: short/medium/long, different roles)
- **10 sample job descriptions** (dev, audit, freelance, remote, on-site)
- **5 sample company profiles** (small startup, mid-size, enterprise, government, non-profit)
- **Standard prompt set** (one per operation type) with version tracking

---

## 7. Session Log

### 2026-03-17 — Initial Research

**Sources reviewed:**
- [Ollama API usage docs](https://docs.ollama.com/api/usage) — native metrics available
- [Redis: LLM Token Optimization](https://redis.io/blog/llm-token-optimization-speed-up-apps/) — semantic caching, prompt tightening, compression
- [Token-Per-Task Economics](https://www.linkedin.com/pulse/token-per-task-economics-6-techniques-cut-llm-spend-50-ercin-dedeoglu-x1o8f) — 6 techniques, 73% cost cut achievable
- [Glukhov: Cost-Effective LLM Applications](https://www.glukhov.org/post/2025/11/cost-effective-llm-applications/) — 81% savings case study
- [Microsoft LLMLingua](https://github.com/microsoft/LLMLingua) — up to 20x prompt compression, MIT license
- [Reddit: Monitoring Ollama](https://www.reddit.com/r/ollama/comments/1rcxt3m/how_are_you_monitoring_your_ollama_callsusage/) — OpenTelemetry + SigNoz dashboard approach
- [Ollama GitHub #11118](https://github.com/ollama/ollama/issues/11118) — token tracking feature request (not yet built in)
- [IBM: Token Optimization](https://developer.ibm.com/articles/awb-token-optimization-backbone-of-effective-prompt-engineering/) — structured prompt strategies
- [Lakera: Prompt Engineering Guide 2026](https://www.lakera.ai/blog/prompt-engineering-guide) — compression challenge: cut 40%, A/B test

**Key decisions:**
- Phase 1 priorities: prompt tightening, model routing, output constraints, batch processing
- Phase 2: semantic caching, LLMLingua evaluation
- All LLM calls will log token metrics from day one
- Benchmark database tracks everything in SQLite
- Equivalent cost tracking even for local Ollama (enables cloud migration estimates)
