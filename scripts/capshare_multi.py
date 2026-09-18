#!/usr/bin/env python3
"""Daily share of stations posting exactly a ceiling price, national and per city.

Reads the sorted daily rows produced by dump_daily.py; one pass for all cities.
Writes data/<slug>/capshare.csv with the national columns repeated in each file.
"""
import csv, sys
from collections import defaultdict
from datetime import date, timedelta
from cities import CITIES, CEILING, STALE_DAYS

END = date.today()   # archives are downloaded fresh at run time

def main(daily_csv):
    subsets = []
    for c in CITIES:
        ids = set(r["id"] for r in csv.DictReader(open(f"data/{c['slug']}/stations.csv")))
        subsets.append((c["slug"], ids))
    nat = defaultdict(lambda: [0, 0, 0])
    loc = {slug: defaultdict(lambda: [0, 0, 0]) for slug, _ in subsets}

    def flush(key, rows):
        sid, fuel = key
        if fuel not in CEILING or not rows:
            return
        cap = CEILING[fuel]
        tgts = [nat] + [loc[slug] for slug, ids in subsets if sid in ids]
        d, last, i = rows[0][0], rows[0][1], 0
        stop = min(rows[-1][0] + timedelta(days=STALE_DAYS), END)
        while d <= stop:
            while i < len(rows) and rows[i][0] <= d:
                last = rows[i][1]; i += 1
            for tgt in tgts:
                cell = tgt[(fuel, d)]
                cell[0] += 1
                if abs(last - cap) < 1e-9:
                    cell[1] += 1
                elif last < cap:
                    cell[2] += 1
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
