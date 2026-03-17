"""
Token & Resource Tracker for Job Agent

Wraps Ollama API calls to automatically capture and store:
- Token counts (input/output)
- Latency metrics (prompt eval, generation, total)
- System resource usage (CPU, RAM)
- Equivalent cloud API cost estimates
- Prompt version tracking

All data is persisted to SQLite for benchmarking and optimization analysis.
"""

import json
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import psutil
import requests

# --- Configuration ---

# Default Ollama endpoint
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Equivalent cloud pricing per 1M tokens (for cost estimation)
# These are approximate and should be updated periodically
MODEL_PRICING = {
    "llama3.1:8b":    {"input": 0.10, "output": 0.10},
    "llama3.1:70b":   {"input": 0.60, "output": 0.60},
    "llama3.2:1b":    {"input": 0.04, "output": 0.04},
    "llama3.2:3b":    {"input": 0.06, "output": 0.06},
    "gemma2:2b":      {"input": 0.05, "output": 0.05},
    "mistral:7b":     {"input": 0.10, "output": 0.10},
    "deepseek-r1:8b": {"input": 0.14, "output": 0.14},
    "phi3:mini":      {"input": 0.05, "output": 0.05},
    "qwen2.5:7b":     {"input": 0.10, "output": 0.10},
}

# Fallback pricing for unknown models
DEFAULT_PRICING = {"input": 0.15, "output": 0.15}

# --- Database ---

DB_PATH = Path(__file__).parent.parent.parent / "data" / "benchmarks" / "token_metrics.db"


def get_db() -> sqlite3.Connection:
    """Get or create the benchmark database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection):
    """Create tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS benchmark_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            model TEXT NOT NULL,
            prompt_template_version TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_duration_ms REAL,
            prompt_eval_ms REAL,
            generation_ms REAL,
            model_load_ms REAL,
            prompt_tokens_per_sec REAL,
            generation_tokens_per_sec REAL,
            equivalent_cost_usd REAL,
            quality_score REAL,
            compression_ratio REAL,
            cache_hit BOOLEAN DEFAULT 0,
            notes TEXT,
            system_cpu_percent REAL,
            system_memory_mb REAL,
            raw_response TEXT
        );

        CREATE TABLE IF NOT EXISTS prompt_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation TEXT NOT NULL,
            version INTEGER NOT NULL,
            template TEXT NOT NULL,
            token_count INTEGER,
            created_at TEXT NOT NULL,
            notes TEXT,
            UNIQUE(operation, version)
        );

        CREATE TABLE IF NOT EXISTS optimization_experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            experiment_name TEXT NOT NULL,
            description TEXT,
            baseline_avg_tokens REAL,
            optimized_avg_tokens REAL,
            token_savings_percent REAL,
            quality_delta REAL,
            started_at TEXT,
            completed_at TEXT,
            conclusion TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_runs_operation ON benchmark_runs(operation);
        CREATE INDEX IF NOT EXISTS idx_runs_model ON benchmark_runs(model);
        CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON benchmark_runs(timestamp);
    """)
    conn.commit()


# --- System Metrics ---

def get_system_metrics() -> dict:
    """Capture current system resource usage."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_mb": psutil.Process().memory_info().rss / (1024 * 1024),
        "system_memory_percent": psutil.virtual_memory().percent,
    }


# --- Cost Estimation ---

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate equivalent cloud API cost in USD."""
    pricing = MODEL_PRICING.get(model, DEFAULT_PRICING)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 8)


# --- Ollama Wrapper ---

def ns_to_ms(ns: int) -> float:
    """Convert nanoseconds to milliseconds."""
    return round(ns / 1_000_000, 2) if ns else 0.0


def tracked_generate(
    prompt: str,
    model: str = "llama3.1:8b",
    operation: str = "unknown",
    system_prompt: str = "",
    max_tokens: Optional[int] = None,
    temperature: float = 0.7,
    prompt_version: Optional[str] = None,
    notes: str = "",
    store: bool = True,
) -> dict:
    """
    Call Ollama's /api/generate with full metric tracking.

    Returns dict with:
        - response: the generated text
        - metrics: all captured metrics
        - run_id: unique identifier for this call
    """
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()

    # Capture pre-call system metrics
    sys_metrics = get_system_metrics()

    # Build request
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if system_prompt:
        payload["system"] = system_prompt
    if max_tokens:
        payload["options"]["num_predict"] = max_tokens

    # Make the call
    wall_start = time.perf_counter()
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "response": None,
            "error": "Ollama not running or unreachable",
            "metrics": None,
            "run_id": run_id,
        }
    except Exception as e:
        return {
            "response": None,
            "error": str(e),
            "metrics": None,
            "run_id": run_id,
        }
    wall_end = time.perf_counter()

    # Extract Ollama metrics
    input_tokens = data.get("prompt_eval_count", 0)
    output_tokens = data.get("eval_count", 0)
    total_duration_ms = ns_to_ms(data.get("total_duration", 0))
    prompt_eval_ms = ns_to_ms(data.get("prompt_eval_duration", 0))
    generation_ms = ns_to_ms(data.get("eval_duration", 0))
    model_load_ms = ns_to_ms(data.get("load_duration", 0))

    # Derived metrics
    prompt_tps = round(input_tokens / (prompt_eval_ms / 1000), 1) if prompt_eval_ms > 0 else 0
    gen_tps = round(output_tokens / (generation_ms / 1000), 1) if generation_ms > 0 else 0
    equiv_cost = estimate_cost(model, input_tokens, output_tokens)

    metrics = {
        "run_id": run_id,
        "timestamp": timestamp,
        "operation": operation,
        "model": model,
        "prompt_template_version": prompt_version,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "total_duration_ms": total_duration_ms,
        "prompt_eval_ms": prompt_eval_ms,
        "generation_ms": generation_ms,
        "model_load_ms": model_load_ms,
        "wall_time_ms": round((wall_end - wall_start) * 1000, 2),
        "prompt_tokens_per_sec": prompt_tps,
        "generation_tokens_per_sec": gen_tps,
        "equivalent_cost_usd": equiv_cost,
        "system_cpu_percent": sys_metrics["cpu_percent"],
        "system_memory_mb": round(sys_metrics["memory_mb"], 1),
    }

    # Store to database
    if store:
        try:
            conn = get_db()
            conn.execute("""
                INSERT INTO benchmark_runs (
                    run_id, timestamp, operation, model, prompt_template_version,
                    input_tokens, output_tokens, total_duration_ms, prompt_eval_ms,
                    generation_ms, model_load_ms, prompt_tokens_per_sec,
                    generation_tokens_per_sec, equivalent_cost_usd, quality_score,
                    compression_ratio, cache_hit, notes, system_cpu_percent,
                    system_memory_mb, raw_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, timestamp, operation, model, prompt_version,
                input_tokens, output_tokens, total_duration_ms, prompt_eval_ms,
                generation_ms, model_load_ms, prompt_tps,
                gen_tps, equiv_cost, None,
                None, False, notes, sys_metrics["cpu_percent"],
                round(sys_metrics["memory_mb"], 1),
                json.dumps(data.get("response", "")[:500]),  # truncate raw response
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            metrics["db_error"] = str(e)

    return {
        "response": data.get("response", ""),
        "metrics": metrics,
        "run_id": run_id,
    }


def tracked_chat(
    messages: list[dict],
    model: str = "llama3.1:8b",
    operation: str = "unknown",
    max_tokens: Optional[int] = None,
    temperature: float = 0.7,
    prompt_version: Optional[str] = None,
    notes: str = "",
    store: bool = True,
) -> dict:
    """
    Call Ollama's /api/chat with full metric tracking.

    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    """
    run_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()
    sys_metrics = get_system_metrics()

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if max_tokens:
        payload["options"]["num_predict"] = max_tokens

    wall_start = time.perf_counter()
    try:
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "response": None,
            "error": "Ollama not running or unreachable",
            "metrics": None,
            "run_id": run_id,
        }
    except Exception as e:
        return {
            "response": None,
            "error": str(e),
            "metrics": None,
            "run_id": run_id,
        }
    wall_end = time.perf_counter()

    input_tokens = data.get("prompt_eval_count", 0)
    output_tokens = data.get("eval_count", 0)
    total_duration_ms = ns_to_ms(data.get("total_duration", 0))
    prompt_eval_ms = ns_to_ms(data.get("prompt_eval_duration", 0))
    generation_ms = ns_to_ms(data.get("eval_duration", 0))
    model_load_ms = ns_to_ms(data.get("load_duration", 0))

    prompt_tps = round(input_tokens / (prompt_eval_ms / 1000), 1) if prompt_eval_ms > 0 else 0
    gen_tps = round(output_tokens / (generation_ms / 1000), 1) if generation_ms > 0 else 0
    equiv_cost = estimate_cost(model, input_tokens, output_tokens)

    response_text = data.get("message", {}).get("content", "")

    metrics = {
        "run_id": run_id,
        "timestamp": timestamp,
        "operation": operation,
        "model": model,
        "prompt_template_version": prompt_version,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "total_duration_ms": total_duration_ms,
        "prompt_eval_ms": prompt_eval_ms,
        "generation_ms": generation_ms,
        "model_load_ms": model_load_ms,
        "wall_time_ms": round((wall_end - wall_start) * 1000, 2),
        "prompt_tokens_per_sec": prompt_tps,
        "generation_tokens_per_sec": gen_tps,
        "equivalent_cost_usd": equiv_cost,
        "system_cpu_percent": sys_metrics["cpu_percent"],
        "system_memory_mb": round(sys_metrics["memory_mb"], 1),
    }

    if store:
        try:
            conn = get_db()
            conn.execute("""
                INSERT INTO benchmark_runs (
                    run_id, timestamp, operation, model, prompt_template_version,
                    input_tokens, output_tokens, total_duration_ms, prompt_eval_ms,
                    generation_ms, model_load_ms, prompt_tokens_per_sec,
                    generation_tokens_per_sec, equivalent_cost_usd, quality_score,
                    compression_ratio, cache_hit, notes, system_cpu_percent,
                    system_memory_mb, raw_response
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id, timestamp, operation, model, prompt_version,
                input_tokens, output_tokens, total_duration_ms, prompt_eval_ms,
                generation_ms, model_load_ms, prompt_tps,
                gen_tps, equiv_cost, None,
                None, False, notes, sys_metrics["cpu_percent"],
                round(sys_metrics["memory_mb"], 1),
                json.dumps(response_text[:500]),
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            metrics["db_error"] = str(e)

    return {
        "response": response_text,
        "metrics": metrics,
        "run_id": run_id,
    }


# --- Reporting ---

def get_summary(operation: Optional[str] = None, last_n: int = 100) -> dict:
    """Get summary statistics for benchmark runs."""
    conn = get_db()

    where = "WHERE operation = ?" if operation else ""
    params = (operation,) if operation else ()

    rows = conn.execute(f"""
        SELECT
            operation,
            model,
            COUNT(*) as call_count,
            ROUND(AVG(input_tokens), 1) as avg_input_tokens,
            ROUND(AVG(output_tokens), 1) as avg_output_tokens,
            ROUND(AVG(input_tokens + output_tokens), 1) as avg_total_tokens,
            ROUND(AVG(total_duration_ms), 1) as avg_latency_ms,
            ROUND(AVG(generation_tokens_per_sec), 1) as avg_gen_tps,
            ROUND(SUM(equivalent_cost_usd), 6) as total_equiv_cost,
            ROUND(AVG(equivalent_cost_usd), 8) as avg_equiv_cost,
            MIN(timestamp) as first_call,
            MAX(timestamp) as last_call
        FROM benchmark_runs
        {where}
        GROUP BY operation, model
        ORDER BY call_count DESC
        LIMIT ?
    """, (*params, last_n)).fetchall()

    conn.close()

    return {
        "summary": [dict(r) for r in rows],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def get_comparison(operation: str) -> dict:
    """Compare metrics across prompt versions for an operation."""
    conn = get_db()

    rows = conn.execute("""
        SELECT
            prompt_template_version,
            COUNT(*) as runs,
            ROUND(AVG(input_tokens), 1) as avg_input,
            ROUND(AVG(output_tokens), 1) as avg_output,
            ROUND(AVG(total_duration_ms), 1) as avg_latency_ms,
            ROUND(AVG(equivalent_cost_usd), 8) as avg_cost,
            ROUND(AVG(quality_score), 2) as avg_quality
        FROM benchmark_runs
        WHERE operation = ? AND prompt_template_version IS NOT NULL
        GROUP BY prompt_template_version
        ORDER BY prompt_template_version
    """, (operation,)).fetchall()

    conn.close()
    return {"operation": operation, "versions": [dict(r) for r in rows]}


def print_summary(operation: Optional[str] = None):
    """Print a formatted summary to stdout."""
    data = get_summary(operation)
    if not data["summary"]:
        print("No benchmark data yet.")
        return

    print(f"\n{'='*80}")
    print(f"  TOKEN & RESOURCE BENCHMARK SUMMARY")
    print(f"  Generated: {data['generated_at']}")
    print(f"{'='*80}\n")

    for row in data["summary"]:
        print(f"  Operation: {row['operation']}")
        print(f"  Model:     {row['model']}")
        print(f"  Calls:     {row['call_count']}")
        print(f"  Avg tokens (in/out/total): {row['avg_input_tokens']} / {row['avg_output_tokens']} / {row['avg_total_tokens']}")
        print(f"  Avg latency:    {row['avg_latency_ms']} ms")
        print(f"  Avg gen speed:  {row['avg_gen_tps']} tokens/sec")
        print(f"  Total est cost: ${row['total_equiv_cost']}")
        print(f"  Avg est cost:   ${row['avg_equiv_cost']}")
        print(f"  Period: {row['first_call']} → {row['last_call']}")
        print(f"  {'-'*60}")


if __name__ == "__main__":
    print_summary()
