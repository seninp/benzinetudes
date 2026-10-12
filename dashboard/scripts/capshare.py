#!/usr/bin/env python3
"""Daily share of stations posting exactly a ceiling price, nationally and locally.

Two ceilings are visible in the data: diesel at 2.250 EUR and petrol at 1.990.
Reads the sorted daily rows produced by dump_daily.py.
"""
import csv, sys
from collections import defaultdict
from datetime import date
from common import carry_forward, read_daily
from config import DIESEL_CAP, PETROL_CAP, STALE_DAYS

END = date.today()   # archives are downloaded fresh at run time
CEILING = {"Gazole": DIESEL_CAP, "E10": PETROL_CAP, "SP98": PETROL_CAP}

def main(daily_csv, subset_csv, out_csv):
    sub = set(r["id"] for r in csv.DictReader(open(subset_csv)))
    # (fuel, day) -> [n, at_ceiling, below]  for nation and local subset
    nat = defaultdict(lambda: [0, 0, 0])
    loc = defaultdict(lambda: [0, 0, 0])
    for sid, fuel, rows in read_daily(daily_csv):
        if fuel not in CEILING:
            continue
        cap = CEILING[fuel]
        tgts = (nat,) + ((loc,) if sid in sub else ())
        for d, last in carry_forward(rows, END, STALE_DAYS):
            for tgt in tgts:
                c = tgt[(fuel, d)]
                c[0] += 1
                if abs(last - cap) < 1e-9:
                    c[1] += 1
                elif last < cap:
                    c[2] += 1

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["day","fuel","ceiling","nat_n","nat_cap","nat_below","loc_n","loc_cap","loc_below"])
        for (fuel, d) in sorted(nat, key=lambda k: (k[1], k[0])):
            n = nat[(fuel, d)]
            l = loc.get((fuel, d), [0, 0, 0])
            w.writerow([d.isoformat(), fuel, CEILING[fuel]] + n + l)
    print(f"wrote {out_csv}: {len(nat)} fuel/day cells", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:4])
