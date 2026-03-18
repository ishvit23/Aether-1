"""Sweep result analyzer for Aether-1 experiments.

Reads a sweep CSV and reports the best/worst parameter combinations.

Usage:
    uv run python experiments/sweep_report.py experiments/results/sweep_YYYYMMDD_HHMMSS.csv
"""

import argparse
import csv
import sys


def load_results(path: str) -> list[dict]:
    """Load sweep results from CSV."""
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            row["final_population"] = int(row["final_population"])
            row["max_population"] = int(row["max_population"])
            row["extinction_tick"] = int(row["extinction_tick"]) if row["extinction_tick"] else None
            row["success"] = row["success"] == "True"
            rows.append(row)
    return rows


def score(row: dict, max_ticks: int = 1000) -> float:
    """Score a run: survival ticks × final population."""
    survival = max_ticks if row["extinction_tick"] is None else row["extinction_tick"]
    return survival * row["final_population"]


def main():
    parser = argparse.ArgumentParser(description="Aether-1 Sweep Report")
    parser.add_argument("csv_file", help="Path to sweep results CSV")
    parser.add_argument("--ticks", type=int, default=1000, help="Max ticks (for scoring)")
    args = parser.parse_args()

    rows = load_results(args.csv_file)
    if not rows:
        print("No results found.")
        sys.exit(1)

    # Identify sweep parameter columns
    known_cols = {
        "seed",
        "success",
        "final_population",
        "max_population",
        "extinction_tick",
    }
    sweep_cols = [c for c in rows[0] if c not in known_cols]

    # Group by parameter combination
    combos: dict[tuple, list[dict]] = {}
    for row in rows:
        key = tuple(row.get(c, "") for c in sweep_cols)
        combos.setdefault(key, []).append(row)

    # Compute per-combo averages
    results = []
    for key, runs in combos.items():
        successful = [r for r in runs if r["success"]]
        if not successful:
            continue
        avg_pop = sum(r["final_population"] for r in successful) / len(successful)
        avg_max = sum(r["max_population"] for r in successful) / len(successful)
        survived = sum(1 for r in successful if r["extinction_tick"] is None)
        avg_score = sum(score(r, args.ticks) for r in successful) / len(successful)
        results.append(
            {
                "params": dict(zip(sweep_cols, key, strict=False)),
                "avg_final_pop": round(avg_pop, 1),
                "avg_max_pop": round(avg_max, 1),
                "survived_ratio": f"{survived}/{len(successful)}",
                "avg_score": round(avg_score, 0),
                "n_runs": len(successful),
            }
        )

    results.sort(key=lambda x: x["avg_score"], reverse=True)

    # Print report
    print("=" * 70)
    print("AETHER-1 SWEEP REPORT")
    print("=" * 70)
    print(f"File: {args.csv_file}")
    print(f"Total runs: {len(rows)} | Combinations: {len(results)}")

    if sweep_cols:
        print(f"Sweep parameters: {', '.join(sweep_cols)}")

    if results:
        print()
        print("🏆 BEST COMBINATION:")
        best = results[0]
        for k, v in best["params"].items():
            print(f"    {k} = {v}")
        print(f"    Avg final pop: {best['avg_final_pop']}")
        print(f"    Survived: {best['survived_ratio']}")
        print(f"    Score: {best['avg_score']}")

        if len(results) > 1:
            print()
            print("💀 WORST COMBINATION:")
            worst = results[-1]
            for k, v in worst["params"].items():
                print(f"    {k} = {v}")
            print(f"    Avg final pop: {worst['avg_final_pop']}")
            print(f"    Survived: {worst['survived_ratio']}")
            print(f"    Score: {worst['avg_score']}")

        print()
        print("ALL COMBINATIONS (sorted by score):")
        print("-" * 70)
        header = "  ".join(f"{c:>15}" for c in sweep_cols)
        header += "  avg_pop  survived  score"
        print(header)
        print("-" * 70)
        for r in results:
            vals = "  ".join(f"{r['params'].get(c, ''):>15}" for c in sweep_cols)
            print(f"{vals}  {r['avg_final_pop']:>7}  {r['survived_ratio']:>8}  {r['avg_score']:>7}")

    print("=" * 70)


if __name__ == "__main__":
    main()
