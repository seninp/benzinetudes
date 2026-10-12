#!/usr/bin/env python3
"""Daily local means split by brand group, to separate the capped from the free.

"Are prices rising, stuck, or falling?" has two answers within 15 km, and the
overall mean hides both. The Total-group stations sit on the 2,250 EUR ceiling
and cannot follow the market up; every other brand can. Averaging them together
produces a line that rises more slowly than the free stations and faster than
the capped ones, and describes neither.

Same carry-forward rule as agg.py — last posted price stands, station drops out
30 days after its final update — restricted to the stations within 15 km.
"""
import csv, sys
from collections import defaultdict
from datetime import date
from common import carry_forward
from config import MIN_STATIONS, STALE_DAYS, START, TOTAL_GROUP

FUELS = ("Gazole", "E10", "SP98")


def run(brands_csv, archive_end_path, out_csv, *px_paths):
    end_day = date.fromisoformat(open(archive_end_path).read().strip())
    group = {}
    for r in csv.DictReader(open(brands_csv)):
        group[r["id"]] = "total" if r["brand"] in TOTAL_GROUP else "other"

    hist = defaultdict(dict)
    for p in px_paths:
        for r in csv.DictReader(open(p)):
            if r["fuel"] in FUELS:
                hist[(r["station_id"], r["fuel"])][date.fromisoformat(r["ts"][:10])] = float(r["price"])

    # fuel -> day -> group -> [total, count, max]
    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [0.0, 0, 0.0])))
    for (sid, fuel), d in hist.items():
        # A station with no OSM brand match counts as "other": it is certainly not
        # Total-group, since all 21 Total sites here matched.
        g = group.get(sid, "other")
        for day, last in carry_forward(sorted(d.items()), end_day, STALE_DAYS):
            if day >= START:
                c = agg[fuel][day][g]
                c[0] += last
                c[1] += 1
                c[2] = max(c[2], last)

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        # The maxima are not decoration. They are the evidence that the 2,250 EUR line
        # is a cap on these brands and not a price they all chose: the Total-group
        # maximum never exceeds it, while the other brands' maximum runs well above.
        w.writerow(["day", "fuel", "total_mean", "total_n", "total_max",
                    "other_mean", "other_n", "other_max"])
        for fuel in FUELS:
            for day in sorted(agg[fuel]):
                t, o = agg[fuel][day]["total"], agg[fuel][day]["other"]
                w.writerow([day.isoformat(), fuel,
                            round(t[0] / t[1], 4) if t[1] >= MIN_STATIONS else "", t[1], round(t[2], 4),
                            round(o[0] / o[1], 4) if o[1] >= MIN_STATIONS else "", o[1], round(o[2], 4)])
    last = max(agg["Gazole"])
    t, o = agg["Gazole"][last]["total"], agg["Gazole"][last]["other"]
    mean = lambda c: f"{c[0] / c[1]:.3f}" if c[1] else "-"
    print(f"{out_csv}: through {last}; diesel {t[1]} Total-group stations "
          f"at {mean(t)} against {o[1]} others at {mean(o)}", file=sys.stderr)


if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3], *sys.argv[4:])
