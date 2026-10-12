#!/usr/bin/env python3
"""Daily means from sorted daily rows, forward-filling with a staleness cap.

Input : CSV (station_id, fuel, day, price) sorted by station_id, fuel, day.
Output: national daily means, plus the same restricted to a station subset.
"""
import csv, sys
from collections import defaultdict
from datetime import date, timedelta

STALE_DAYS = 30          # a station stops counting 30 days after its last update

def accumulate(rows, end_day, tot, cnt):
    """rows: [(day, price)] for one station+fuel, ascending."""
    d, last = rows[0][0], rows[0][1]
    idx, stop = 0, min(rows[-1][0] + timedelta(days=STALE_DAYS), end_day)
    while d <= stop:
        while idx < len(rows) and rows[idx][0] <= d:
            last = rows[idx][1]; idx += 1
        tot[d] += last; cnt[d] += 1
        d += timedelta(days=1)

def run(in_csv, subset_ids, nat_out, loc_out):
    nat_t = defaultdict(lambda: defaultdict(float)); nat_c = defaultdict(lambda: defaultdict(int))
    loc_t = defaultdict(lambda: defaultdict(float)); loc_c = defaultdict(lambda: defaultdict(int))
    # The archives are downloaded fresh at run time, so the series runs to today;
    # forward-fill keeps the current (partial) day well-defined.
    end_day = date.today()
    obs_max = None           # last day the archive actually observed
    cur, buf = None, []
    def flush():
        if not buf: return
        sid, fuel = cur
        accumulate(buf, end_day, nat_t[fuel], nat_c[fuel])
        if sid in subset_ids:
            accumulate(buf, end_day, loc_t[fuel], loc_c[fuel])
    with open(in_csv) as f:
        for sid, fuel, day, price in csv.reader(f):
            k = (sid, fuel)
            if k != cur:
                flush(); cur, buf = k, []
            d = date.fromisoformat(day)
            if obs_max is None or d > obs_max:
                obs_max = d
            buf.append((d, float(price)))
    flush()
    # The series is forward-filled to today, but the archive is republished once
    # a day and its last day is partial; record where the observations end.
    with open("archive_end.txt", "w") as f:
        f.write(obs_max.isoformat() + "\n")
    print(f"archive observations end {obs_max}, series filled to {end_day}", file=sys.stderr)
    for path, T, C in ((nat_out, nat_t, nat_c), (loc_out, loc_t, loc_c)):
        with open(path, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["day","fuel","mean_price","n_stations"])
            for fuel in sorted(T):
                for d in sorted(T[fuel]):
                    if C[fuel][d] >= 3:
                        w.writerow([d.isoformat(), fuel, round(T[fuel][d]/C[fuel][d], 4), C[fuel][d]])
        print(f"wrote {path}", file=sys.stderr)

if __name__ == "__main__":
    ids = set(r["id"] for r in csv.DictReader(open(sys.argv[2])))
    print(f"subset: {len(ids)} stations", file=sys.stderr)
    run(sys.argv[1], ids, sys.argv[3], sys.argv[4])
