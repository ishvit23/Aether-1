"""Metric comparison utility for Aether-1 runs."""

import argparse
import pandas as pd
import sys

def main():
    parser = argparse.ArgumentParser(description="Compare two Aether-1 metrics files")
    parser.add_argument("file1", help="First metrics CSV")
    parser.add_argument("file2", help="Second metrics CSV")
    parser.add_argument("--metric", default="population", help="Metric to compare")
    args = parser.parse_args()

    try:
        df1 = pd.read_csv(args.file1)
        df2 = pd.read_csv(args.file2)
    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)

    if args.metric not in df1.columns:
        print(f"Error: Metric '{args.metric}' not found in {args.file1}")
        sys.exit(1)

    m1_final = df1[args.metric].iloc[-1]
    m2_final = df2[args.metric].iloc[-1]
    
    m1_max = df1[args.metric].max()
    m2_max = df2[args.metric].max()

    print(f"Comparison of '{args.metric}':")
    print(f"{'Metric':<10} | {'File 1':<15} | {'File 2':<15} | {'Diff':<10}")
    print("-" * 60)
    print(f"{'Final':<10} | {m1_final:<15.2f} | {m2_final:<15.2f} | {m2_final-m1_final:<10.2f}")
    print(f"{'Max':<10} | {m1_max:<15.2f} | {m2_max:<15.2f} | {m2_max-m1_max:<10.2f}")

    # Check for duration
    t1 = df1['tick'].max()
    t2 = df2['tick'].max()
    print(f"\nSimulation Duration (Ticks):")
    print(f"File 1: {t1} | File 2: {t2} | Diff: {t2-t1}")

if __name__ == "__main__":
    main()
