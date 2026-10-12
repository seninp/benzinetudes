#!/usr/bin/env python3
"""Daily share of stations posting exactly a ceiling price, nationally and locally.

Two ceilings are visible in the data: diesel at 2.250 EUR and petrol at 1.990.
Reads the sorted daily rows produced by dump_daily.py.
"""
import csv, sys
from collections import defaultdict
from datetime import date, timedelta

STALE = 30
END = date.today()   # archives are downloaded fresh at run time
CEILING = {"Gazole": 2.250, "E10": 1.990, "SP98": 1.990}

def main(daily_csv, subset_csv, out_csv):
    sub = set(r["id"] for r in csv.DictReader(open(subset_csv)))
    # (fuel, day) -> [n, at_ceiling, below]  for nation and local subset
    nat = defaultdict(lambda: [0, 0, 0])
    loc = defaultdict(lambda: [0, 0, 0])

    def flush(key, rows):
        if not rows:
            return
        sid, fuel = key
        if fuel not in CEILING:
            return
        cap = CEILING[fuel]
        d, last, i = rows[0][0], rows[0][1], 0
        stop = min(rows[-1][0] + timedelta(days=STALE), END)
        while d <= stop:
            while i < len(rows) and rows[i][0] <= d:
                last = rows[i][1]; i += 1
            for tgt in (nat,) + ((loc,) if sid in sub else ()):
                c = tgt[(fuel, d)]
                c[0] += 1
                if abs(last - cap) < 1e-9:
                    c[1] += 1
                elif last < cap:
                    c[2] += 1
            d += timedelta(days=1)

    cur, buf = None, []
    for sid, fuel, day, price in csv.reader(open(daily_csv)):
        k = (sid, fuel)
        if k != cur:
            if cur:
                flush(cur, buf)
            cur, buf = k, []
        buf.append((date.fromisoformat(day), float(price)))
    if cur:
        flush(cur, buf)

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
