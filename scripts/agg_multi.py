#!/usr/bin/env python3
"""Daily means from sorted daily rows, forward-filled with a staleness cap.

Input : daily_all.csv (station_id, fuel, day, price) sorted by station, fuel, day.
Output: data/nat_daily.csv plus data/<slug>/loc_daily.csv per city, one pass.
The archives are downloaded fresh at run time, so the series runs to today.
"""
import csv, sys
from collections import defaultdict
from datetime import date, timedelta
from cities import CITIES, STALE_DAYS

def accumulate(rows, end_day, tot, cnt):
    d, last = rows[0][0], rows[0][1]
    idx, stop = 0, min(rows[-1][0] + timedelta(days=STALE_DAYS), end_day)
    while d <= stop:
        while idx < len(rows) and rows[idx][0] <= d:
            last = rows[idx][1]; idx += 1
        tot[d] += last; cnt[d] += 1
        d += timedelta(days=1)

def main(daily_csv):
    subsets = []
    for c in CITIES:
        ids = set(r["id"] for r in csv.DictReader(open(f"data/{c['slug']}/stations.csv")))
        subsets.append((c["slug"], ids))
    sinks = {"nat": (defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(int)))}
    for slug, _ in subsets:
        sinks[slug] = (defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(int)))
    end_day = date.today()

    cur, buf = None, []
    def flush():
        if not buf:
            return
        sid, fuel = cur
        accumulate(buf, end_day, sinks["nat"][0][fuel], sinks["nat"][1][fuel])
        for slug, ids in subsets:
            if sid in ids:
                accumulate(buf, end_day, sinks[slug][0][fuel], sinks[slug][1][fuel])
    with open(daily_csv) as f:
        for sid, fuel, day, price in csv.reader(f):
            k = (sid, fuel)
            if k != cur:
                flush(); cur, buf = k, []
            buf.append((date.fromisoformat(day), float(price)))
    flush()

    for slug, (T, C) in sinks.items():
        path = "data/nat_daily.csv" if slug == "nat" else f"data/{slug}/loc_daily.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["day", "fuel", "mean_price", "n_stations"])
            for fuel in sorted(T):
                for d in sorted(T[fuel]):
                    if C[fuel][d] >= 3:
                        w.writerow([d.isoformat(), fuel, round(T[fuel][d] / C[fuel][d], 4), C[fuel][d]])
        print(f"wrote {path}", file=sys.stderr)

if __name__ == "__main__":
    main(sys.argv[1])
