"""
Token Baseline Benchmark Tests

Establishes baseline token consumption for each operation type in the Job Agent.
Run these BEFORE applying optimizations, then re-run AFTER to measure improvement.

Usage:
    # Run all benchmarks (requires Ollama running locally)
    pytest tests/token_benchmark/test_token_baseline.py -v -s

    # Run specific benchmark
    pytest tests/token_benchmark/test_token_baseline.py::TestResumeOperations -v -s

    # Skip if Ollama is not available
    pytest tests/token_benchmark/test_token_baseline.py -v -s -m "not requires_ollama"
"""

import json
import os
import sys
import pytest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.token_tracker import (
    tracked_generate,
    tracked_chat,
    get_summary,
    print_summary,
    estimate_cost,
    get_db,
)

# --- Test Fixtures ---

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture(name: str) -> str:
    """Load a test fixture file."""
    path = FIXTURES_DIR / name
    if path.exists():
        return path.read_text()
    return ""


# --- Sample Data ---

SAMPLE_JOB_DESCRIPTION = """
Senior Full-Stack Developer — Remote

We're looking for a Senior Full-Stack Developer to join our engineering team.
You'll build and maintain web applications using React, Next.js, and Python.

Requirements:
- 5+ years of experience in full-stack web development
- Strong proficiency in React, TypeScript, and Next.js
- Backend experience with Python, FastAPI or Django
- Database experience (PostgreSQL, Redis)
- Experience with CI/CD pipelines and cloud platforms (AWS/GCP)
- Familiarity with Docker and container orchestration

Nice to have:
- Experience with LLM/AI integration
- Knowledge of graph databases
- Open source contributions
- SOX compliance or audit experience

Salary: $130,000 - $170,000
Location: Remote (US)
"""

SAMPLE_RESUME_BULLETS = [
    "Built and maintained React/Next.js web applications serving 50K+ daily users",
    "Designed Python automation pipelines that reduced manual processing time by 85%",
    "Implemented ODBC connectivity between NICE IEX and Avaya CMS for unified reporting",
    "Developed security-hardened deployment architecture for OpenClaw instance managing 800+ documents",
    "Created automated SOX audit test cases for role-based access control validation",
]

SAMPLE_RESUME_SECTION = """
## Experience

### Software Developer | Current Employer | 2022-Present
- Built and maintained React/Next.js web applications serving 50K+ daily users
- Designed Python automation pipelines that reduced manual processing time by 85%
- Implemented ODBC connectivity between NICE IEX and Avaya CMS for unified reporting
- Developed security-hardened deployment architecture for OpenClaw instance
- Created automated SOX audit test cases for role-based access control validation

### Skills
JavaScript/TypeScript, Python, React, Next.js, SQL, Docker, Git, Ollama, LangGraph
"""

SAMPLE_COMPANY_NAME = "Acme Technology Solutions"


# --- Helpers ---

def ollama_available() -> bool:
    """Check if Ollama is running."""
    import requests
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


requires_ollama = pytest.mark.skipif(
    not ollama_available(),
    reason="Ollama not running — skipping live benchmarks"
)


# --- Prompt Templates (Version 1 — Baseline, unoptimized) ---

PROMPTS_V1 = {
    "extract_skills_from_jd": {
        "system": "You are a helpful assistant that analyzes job descriptions.",
        "prompt": f"""Please carefully analyze the following job description and extract all the required skills, 
preferred skills, and qualifications mentioned. Organize them into categories and provide a comprehensive list.

Job Description:
{SAMPLE_JOB_DESCRIPTION}

Please provide your analysis in a structured format.""",
        "max_tokens": 500,
    },
    "tailor_resume_bullet": {
        "system": "You are a professional resume writer who helps tailor resumes to specific job postings.",
        "prompt": f"""I need you to rewrite the following resume bullet point so that it better aligns with the 
requirements of the job description provided below. Please maintain truthfulness and don't add any 
skills or experiences that aren't implied by the original bullet point. Make it compelling and 
action-oriented.

Original bullet point:
"{SAMPLE_RESUME_BULLETS[0]}"

Target job description:
{SAMPLE_JOB_DESCRIPTION}

Please provide the rewritten bullet point.""",
        "max_tokens": 200,
    },
    "skill_gap_analysis": {
        "system": "You are a career advisor who helps identify skill gaps between a candidate's profile and job requirements.",
        "prompt": f"""Please analyze the gap between my current skills and experience and the requirements of the 
job description below. Identify what skills I already have that match, what skills are missing, 
and recommend specific actions to close the gaps.

My resume:
{SAMPLE_RESUME_SECTION}

Job Description:
{SAMPLE_JOB_DESCRIPTION}

Please provide a detailed analysis.""",
        "max_tokens": 600,
    },
    "cover_letter_paragraph": {
        "system": "You are a professional cover letter writer.",
        "prompt": f"""Write one compelling opening paragraph for a cover letter for the following job. 
Reference my relevant experience but keep it concise and engaging.

My background:
{SAMPLE_RESUME_SECTION}

Job:
{SAMPLE_JOB_DESCRIPTION}

Write one paragraph only.""",
        "max_tokens": 300,
    },
    "company_summary": {
        "system": "You are a business intelligence analyst.",
        "prompt": f"""Summarize what you know about {SAMPLE_COMPANY_NAME}. Include: industry, approximate size, 
key products/services, recent news, and culture. If you don't have specific information, 
indicate what would need to be researched via OSINT tools.

Provide a concise briefing.""",
        "max_tokens": 400,
    },
}

# --- Optimized Prompt Templates (Version 2 — Token-efficient) ---

PROMPTS_V2 = {
    "extract_skills_from_jd": {
        "system": "Extract skills from job descriptions. Output JSON only.",
        "prompt": f"""Extract required_skills, preferred_skills, and qualifications as JSON arrays.

JD:
{SAMPLE_JOB_DESCRIPTION}""",
        "max_tokens": 300,
    },
    "tailor_resume_bullet": {
        "system": "Resume bullet rewriter. Truthful, concise, action-oriented.",
        "prompt": f"""Rewrite for this JD. Keep truthful. Max 25 words.

Bullet: "{SAMPLE_RESUME_BULLETS[0]}"

JD skills needed: React, Next.js, TypeScript, Python, CI/CD, cloud""",
        "max_tokens": 80,
    },
    "skill_gap_analysis": {
        "system": "Skill gap analyzer. Output JSON.",
        "prompt": f"""Compare resume skills to JD requirements. Output JSON with: matching_skills[], missing_skills[], recommended_actions[].

Resume skills: JavaScript, TypeScript, Python, React, Next.js, SQL, Docker, Git, Ollama, LangGraph, ODBC, SOX audit

JD requirements: React, TypeScript, Next.js, Python, FastAPI/Django, PostgreSQL, Redis, CI/CD, AWS/GCP, Docker, LLM/AI, graph databases""",
        "max_tokens": 300,
    },
    "cover_letter_paragraph": {
        "system": "Write one cover letter opening paragraph. Concise, specific, compelling.",
        "prompt": f"""Opening paragraph for: Senior Full-Stack Developer (Remote, $130-170K).
My strengths: React/Next.js (50K+ users), Python automation (85% time savings), security architecture, SOX audit.
Max 80 words.""",
        "max_tokens": 150,
    },
    "company_summary": {
        "system": "Company briefing. Concise facts only.",
        "prompt": f"""Brief on {SAMPLE_COMPANY_NAME}: industry, size, products, recent news, culture. Flag unknown items for OSINT research. Max 150 words.""",
        "max_tokens": 250,
    },
}


# --- Test Classes ---

class TestTokenEstimation:
    """Test cost estimation without requiring Ollama."""

    def test_cost_known_model(self):
        cost = estimate_cost("llama3.1:8b", 1000, 500)
        assert cost > 0
        assert cost < 0.001  # should be very small for 1500 tokens

    def test_cost_unknown_model(self):
        cost = estimate_cost("some-unknown-model:latest", 1000, 500)
        assert cost > 0  # falls back to default pricing

    def test_cost_zero_tokens(self):
        cost = estimate_cost("llama3.1:8b", 0, 0)
        assert cost == 0

    def test_cost_scaling(self):
        cost_small = estimate_cost("llama3.1:8b", 100, 50)
        cost_large = estimate_cost("llama3.1:8b", 10000, 5000)
        assert cost_large > cost_small
        assert cost_large == pytest.approx(cost_small * 100, rel=0.01)


class TestDatabaseOperations:
    """Test benchmark database without requiring Ollama."""

    def test_db_creation(self, tmp_path):
        """Verify database and tables are created."""
        import src.utils.token_tracker as tt
        original_path = tt.DB_PATH
        tt.DB_PATH = tmp_path / "test_metrics.db"
        try:
            conn = get_db()
            # Check tables exist
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t["name"] for t in tables]
            assert "benchmark_runs" in table_names
            assert "prompt_versions" in table_names
            assert "optimization_experiments" in table_names
            conn.close()
        finally:
            tt.DB_PATH = original_path

    def test_summary_empty_db(self, tmp_path):
        """Summary should work on empty database."""
        import src.utils.token_tracker as tt
        original_path = tt.DB_PATH
        tt.DB_PATH = tmp_path / "test_metrics.db"
        try:
            result = get_summary()
            assert result["summary"] == []
        finally:
            tt.DB_PATH = original_path


class TestPromptTokenCounting:
    """Measure prompt sizes without calling Ollama (token estimation via character count)."""

    def test_v1_vs_v2_prompt_sizes(self):
        """Compare character counts of v1 vs v2 prompts as a proxy for token savings."""
        print("\n" + "=" * 70)
        print("  PROMPT SIZE COMPARISON: V1 (Verbose) vs V2 (Optimized)")
        print("=" * 70)

        results = []
        for op_name in PROMPTS_V1:
            v1 = PROMPTS_V1[op_name]
            v2 = PROMPTS_V2[op_name]

            v1_chars = len(v1["system"]) + len(v1["prompt"])
            v2_chars = len(v2["system"]) + len(v2["prompt"])
            v1_est_tokens = v1_chars // 4  # rough estimate
            v2_est_tokens = v2_chars // 4
            savings = round((1 - v2_est_tokens / v1_est_tokens) * 100, 1) if v1_est_tokens > 0 else 0

            # max_tokens savings
            v1_max = v1["max_tokens"]
            v2_max = v2["max_tokens"]
            output_savings = round((1 - v2_max / v1_max) * 100, 1) if v1_max > 0 else 0

            results.append({
                "operation": op_name,
                "v1_est_tokens": v1_est_tokens,
                "v2_est_tokens": v2_est_tokens,
                "input_savings_pct": savings,
                "v1_max_output": v1_max,
                "v2_max_output": v2_max,
                "output_savings_pct": output_savings,
            })

            print(f"\n  {op_name}:")
            print(f"    Input:  V1={v1_est_tokens} tokens → V2={v2_est_tokens} tokens ({savings}% savings)")
            print(f"    Output: V1=max {v1_max} → V2=max {v2_max} ({output_savings}% savings)")

        # Aggregates
        avg_input_savings = sum(r["input_savings_pct"] for r in results) / len(results)
        avg_output_savings = sum(r["output_savings_pct"] for r in results) / len(results)
        print(f"\n  {'='*50}")
        print(f"  Average input token savings:  {avg_input_savings:.1f}%")
        print(f"  Average output cap savings:   {avg_output_savings:.1f}%")
        print(f"  {'='*50}\n")

        # Assert meaningful savings
        assert avg_input_savings > 20, f"Expected >20% input savings, got {avg_input_savings}%"


@requires_ollama
class TestResumeOperations:
    """Benchmark resume-related operations against Ollama."""

    def test_extract_skills_v1(self):
        """Baseline: verbose skill extraction."""
        p = PROMPTS_V1["extract_skills_from_jd"]
        result = tracked_generate(
            prompt=p["prompt"],
            system_prompt=p["system"],
            max_tokens=p["max_tokens"],
            operation="extract_skills_from_jd",
            prompt_version="v1_baseline",
            model="llama3.1:8b",
            notes="Baseline verbose prompt",
        )
        assert result["response"] is not None, f"Error: {result.get('error')}"
        m = result["metrics"]
        print(f"\n  [extract_skills v1] in={m['input_tokens']} out={m['output_tokens']} "
              f"latency={m['total_duration_ms']}ms cost=${m['equivalent_cost_usd']}")

    def test_extract_skills_v2(self):
        """Optimized: concise skill extraction."""
        p = PROMPTS_V2["extract_skills_from_jd"]
        result = tracked_generate(
            prompt=p["prompt"],
            system_prompt=p["system"],
            max_tokens=p["max_tokens"],
            operation="extract_skills_from_jd",
            prompt_version="v2_optimized",
            model="llama3.1:8b",
            notes="Optimized concise prompt, JSON output",
        )
        assert result["response"] is not None, f"Error: {result.get('error')}"
        m = result["metrics"]
        print(f"\n  [extract_skills v2] in={m['input_tokens']} out={m['output_tokens']} "
              f"latency={m['total_duration_ms']}ms cost=${m['equivalent_cost_usd']}")

    def test_tailor_bullet_v1(self):
        """Baseline: verbose bullet rewrite."""
        p = PROMPTS_V1["tailor_resume_bullet"]
        result = tracked_generate(
            prompt=p["prompt"],
            system_prompt=p["system"],
            max_tokens=p["max_tokens"],
            operation="tailor_resume_bullet",
            prompt_version="v1_baseline",
            model="llama3.1:8b",
        )
        assert result["response"] is not None
        m = result["metrics"]
        print(f"\n  [tailor_bullet v1] in={m['input_tokens']} out={m['output_tokens']} "
              f"latency={m['total_duration_ms']}ms cost=${m['equivalent_cost_usd']}")

    def test_tailor_bullet_v2(self):
        """Optimized: concise bullet rewrite."""
        p = PROMPTS_V2["tailor_resume_bullet"]
        result = tracked_generate(
            prompt=p["prompt"],
            system_prompt=p["system"],
            max_tokens=p["max_tokens"],
            operation="tailor_resume_bullet",
            prompt_version="v2_optimized",
            model="llama3.1:8b",
        )
        assert result["response"] is not None
        m = result["metrics"]
        print(f"\n  [tailor_bullet v2] in={m['input_tokens']} out={m['output_tokens']} "
              f"latency={m['total_duration_ms']}ms cost=${m['equivalent_cost_usd']}")


@requires_ollama
class TestModelRouting:
    """Benchmark same task across different model sizes to find optimal routing."""

    MODELS_TO_TEST = ["llama3.2:1b", "llama3.1:8b"]  # Add larger models as available

    def test_skill_extraction_across_models(self):
        """Compare skill extraction quality and cost across model sizes."""
        p = PROMPTS_V2["extract_skills_from_jd"]
        print("\n  Model Routing Benchmark: extract_skills_from_jd")
        print("  " + "-" * 50)

        for model in self.MODELS_TO_TEST:
            try:
                result = tracked_generate(
                    prompt=p["prompt"],
                    system_prompt=p["system"],
                    max_tokens=p["max_tokens"],
                    operation="extract_skills_from_jd",
                    prompt_version="v2_optimized",
                    model=model,
                    notes=f"Model routing test: {model}",
                )
                if result["response"]:
                    m = result["metrics"]
                    print(f"  {model:20s} | in={m['input_tokens']:4d} out={m['output_tokens']:4d} "
                          f"| {m['total_duration_ms']:8.0f}ms | ${m['equivalent_cost_usd']:.8f}")
                else:
                    print(f"  {model:20s} | SKIPPED (model not available)")
            except Exception as e:
                print(f"  {model:20s} | ERROR: {e}")


@requires_ollama
class TestResourceConsumption:
    """Measure system resource impact of LLM operations."""

    def test_memory_baseline(self):
        """Capture memory usage before and after a model call."""
        import psutil

        # Before
        mem_before = psutil.Process().memory_info().rss / (1024 * 1024)
        sys_mem_before = psutil.virtual_memory().percent

        # Make a call
        result = tracked_generate(
            prompt="Say hello in exactly 5 words.",
            model="llama3.1:8b",
            max_tokens=20,
            operation="resource_test",
            notes="Memory baseline test",
        )

        # After
        mem_after = psutil.Process().memory_info().rss / (1024 * 1024)
        sys_mem_after = psutil.virtual_memory().percent

        print(f"\n  Memory: process {mem_before:.1f}MB → {mem_after:.1f}MB "
              f"(delta: {mem_after - mem_before:+.1f}MB)")
        print(f"  System: {sys_mem_before}% → {sys_mem_after}%")

        if result["metrics"]:
            print(f"  Model load time: {result['metrics']['model_load_ms']}ms")


class TestBenchmarkReporting:
    """Test the reporting functionality."""

    def test_print_summary(self):
        """Just verify print_summary doesn't crash."""
        print_summary()

    def test_get_summary_structure(self):
        """Verify summary returns expected structure."""
        result = get_summary()
        assert "summary" in result
        assert "generated_at" in result
        assert isinstance(result["summary"], list)


# --- Entrypoint ---

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
