"""Metric comparison utility for Aether-1 runs.

Compares multiple simulation metrics CSVs side-by-side.

Usage:
    uv run python experiments/compare_runs.py run1.csv run2.csv run3.csv
    uv run python experiments/compare_runs.py run1.csv run2.csv --metric avg_energy
"""

import argparse
import csv
import sys


def load_metrics(path: str) -> list[dict]:
    """Load metrics from a CSV file."""
    with open(path) as f:
        return list(csv.DictReader(f))


def analyze(rows: list[dict], metric: str) -> dict:
    """Compute summary statistics for a metric column."""
    values = [float(r[metric]) for r in rows if metric in r]
    if not values:
        return {"final": 0, "max": 0, "min": 0, "avg": 0, "ticks": 0}

    pops = [int(r["population"]) for r in rows]
    extinction = None
    for r in rows:
        if int(r["population"]) == 0:
            extinction = int(r["tick"])
            break

    return {
        "final": values[-1],
        "max": max(values),
        "min": min(values),
        "avg": round(sum(values) / len(values), 2),
        "ticks": int(rows[-1]["tick"]) if rows else 0,
        "peak_pop": max(pops),
        "final_pop": pops[-1] if pops else 0,
        "extinction_tick": extinction,
    }


def main():
    parser = argparse.ArgumentParser(description="Compare Aether-1 metrics files")
    parser.add_argument("files", nargs="+", help="Metrics CSV files to compare")
    parser.add_argument("--metric", default="population", help="Metric to compare")
    args = parser.parse_args()

    if len(args.files) < 1:
        print("Provide at least one file.")
        sys.exit(1)

    results = []
    for path in args.files:
        try:
            rows = load_metrics(path)
            stats = analyze(rows, args.metric)
            results.append((path, stats))
        except FileNotFoundError:
            print(f"File not found: {path}")
            sys.exit(1)

    # Print comparison table
    print(f"\nComparison of '{args.metric}' across {len(results)} runs:")
    print("=" * 80)

    # Header
    labels = [f"File {i + 1}" for i in range(len(results))]
    header = f"{'Stat':<20}" + "".join(f" | {label:<15}" for label in labels)
    print(header)
    print("-" * 80)

    # Rows
    metrics = [
        ("Final", "final"),
        ("Max", "max"),
        ("Min", "min"),
        ("Average", "avg"),
        ("Ticks", "ticks"),
        ("Peak Population", "peak_pop"),
        ("Final Population", "final_pop"),
        ("Extinction Tick", "extinction_tick"),
    ]

    for label, key in metrics:
        row = f"{label:<20}"
        for _, stats in results:
            val = stats.get(key)
            if val is None:
                row += f" | {'survived':<15}"
            elif isinstance(val, float):
                row += f" | {val:<15.2f}"
            else:
                row += f" | {val:<15}"
        print(row)

    print("=" * 80)

    # File paths
    print("\nFiles:")
    for i, (path, _) in enumerate(results):
        print(f"  File {i + 1}: {path}")


if __name__ == "__main__":
    main()
