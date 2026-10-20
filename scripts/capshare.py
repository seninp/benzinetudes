#!/usr/bin/env python3
"""Daily share of stations posting exactly a ceiling price, national and per city.

Reads the sorted daily rows produced by dump_daily.py; one pass for all cities.
Writes data/<slug>/capshare.csv with the national columns repeated in each file.
Runs after agg.py and stops on its data/archive_end.txt, the last observed day.
"""
import csv, sys
from collections import defaultdict
from datetime import date
from config import CITIES, CEILING, STALE_DAYS
from common import carry_forward, read_daily

END = date.fromisoformat(open("data/archive_end.txt").read().strip())

def main(daily_csv):
    subsets = []
    for c in CITIES:
        ids = set(r["id"] for r in csv.DictReader(open(f"data/{c['slug']}/stations.csv")))
        subsets.append((c["slug"], ids))
    nat = defaultdict(lambda: [0, 0, 0])
    loc = {slug: defaultdict(lambda: [0, 0, 0]) for slug, _ in subsets}

    for sid, fuel, rows in read_daily(daily_csv):
        if fuel not in CEILING:
            continue
        cap = CEILING[fuel]
        tgts = [nat] + [loc[slug] for slug, ids in subsets if sid in ids]
        for d, last in carry_forward(rows, END, STALE_DAYS):
            for tgt in tgts:
                cell = tgt[(fuel, d)]
                cell[0] += 1
                if abs(last - cap) < 1e-9:
                    cell[1] += 1
                elif last < cap:
                    cell[2] += 1

    for slug, _ in subsets:
        path = f"data/{slug}/capshare.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["day", "fuel", "ceiling",
                        "nat_n", "nat_cap", "nat_below", "loc_n", "loc_cap", "loc_below"])
            for (fuel, d) in sorted(nat, key=lambda k: (k[1], k[0])):
                n = nat[(fuel, d)]
                l = loc[slug].get((fuel, d), [0, 0, 0])
                w.writerow([d.isoformat(), fuel, CEILING[fuel]] + n + l)
        print(f"wrote {path}", file=sys.stderr)

if __name__ == "__main__":
    main(sys.argv[1])
