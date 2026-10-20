#!/usr/bin/env python3
"""Daily means from sorted daily rows, forward-filled with a staleness cap.

Input : daily_all.csv (station_id, fuel, day, price) sorted by station, fuel, day.
Output: data/nat_daily.csv plus data/<slug>/loc_daily.csv per city, one pass,
and data/archive_end.txt, the last day the archive observed. Every series stops
there: the days up to the build were once written as carried-forward prices,
and half the reports' figures came to be measured on a day nobody observed.
"""
import csv, sys
from collections import defaultdict
from datetime import date
from config import CITIES, MIN_STATIONS, STALE_DAYS
from common import carry_forward, read_daily

def main(daily_csv):
    subsets = []
    for c in CITIES:
        ids = set(r["id"] for r in csv.DictReader(open(f"data/{c['slug']}/stations.csv")))
        subsets.append((c["slug"], ids))
    sinks = {"nat": (defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(int)))}
    for slug, _ in subsets:
        sinks[slug] = (defaultdict(lambda: defaultdict(float)), defaultdict(lambda: defaultdict(int)))
    end_day = date.today()
    obs_max = None          # last day the archive actually observed

    for sid, fuel, rows in read_daily(daily_csv):
        if obs_max is None or rows[-1][0] > obs_max:
            obs_max = rows[-1][0]
        tgts = [sinks["nat"]] + [sinks[slug] for slug, ids in subsets if sid in ids]
        for d, price in carry_forward(rows, end_day, STALE_DAYS):
            for T, C in tgts:
                T[fuel][d] += price; C[fuel][d] += 1

    # The archive stops before the build day; record where the observations end.
    with open("data/archive_end.txt", "w") as f:
        f.write(obs_max.isoformat() + "\n")
    print(f"archive observations end {obs_max}; series written to that day", file=sys.stderr)

    for slug, (T, C) in sinks.items():
        path = "data/nat_daily.csv" if slug == "nat" else f"data/{slug}/loc_daily.csv"
        with open(path, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["day", "fuel", "mean_price", "n_stations"])
            for fuel in sorted(T):
                for d in sorted(T[fuel]):
                    if d <= obs_max and C[fuel][d] >= MIN_STATIONS:
                        w.writerow([d.isoformat(), fuel, round(T[fuel][d] / C[fuel][d], 4), C[fuel][d]])
        print(f"wrote {path}", file=sys.stderr)

if __name__ == "__main__":
    main(sys.argv[1])
