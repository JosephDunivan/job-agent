#!/usr/bin/env python3
"""
Quick benchmark runner — measures token baseline for all operations.

Usage:
    python scripts/run_benchmark.py              # Run all benchmarks
    python scripts/run_benchmark.py --report      # Show summary report only
    python scripts/run_benchmark.py --compare     # Compare v1 vs v2 prompts
    python scripts/run_benchmark.py --export csv  # Export data to CSV
"""

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.token_tracker import (
    tracked_generate,
    get_summary,
    get_comparison,
    print_summary,
    get_db,
)


def export_csv(output_path: str = "data/benchmarks/benchmark_export.csv"):
    """Export all benchmark runs to CSV."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM benchmark_runs ORDER BY timestamp").fetchall()
    conn.close()

    if not rows:
        print("No data to export.")
        return

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow(tuple(row))

    print(f"Exported {len(rows)} rows to {output_path}")


def compare_versions():
    """Compare v1 vs v2 prompt performance for all operations."""
    operations = [
        "extract_skills_from_jd",
        "tailor_resume_bullet",
        "skill_gap_analysis",
        "cover_letter_paragraph",
        "company_summary",
    ]

    print("\n" + "=" * 80)
    print("  PROMPT VERSION COMPARISON (V1 Baseline vs V2 Optimized)")
    print("=" * 80)

    for op in operations:
        data = get_comparison(op)
        if not data["versions"]:
            print(f"\n  {op}: No data yet")
            continue

        print(f"\n  {op}:")
        for v in data["versions"]:
            print(f"    {v['prompt_template_version']:15s} | "
                  f"runs={v['runs']:3d} | "
                  f"avg_in={v['avg_input']:6.0f} | "
                  f"avg_out={v['avg_output']:6.0f} | "
                  f"latency={v['avg_latency_ms']:8.0f}ms | "
                  f"cost=${v['avg_cost']:.8f} | "
                  f"quality={v['avg_quality'] or 'N/A'}")

        # Calculate savings if both versions exist
        versions = {v["prompt_template_version"]: v for v in data["versions"]}
        if "v1_baseline" in versions and "v2_optimized" in versions:
            v1 = versions["v1_baseline"]
            v2 = versions["v2_optimized"]
            if v1["avg_input"] and v2["avg_input"]:
                input_savings = (1 - v2["avg_input"] / v1["avg_input"]) * 100
                output_savings = (1 - v2["avg_output"] / v1["avg_output"]) * 100 if v1["avg_output"] else 0
                latency_savings = (1 - v2["avg_latency_ms"] / v1["avg_latency_ms"]) * 100 if v1["avg_latency_ms"] else 0
                print(f"    → Savings: input {input_savings:+.1f}% | output {output_savings:+.1f}% | latency {latency_savings:+.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Job Agent Token Benchmark Runner")
    parser.add_argument("--report", action="store_true", help="Show summary report")
    parser.add_argument("--compare", action="store_true", help="Compare prompt versions")
    parser.add_argument("--export", choices=["csv"], help="Export benchmark data")
    parser.add_argument("--operation", type=str, help="Filter by operation name")
    args = parser.parse_args()

    if args.report:
        print_summary(args.operation)
    elif args.compare:
        compare_versions()
    elif args.export == "csv":
        export_csv()
    else:
        print("Run pytest for full benchmarks:")
        print("  pytest tests/token_benchmark/ -v -s")
        print("\nOr use flags:")
        print("  --report   Show summary of collected data")
        print("  --compare  Compare v1 vs v2 prompt performance")
        print("  --export csv  Export all data to CSV")


if __name__ == "__main__":
    main()
