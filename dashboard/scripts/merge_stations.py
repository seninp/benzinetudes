#!/usr/bin/env python3
"""Merge per-file station lists into one, later files winning on metadata.

Usage: merge_stations.py <out.csv> <st_a.csv> [st_b.csv ...]   (oldest first)
"""
import csv, sys

def main(out_csv, *paths):
    rows = {}
    for p in paths:
        for r in csv.DictReader(open(p)):
            rows[r["id"]] = r
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(next(iter(rows.values())).keys()))
        w.writeheader()
        for r in sorted(rows.values(), key=lambda r: float(r["dist_km"])):
            w.writerow(r)
    print(f"{out_csv}: {len(rows)} stations", file=sys.stderr)

if __name__ == "__main__":
    main(sys.argv[1], *sys.argv[2:])
