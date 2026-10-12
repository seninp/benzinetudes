#!/usr/bin/env python3
"""Day-of-week effect in local pump prices.

Two questions, two measures:

1. "Which weekday is cheapest to fill?" — compare a day against the same
   station's own price in the same week, never against other stations. The naive
   measure, a mean price by weekday, mixes in *who reported that day*: reporting
   has its own weekly rhythm, so a weekday crowded with cheap supermarkets looks
   cheap even when no price moved. Deviation from the station's own weekly mean
   removes both the station's level and any composition effect, leaving only the
   within-week shape.

2. "When do prices actually change?" — count posted updates by the weekday of
   their timestamp, and the mean signed size of the change. This says when a move
   lands, which is what tells you to fill the day before.

Both are computed over the whole series and over a recent window, because the
2,250 EUR ceiling arrived on 2026-04-08 and flattens everything it touches: a
station pinned at the cap contributes seven zero deviations and drags the
weekday means toward nothing. The recent window is the one to read, and the
`moving` scope reports the same figure over station-weeks whose price moved at
all, which is the effect a driver who shops around actually sees.

Measure 1 is also split by the week's own direction (`rose`, `fell`, `flat`),
and that split is the only honest way to read it. Pooled over every week, Monday
comes out cheapest and Sunday dearest -- but weeks when the price rose tilt one
way and weeks when it fell tilt exactly the opposite way, by almost the same
amount. The pooled tilt is not a weekly habit; it is the net excess of rising
weeks over falling ones in a period when diesel rose 72 centimes. Publishing the
pooled bars alone would tell a driver to fill on Monday because 2026 was an
expensive year, which is a forecast wearing a habit's clothes.
"""
import csv, sys
from collections import defaultdict
from datetime import date, timedelta

STALE_DAYS = 30          # mirrors agg.py: a station stops counting 30 days after its last update
START = date(2025, 1, 15)
RECENT_DAYS = 180
FUELS = ("Gazole", "E10", "SP98")
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SCOPES = ("all", "recent", "recent_moving", "rose", "fell", "flat")


def load(paths):
    """(station, fuel) -> [(day, price)] ascending, one row per day posted."""
    hist = defaultdict(dict)
    for p in paths:
        for r in csv.DictReader(open(p)):
            if r["fuel"] not in FUELS:
                continue
            d = date.fromisoformat(r["ts"][:10])
            # several updates in a day: the last one is the price that stands
            hist[(r["station_id"], r["fuel"])][d] = float(r["price"])
    return {k: sorted(v.items()) for k, v in hist.items()}


def daily(rows, end_day):
    """Carry each posted price forward, stopping STALE_DAYS after the last post."""
    out, idx, last = {}, 0, rows[0][1]
    d, stop = rows[0][0], min(rows[-1][0] + timedelta(days=STALE_DAYS), end_day)
    while d <= stop:
        while idx < len(rows) and rows[idx][0] <= d:
            last = rows[idx][1]
            idx += 1
        out[d] = last
        d += timedelta(days=1)
    return out


def run(px_paths, archive_end_path, dev_out, upd_out):
    end_day = date.fromisoformat(open(archive_end_path).read().strip())
    recent_from = end_day - timedelta(days=RECENT_DAYS)
    hist = load(px_paths)

    # --- measure 1: deviation from the station's own weekly mean -------------
    # scope -> fuel -> dow -> [deviations in euros], and the same grouped by
    # calendar week. Station-weeks are not independent observations: every
    # station in the area sees the same national move in the same week, so an
    # error bar over station-days would be far too tight. The reported error
    # clusters by calendar week, which is where that shared shock lives.
    dev = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    devw = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    weeks_seen = defaultdict(lambda: defaultdict(int))
    for (sid, fuel), rows in hist.items():
        ser = daily(rows, end_day)
        byweek = defaultdict(dict)
        for d, p in ser.items():
            if d >= START:
                byweek[d.isocalendar()[:2]][d.weekday()] = (d, p)
        for wk, days in byweek.items():
            if len(days) < 7:        # partial weeks would bias the mean toward the days present
                continue
            vals = [p for _, p in days.values()]
            wmean = sum(vals) / 7
            moved = max(vals) - min(vals) > 1e-9
            # Net move across the week, Monday's price against Sunday's. This is
            # what separates a weekly habit from the month's trend leaking in.
            net = days[6][1] - days[0][1]
            scopes = ["all", "rose" if net > 1e-9 else "fell" if net < -1e-9 else "flat"]
            if min(d for d, _ in days.values()) >= recent_from:
                scopes.append("recent")
                if moved:
                    scopes.append("recent_moving")
            for sc in scopes:
                weeks_seen[sc][fuel] += 1
                for dow, (_, p) in days.items():
                    dev[sc][fuel][dow].append(p - wmean)
                    devw[sc][fuel][dow][wk].append(p - wmean)

    def se_by_week(buckets):
        """Standard error of the mean deviation, clustering by calendar week."""
        wk_means = [sum(v) / len(v) for v in buckets.values()]
        n = len(wk_means)
        if n < 2:
            return None, n
        m = sum(wk_means) / n
        var = sum((x - m) ** 2 for x in wk_means) / (n - 1)
        return (var / n) ** 0.5, n

    with open(dev_out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scope", "fuel", "dow", "dow_name", "n_station_days",
                    "mean_dev_c", "se_c", "n_weeks"])
        for sc in SCOPES:
            for fuel in FUELS:
                for dow in range(7):
                    v = dev[sc][fuel][dow]
                    if not v:
                        continue
                    se, nw = se_by_week(devw[sc][fuel][dow])
                    w.writerow([sc, fuel, dow, DOW[dow], len(v),
                                round(100 * sum(v) / len(v), 4),
                                round(100 * se, 4) if se is not None else "", nw])
    for sc in ("all", "recent", "recent_moving"):
        print(f"{dev_out}: {sc} — " + ", ".join(
            f"{fuel} {weeks_seen[sc][fuel]} station-weeks" for fuel in FUELS), file=sys.stderr)

    # --- measure 2: when updates land, and which way -------------------------
    upd = defaultdict(lambda: defaultdict(lambda: [0, 0.0, 0, 0]))   # n, sum_delta, n_up, n_down
    updw = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for (sid, fuel), rows in hist.items():
        prev = None
        for d, p in rows:
            if d >= START and prev is not None:
                for sc in (["all"] + (["recent"] if d >= recent_from else [])):
                    c = upd[sc][(fuel, d.weekday())]
                    c[0] += 1
                    c[1] += p - prev
                    if p > prev + 1e-9:
                        c[2] += 1
                    elif p < prev - 1e-9:
                        c[3] += 1
                    updw[sc][(fuel, d.weekday())][d.isocalendar()[:2]].append(p - prev)
            prev = p
    with open(upd_out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scope", "fuel", "dow", "dow_name", "n_updates",
                    "mean_change_c", "se_c", "n_weeks", "n_up", "n_down"])
        for sc in ("all", "recent"):
            for fuel in FUELS:
                for dow in range(7):
                    n, s, up, dn = upd[sc][(fuel, dow)]
                    if not n:
                        continue
                    se, nw = se_by_week(updw[sc][(fuel, dow)])
                    w.writerow([sc, fuel, dow, DOW[dow], n,
                                round(100 * s / n, 4),
                                round(100 * se, 4) if se is not None else "", nw, up, dn])
    print(f"{upd_out}: {sum(c[0] for c in upd['all'].values())} price changes "
          f"({sum(c[0] for c in upd['recent'].values())} in the last {RECENT_DAYS} days)",
          file=sys.stderr)


if __name__ == "__main__":
    run(sys.argv[1:-3], sys.argv[-3], sys.argv[-2], sys.argv[-1])
