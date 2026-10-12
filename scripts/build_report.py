#!/usr/bin/env python3
"""Compute everything the report shows, from the CSVs in data/, into data/report_data.json.

Run from the repository root; render_html.py then embeds the JSON in the template.
"""
import csv, json, math, re, statistics
from collections import defaultdict
from datetime import date, timedelta
from config import (CAP_DAY, CENTER_LAT, CENTER_LON, CENTER_NAME, DIESEL_CAP,
                    DRY_WINDOW, PETROL_CAP, RADIUS_KM, START, TOTAL_GROUP)

# Last day present in the aggregated series (agg.py runs it through fetch day).
END = max(date.fromisoformat(r["day"]) for r in csv.DictReader(open("data/nat_daily.csv")))
# Last day the archive actually observed. Every measurement — trend windows, the dry
# count, any comparison — must end here, never on END: the days between are
# forward-filled, so a carried-forward price would count as a reading.
OBS_END = date.fromisoformat(open("data/archive_end.txt").read().strip())
FUELS = ["Gazole", "E10", "SP98", "SP95", "E85", "GPLc"]
LABEL = {"Gazole": "Diesel (Gazole)", "E10": "Petrol E10 (SP95-E10)",
         "SP98": "Petrol SP98", "SP95": "Petrol SP95", "E85": "Superethanol E85",
         "GPLc": "LPG (GPLc)"}

def load(path):
    s = defaultdict(dict); n = defaultdict(dict)
    for r in csv.DictReader(open(path)):
        d = date.fromisoformat(r["day"])
        if START <= d <= END:
            s[r["fuel"]][d] = float(r["mean_price"])
            n[r["fuel"]][d] = int(r["n_stations"])
    return s, n

loc, loc_n = load("data/loc_daily.csv")
nat, nat_n = load("data/nat_daily.csv")

days = []
d = START
while d <= END:
    days.append(d); d += timedelta(days=1)

def series(src, fuel):
    return [round(src[fuel][d], 4) if d in src[fuel] else None for d in days]

BRANDS = {r["id"]: r for r in csv.DictReader(open("data/brands.csv"))}
RIVALS = ("Intermarché", "Super U")

# Open stock outages from the annual archive (the instant feed carries none).
# A flag older than DRY_WINDOW days means "stopped selling that fuel", not "dry".
RUPTURES = defaultdict(dict)
for r in csv.DictReader(open("data/ruptures.csv")):
    RUPTURES[r["id"]][r["fuel"]] = r["debut"]

# Every rupture interval, open or closed, to reconstruct the dry count on any
# past day under the table's own rule: an outage counts while it is open, and
# for at most DRY_WINDOW days after it began.
INTERVALS = [(r["id"], r["fuel"], r["debut"], r["fin"])
             for r in csv.DictReader(open("data/rupture_hist.csv"))
             if r["fuel"] in FUELS]

def bearing(lat, lon):
    """8-point compass bearing from the centre to a station."""
    p1, p2 = math.radians(CENTER_LAT), math.radians(lat)
    dl = math.radians(lon - CENTER_LON)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    deg = (math.degrees(math.atan2(y, x)) + 360) % 360
    return ["N","NE","E","SE","S","SW","W","NW"][int((deg + 22.5) % 360 // 45)]

# str.title() capitalises after every hyphen, so the feed's LABARTHE-SUR-LEZE came out
# "Labarthe-Sur-Lèze" and SAINT-ORENS-DE-GAMEVILLE as "Saint-Orens-De-Gameville". French
# keeps these particles lower case. Only the casing is corrected here: the feed also
# spells some towns two ways ("Labege" and "Labège", "Portet Sur Garonne" and
# "Portet-Sur-Garonne"), and guessing which is meant is not this script's business.
PARTICLES = {"sur", "sous", "de", "du", "des", "le", "la", "les", "en", "lès", "et"}

def frtown(s):
    # split keeping the separators, so "Saint-Orens-De-Gameville" rebuilds exactly
    parts = re.split(r"([-\s])", s.title())
    # never the first word: "Le Vernet" keeps its article
    return parts[0] + "".join(p.lower() if p.lower() in PARTICLES else p
                              for p in parts[1:])

stations = []
for r in csv.DictReader(open("data/stations_now.csv")):
    # Stations posting nothing today stay in; the table shows them as silent.
    prices = {f: (float(r[f]) if r[f] else None) for f in FUELS}
    b = BRANDS.get(r["id"], {})
    stations.append({"id": r["id"], "ville": frtown(r["ville"]),
                     "adresse": r["adresse"], "cp": r["cp"],
                     "dist": float(r["dist_km"]), "prices": prices,
                     "maj": r["maj"][:16],
                     "brand": b.get("brand", ""),
                     "brand_shared": b.get("shared", "") == "1",
                     "dir": bearing(float(r["lat"]), float(r["lon"]))})
stations.sort(key=lambda s: s["dist"])

snap = max((st["maj"] for st in stations if st["maj"]), default="")[:10]
dry_cutoff = (date.fromisoformat(snap) - timedelta(days=DRY_WINDOW)).isoformat()
for st in stations:
    st["dry"] = {f: d for f, d in RUPTURES.get(st["id"], {}).items()
                 if f in FUELS and d >= dry_cutoff}

# monthly means for the table view
monthly = defaultdict(dict)
for fuel in FUELS:
    agg = defaultdict(lambda: [0.0, 0, 0.0, 0])
    for d in days:
        if d in loc[fuel]:
            k = f"{d.year}-{d.month:02d}"
            agg[k][0] += loc[fuel][d]; agg[k][1] += 1
        if d in nat[fuel]:
            k = f"{d.year}-{d.month:02d}"
            agg[k][2] += nat[fuel][d]; agg[k][3] += 1
    for k, (ls, lc, ns, nc) in agg.items():
        monthly[k][fuel] = [round(ls/lc, 3) if lc else None,
                            round(ns/nc, 3) if nc else None]

cap_days, cap_nat, cap_loc = [], [], []
# capshare.csv carries one row per day AND fuel (E10, Gazole, SP98, in that order).
# The diesel ceiling series must take Gazole rows only: without the filter these lists
# ran 3x the length of `days`, so the chart plotted three interleaved fuels against a
# day axis and the findings quoted the last row of the file — SP98 — as the diesel share.
cap_by_day = {}
for r in csv.DictReader(open("data/capshare.csv")):
    d = date.fromisoformat(r["day"])
    if r["fuel"] != "Gazole" or not (START <= d <= END):
        continue
    cap_by_day[d] = r
for d in days:
    r = cap_by_day.get(d)
    if r is None:
        cap_days.append(d)
        cap_nat.append(None)
        cap_loc.append(None)
        continue
    cap_days.append(d)
    cap_nat.append(round(100 * int(r["nat_cap"]) / int(r["nat_n"]), 2) if int(r["nat_n"]) else None)
    cap_loc.append(round(100 * int(r["loc_cap"]) / int(r["loc_n"]), 2) if int(r["loc_n"]) else None)

CAP = DIESEL_CAP
# "At the ceiling" is only a third of the picture, and on its own it misleads: 16%
# of stations post diesel at exactly 2,250 EUR, but three quarters post *above* it.
# Without that third number a reader takes the cap for a national maximum, which it
# plainly is not. Every share here therefore carries at / below / above.
ceilings = {r["fuel"]: {"ceiling": float(r["ceiling"]), "n": int(r["n"]),
                        "at": int(r["at_ceiling"]), "below": int(r["below"]),
                        "above": int(r["n"]) - int(r["at_ceiling"]) - int(r["below"]),
                        "lowest": float(r["lowest"]),
                        "pct_at": round(100 * int(r["at_ceiling"]) / int(r["n"]), 1),
                        "pct_below": round(100 * int(r["below"]) / int(r["n"]), 1),
                        "pct_above": round(100 * (int(r["n"]) - int(r["at_ceiling"])
                                                  - int(r["below"])) / int(r["n"]), 1)}
             for r in csv.DictReader(open("data/ceilings_now.csv"))}


def shares(n, a, b):
    """at / below / above as percentages of n."""
    return {"n": n, "at": round(100 * a / n, 1), "below": round(100 * b / n, 1),
            "above": round(100 * (n - a - b) / n, 1)} if n else None


arch, cap_hist = {}, {}
for r in csv.DictReader(open("data/capshare.csv")):
    d = date.fromisoformat(r["day"])
    nn, na, nb = int(r["nat_n"]), int(r["nat_cap"]), int(r["nat_below"])
    ln, la, lb = int(r["loc_n"]), int(r["loc_cap"]), int(r["loc_below"])
    if r["fuel"] == "Gazole":
        cap_hist[d] = {"nat": shares(nn, na, nb), "loc": shares(ln, la, lb)}
    if d == END and nn:
        arch[r["fuel"]] = {"nat": shares(nn, na, nb), "loc": shares(ln, la, lb)}
for f, v in arch.items():
    if f in ceilings:
        ceilings[f]["archive_pct_at"] = v["nat"]["at"]
        ceilings[f]["archive_pct_loc"] = v["loc"]["at"] if v["loc"] else None
        ceilings[f]["archive"] = v

# What actually happened on the day the 2,250 cluster formed, stated in all three
# shares. The tempting reading -- "cheap stations raised their price to the cap" --
# is wrong, and the numbers say why: the share *above* 2,250 did not move that day
# (73,8% to 74,8%), so nothing crossed the line. The capped stations simply rose
# into their own cap and stopped, which is why they moved out of "below" and into
# "at". The local Total-group series is the direct evidence: their diesel maximum
# is exactly 2,250 EUR on every day from 7 April on, and when the market fell back
# in April and June they went below the cap again rather than sitting on it.
cap_story = {"day": CAP_DAY.isoformat(),
             "before": cap_hist.get(CAP_DAY - timedelta(days=1)),
             "after": cap_hist.get(CAP_DAY),
             "now": cap_hist.get(END),
             "trough": None}
# The month when the cap bound on almost nobody, which is the cleanest proof that it
# is a cap and not a floor: in June diesel fell and the 2,250 cluster emptied out.
if cap_hist:
    tr = min((d for d in cap_hist if d >= CAP_DAY and cap_hist[d]["nat"]),
             key=lambda d: cap_hist[d]["nat"]["at"], default=None)
    if tr:
        cap_story["trough"] = {"day": tr.isoformat(), **cap_hist[tr]["nat"]}

by_brand = defaultdict(list)
for st in stations:
    if st["prices"]["Gazole"] is not None:
        by_brand[st["brand"] or "Brand unknown"].append(st["prices"]["Gazole"])
brand_rows = sorted(
    ({"brand": b, "n": len(v), "min": round(min(v), 3),
      "median": round(statistics.median(v), 3), "max": round(max(v), 3),
      "total": b in TOTAL_GROUP, "known": b != "Brand unknown"} for b, v in by_brand.items()),
    key=lambda r: r["median"])
total_st = sorted((st for st in stations if st["brand"] in TOTAL_GROUP),
                  key=lambda st: st["dist"])
rival_st = sorted((st for st in stations if st["brand"] in RIVALS),
                  key=lambda st: st["dist"])

# The outage intervals come from the annual archive, so the series can only run as
# far as the archive observed. Extending it to the snapshot day added one point that
# was a copy of the day before — a flat tail that read as "no new outages today"
# when it meant "no data yet".
dry_days = []
d = START
while d <= OBS_END:
    dry_days.append(d); d += timedelta(days=1)

def dry_series(ids):
    ids, out = set(ids), []
    for d in dry_days:
        iso, floor = d.isoformat(), (d - timedelta(days=DRY_WINDOW)).isoformat()
        out.append(len(set((sid, fuel) for sid, fuel, debut, fin in INTERVALS
                           if sid in ids and floor <= debut <= iso
                           and (not fin or fin > iso))))
    return out

dry_table = dry_series([s["id"] for s in total_st + rival_st])
dry_all = dry_series([s["id"] for s in stations])
# non-Total stations that also sit exactly on the diesel ceiling
cap_others = [{"brand": st["brand"] or "", "ville": st["ville"], "dist": st["dist"]}
              for st in stations
              if st["prices"]["Gazole"] == CAP and st["brand"] not in TOTAL_GROUP]
capped = sorted((s for s in stations if s["prices"]["Gazole"] == CAP), key=lambda s: s["dist"])
# A station can post the ceiling price and still be dry: the price comes from the
# instant feed, the outage flag only from the annual archive. Send readers to the
# nearest one that has not declared its diesel out of stock (v1.4's lesson).
capped_wet = [s for s in capped if "Gazole" not in s["dry"]]
# The reader's own town, used as the "do nothing" baseline everywhere. Nine of the 71
# stations post no price at all today, so `next()` on a generator would abort the whole
# build the first morning the Castanet pump goes quiet. Fall back to the nearest station
# that does post diesel, and let the template say which it used.
in_town = [s for s in stations if s["cp"] == "31320" and s["prices"]["Gazole"]]
castanet = min(in_town or [s for s in stations if s["prices"]["Gazole"]],
               key=lambda s: s["dist"])
castanet_in_town = bool(in_town)

# The worked example in finding 5 names one station and lists the fuels it posts.
# That list was hardcoded as diesel, E85 and LPG and went stale on 27 September,
# when the same station started posting E10 at the ceiling too, so the finding is
# fed from the live snapshot instead. Only the SP98 sale stays fixed: it is a
# dated observation, not a fact about today's feed.
SHORT = {"Gazole": "diesel", "E10": "E10", "SP98": "SP98", "SP95": "SP95",
         "E85": "E85", "GPLc": "LPG"}
EXAMPLE_ID = "31300008"
ex_st = next(s for s in stations if s["id"] == EXAMPLE_ID)


def delta(fuel, back):
    ref = END - timedelta(days=back)
    if fuel in loc and END in loc[fuel] and ref in loc[fuel]:
        return round(loc[fuel][END] - loc[fuel][ref], 3)
    return None

# --- trend ------------------------------------------------------------------
TREND_WIN = 28          # observed days behind OBS_END that set the headline direction
MATERIAL_C = 1.0        # centimes/week a slope must clear to be called a trend at all
TREND_FUELS = ["Gazole", "E10", "SP98"]


def ols_cw(src, fuel, n, end=None):
    """Least-squares slope in centimes per week, with its standard error and R²."""
    end = end or OBS_END
    pts = [(i, src[fuel][end - timedelta(days=n - 1 - i)])
           for i in range(n) if (end - timedelta(days=n - 1 - i)) in src[fuel]]
    if len(pts) < 3:
        return None
    k = len(pts)
    mx = sum(x for x, _ in pts) / k
    my = sum(y for _, y in pts) / k
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    b = sum((x - mx) * (y - my) for x, y in pts) / sxx
    res = [y - (my + b * (x - mx)) for x, y in pts]
    sst = sum((y - my) ** 2 for _, y in pts)
    se = ((sum(r * r for r in res) / (k - 2)) / sxx) ** 0.5
    return {"cw": round(b * 700, 2), "se": round(se * 700, 2),
            "r2": round(1 - sum(r * r for r in res) / sst, 2) if sst else None, "n": k}


def direction(sl):
    """rising / falling / flat, from the slope's 95% interval and a materiality floor."""
    if not sl:
        return "unknown"
    lo, hi = sl["cw"] - 1.96 * sl["se"], sl["cw"] + 1.96 * sl["se"]
    if lo > MATERIAL_C:
        return "rising"
    if hi < -MATERIAL_C:
        return "falling"
    return "flat"


def chg(src, fuel, back):
    ref = OBS_END - timedelta(days=back)
    if OBS_END in src[fuel] and ref in src[fuel]:
        return round(100 * (src[fuel][OBS_END] - src[fuel][ref]), 1)
    return None


trend = {}
for fuel in TREND_FUELS:
    row = {}
    for tag, src in (("loc", loc), ("nat", nat)):
        sl = ols_cw(src, fuel, TREND_WIN)
        win = [src[fuel][OBS_END - timedelta(days=i)] for i in range(90)
               if (OBS_END - timedelta(days=i)) in src[fuel]]
        row[tag] = {"value": round(src[fuel][OBS_END], 3),
                    "d7": chg(src, fuel, 7), "d30": chg(src, fuel, 30),
                    "d90": chg(src, fuel, 90), "d365": chg(src, fuel, 365),
                    "slope": sl, "slope14": ols_cw(src, fuel, 14),
                    "dir": direction(sl),
                    "band": [round(min(win), 3), round(max(win), 3)] if win else None}
        # Finding 1 used to assert a peak and a band as prose, and both had gone stale:
        # it named 2,349 EUR on 8 April when the true peak is later and higher, and a
        # band whose top was already below the price printed in the tile beside it.
        # Compute them, over the life of the series and since the cap arrived.
        hist = {d: v for d, v in src[fuel].items() if d <= OBS_END}
        for tag2, floor in (("all", START), ("since_cap", CAP_DAY)):
            h = {d: v for d, v in hist.items() if d >= floor}
            if not h:
                continue
            pk = max(h, key=lambda d: h[d])
            tr = min(h, key=lambda d: h[d])
            row[tag]["peak" if tag2 == "all" else "peak_since_cap"] = {
                "day": pk.isoformat(), "value": round(h[pk], 3)}
            row[tag]["band_" + tag2] = [round(h[tr], 3), round(h[pk], 3)]
    trend[fuel] = row

# "Almost all of the rise came in one month" was asserted; measure it, because the
# honest number is seven tenths and a reader can check seven tenths against the chart.
big_month = None
if monthly:
    mv = {k: v["Gazole"][0] for k, v in monthly.items() if v.get("Gazole") and v["Gazole"][0]}
    ks = sorted(mv)
    steps = [(ks[i], round(100 * (mv[ks[i]] - mv[ks[i - 1]]), 1)) for i in range(1, len(ks))]
    tail = steps[-12:]                      # the same twelve months the d365 figure spans
    if tail:
        worst = max(tail, key=lambda s: s[1])
        rise = trend["Gazole"]["loc"]["d365"]
        big_month = {"month": worst[0], "c": worst[1],
                     "share": round(100 * worst[1] / rise) if rise else None}

# --- the ceiling splits the local market, so the split carries the trend -----
# One mean over all 71 stations describes nobody: the Total-group sites are
# pinned to the ceiling and cannot follow the market up, the rest can and do.
split_rows = defaultdict(dict)
for r in csv.DictReader(open("data/trend_split.csv")):
    split_rows[r["fuel"]][date.fromisoformat(r["day"])] = r
split = {}
for fuel in TREND_FUELS:
    level = CAP if fuel == "Gazole" else PETROL_CAP
    byday = split_rows[fuel]
    obs = sorted(d for d in byday if d <= OBS_END)
    # `days` runs one day past the observations, and trend_split.csv stops at the
    # last observed day: neither series gets a forward-filled point drawn for it.
    ser = {k: [(round(float(byday[d][k]), 4) if d in byday and byday[d][k] else None)
               for d in days]
           for k in ("total_mean", "other_mean")}
    pinned = None
    for d in reversed(obs):
        v = byday[d]["total_mean"]
        if v and abs(float(v) - level) < 5e-5:
            pinned = d
        else:
            break
    tm = {d: float(byday[d]["total_mean"]) for d in obs if byday[d]["total_mean"]}
    om = {d: float(byday[d]["other_mean"]) for d in obs if byday[d]["other_mean"]}
    last = obs[-1]
    split[fuel] = {
        "level": level, "days": [d.isoformat() for d in days],
        "total": ser["total_mean"], "other": ser["other_mean"],
        "total_now": round(tm[last], 3), "other_now": round(om[last], 3),
        "gap_c": round(100 * (om[last] - tm[last]), 1),
        "total_n": int(byday[last]["total_n"]), "other_n": int(byday[last]["other_n"]),
        "pinned_since": pinned.isoformat() if pinned else None,
        "pinned_days": (last - pinned).days if pinned else None,
        "total_d90": round(100 * (tm[last] - tm[last - timedelta(days=90)]), 1)
                     if last - timedelta(days=90) in tm else None,
        "other_d90": round(100 * (om[last] - om[last - timedelta(days=90)]), 1)
                     if last - timedelta(days=90) in om else None,
        "total_slope": ols_cw({fuel: tm}, fuel, TREND_WIN, end=last),
        "other_slope": ols_cw({fuel: om}, fuel, TREND_WIN, end=last),
    }
    # The claim "this group is capped" needs the maximum, not the mean: a mean can sit
    # on a round number by coincidence, a maximum that never clears it cannot. Report
    # the exceptions rather than claiming "never" -- diesel has two of them in 20 months.
    tx = {d: float(byday[d]["total_max"]) for d in obs if byday[d]["total_max"]}
    over = [d for d, v in sorted(tx.items()) if v > level + 5e-5]
    ceil_since = None
    for d in reversed(sorted(tx)):
        if tx[d] > level + 5e-5:
            break
        ceil_since = d
    split[fuel]["cap_evidence"] = {
        "days": len(tx), "over": len(over),
        "last_over": over[-1].isoformat() if over else None,
        "since": ceil_since.isoformat() if ceil_since else None,
        "total_max": round(tx[last], 3) if last in tx else None,
        "other_max": round(float(byday[last]["other_max"]), 3),
    }
# Before the ceiling, Total was the dearer option here; it is worth showing that
# the cap inverted the local ranking rather than simply widening a gap.
pre = date(2026, 3, 1)
if pre in split_rows["Gazole"] and split_rows["Gazole"][pre]["total_mean"]:
    r = split_rows["Gazole"][pre]
    split["Gazole"]["pre_cap"] = {"day": pre.isoformat(),
                                  "gap_c": round(100 * (float(r["other_mean"]) - float(r["total_mean"])), 1)}

# --- day of week ------------------------------------------------------------
DOW = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
wk_dev = defaultdict(lambda: defaultdict(list))
for r in csv.DictReader(open("data/weekday_dev.csv")):
    wk_dev[r["scope"]][r["fuel"]].append(
        {"dow": int(r["dow"]), "name": DOW[int(r["dow"])], "dev": float(r["mean_dev_c"]),
         "se": float(r["se_c"]) if r["se_c"] else None, "n": int(r["n_station_days"]),
         "weeks": int(r["n_weeks"])})
wk_upd = defaultdict(lambda: defaultdict(list))
for r in csv.DictReader(open("data/weekday_upd.csv")):
    up, dn = int(r["n_up"]), int(r["n_down"])
    wk_upd[r["scope"]][r["fuel"]].append(
        {"dow": int(r["dow"]), "name": DOW[int(r["dow"])], "n": int(r["n_updates"]),
         "mean_c": float(r["mean_change_c"]),
         "se": float(r["se_c"]) if r["se_c"] else None,
         "weeks": int(r["n_weeks"]), "up": up, "down": dn,
         "share_up": round(100 * up / (up + dn), 1) if up + dn else None})

# The section's own conclusion, computed rather than asserted: a weekday is worth
# driving for only if its deviation clears both zero (by its clustered error) and
# the materiality floor. Compare whatever it is worth against choosing a station.
wk_scope, wk_fuel = "recent_moving", "Gazole"
wd = sorted(wk_dev[wk_scope][wk_fuel], key=lambda r: r["dev"])
weekday = {"scope": wk_scope, "dev": {f: wk_dev[wk_scope][f] for f in TREND_FUELS},
           "dev_all": {f: wk_dev["all"][f] for f in TREND_FUELS},
           "upd": {f: wk_upd["recent"][f] for f in TREND_FUELS},
           "window_days": 180,
           "cheapest": wd[0] if wd else None, "dearest": wd[-1] if wd else None,
           "spread_c": round(wd[-1]["dev"] - wd[0]["dev"], 2) if wd else None,
           "significant": bool(wd and wd[0]["se"] is not None
                               and abs(wd[0]["dev"]) - 1.96 * wd[0]["se"] > MATERIAL_C)}
# The strongest weekday signal is not the level but when rises land: pick the day
# whose share of increases is furthest above a coin flip by more than its error.
ups = [r for r in wk_upd["recent"][wk_fuel] if r["share_up"] is not None and r["weeks"] >= 10]
up_day = max(ups, key=lambda r: r["share_up"]) if ups else None
weekday["rise_day"] = up_day
weekday["rise_day_sig"] = bool(up_day and up_day["se"] is not None
                               and up_day["share_up"] > 50)

# Why the pooled bars must not be published on their own. Split the same station
# weeks by their own net move and the weekday shape reverses with it: weeks that
# rose are cheap on Monday, weeks that fell are dear on Monday, by nearly the same
# amount, and weeks that did not move are flat all week. So there is no weekday
# habit -- only the arithmetic that a week which climbs is cheap at its start.
# Rising and falling weeks are near enough equal in number, but a rising week
# moves further than a falling one, and that asymmetry is the whole of the pooled
# Monday discount. The report draws these three panels, not the pooled bars.
dec = {}
for sc in ("rose", "fell", "flat"):
    rows = wk_dev[sc][wk_fuel]
    if not rows:
        continue
    dec[sc] = {"rows": rows,
               "weeks": rows[0]["n"],                       # one day per week per station
               "span_c": round(max(r["dev"] for r in rows) - min(r["dev"] for r in rows), 2)}
tot_weeks = sum(v["weeks"] for v in dec.values())
for v in dec.values():
    v["share"] = round(100 * v["weeks"] / tot_weeks, 1) if tot_weeks else None
weekday["dec"] = dec
weekday["dec_fuel"] = wk_fuel
weekday["dec_weeks"] = tot_weeks
# The residue the pooled view shows is the difference between the two spans, not a habit.
if "rose" in dec and "fell" in dec:
    weekday["asym_c"] = round(dec["rose"]["span_c"] - dec["fell"]["span_c"], 2)
pooled = sorted(wk_dev["all"][wk_fuel], key=lambda r: r["dev"])
weekday["pooled"] = {"cheapest": pooled[0], "dearest": pooled[-1],
                     "spread_c": round(pooled[-1]["dev"] - pooled[0]["dev"], 2)} if pooled else None

# --- how old is "today"? -----------------------------------------------------
# The instant feed carries each station's last posted price, whenever that was, so
# "diesel today" is a composite across a fortnight: only a dozen stations posted on
# the snapshot day itself and the oldest diesel price on the page is nearly two weeks
# old. Every panel built from the snapshot has to be able to say so.
fresh_days = sorted((date.fromisoformat(snap) - date.fromisoformat(s["maj"][:10])).days
                    for s in stations if s["prices"]["Gazole"] is not None)
freshness = {
    "snapshot": snap,
    "n": len(fresh_days),
    "today": sum(1 for v in fresh_days if v == 0),
    "stale": sum(1 for v in fresh_days if v > 0),
    "oldest_days": fresh_days[-1] if fresh_days else None,
    "oldest_day": (date.fromisoformat(snap) - timedelta(days=fresh_days[-1])).isoformat()
                  if fresh_days else None,
    "median_days": fresh_days[len(fresh_days) // 2] if fresh_days else None,
}

cards = []
for fuel in ["Gazole", "E10", "SP98", "E85"]:
    cards.append({"fuel": fuel, "label": LABEL[fuel],
                  "value": round(loc[fuel][END], 3),
                  "nat": round(nat[fuel][END], 3),
                  "d30": delta(fuel, 30), "d365": delta(fuel, 365),
                  "n": loc_n[fuel][END],
                  "spark": [v for v in series(loc, fuel)[-90:] if v is not None]})

DATA = {
  "meta": {"center": CENTER_NAME, "radius": int(RADIUS_KM), "start": START.isoformat(),
           "end": END.isoformat(),
           "archive_end": OBS_END.isoformat(),
           "built": max((st["maj"] for st in stations if st["maj"]), default="")[:10],
           "n_stations": len(stations),
           "n_priced": sum(1 for s in stations if any(v is not None for v in s["prices"].values())),
           "n_diesel": sum(1 for s in stations if s["prices"]["Gazole"] is not None),
           "nat_n": nat_n["Gazole"][END], "loc_n": loc_n["Gazole"][END]},
  "days": [d.isoformat() for d in days],
  "obs_end": OBS_END.isoformat(),
  "labels": LABEL,
  "trend": trend,
  "split": split,
  "weekday": weekday,
  "material_c": MATERIAL_C,
  "local": {f: series(loc, f) for f in FUELS},
  "nat":   {f: series(nat, f) for f in FUELS},
  "cards": cards,
  "stations": stations,
  "monthly": {k: monthly[k] for k in sorted(monthly)},
  "spread": [round(loc["Gazole"][d] - nat["Gazole"][d], 4)
             if d in loc["Gazole"] and d in nat["Gazole"] else None for d in days],
  "brands": brand_rows,
  "ceilings": ceilings,
  "cap_others": sorted(cap_others, key=lambda r: r["dist"]),
  "petrol_cap": PETROL_CAP,
  "cap_story": cap_story,
  "big_month": big_month,
  "freshness": freshness,
  # A dated observation, not a live measurement: these two snapshots are kept because
  # they are the only pair whose station rosters were compared by hand. The prose must
  # date it -- read in the present tense it implies today's gap has the same cause,
  # and diesel's snapshot-to-archive gap has since widened from 2 points to 6.
  "churn": {"between": ["2026-09-14", "2026-09-15"],
            "Gazole": {"arrived": 74, "at_ceiling": 71, "base": 9256},
            "E10":    {"arrived": 222, "at_ceiling": 220, "base": 6959},
            "SP98":   {"arrived": 194, "at_ceiling": 191, "base": 7068}},
  "example": {"id": EXAMPLE_ID, "name": "Rocade Purpan",
              "adresse": "6 avenue du Goupe Morhange, Toulouse", "km": ex_st["dist"],
              "reports": [SHORT[f] for f in FUELS if ex_st["prices"][f] is not None],
              "dry": sorted(SHORT[f] for f in ex_st["dry"]),
              "sp98_silent": ex_st["prices"]["SP98"] is None,
              "sold_unreported": "SP98 at 1,990 €",
              "observed": "2026-09-15"},
  "dry_hist": {"days": [d.isoformat() for d in dry_days],
               "table": dry_table, "all": dry_all, "window": DRY_WINDOW},
  "total": {"n": len(total_st),
            "n_diesel": sum(1 for s in total_st if s["prices"]["Gazole"] is not None),
            "n_at_cap": sum(1 for s in total_st if s["prices"]["Gazole"] == CAP),
            "ids": [s["id"] for s in total_st]},
  "rivals": {"n": len(rival_st), "brands": list(RIVALS),
             "ids": [s["id"] for s in rival_st]},
  "cap": {"level": CAP,
          "nat": cap_nat, "loc": cap_loc,
          "n_local": len(capped), "n_local_diesel": sum(1 for s in stations if s["prices"]["Gazole"]),
          "n_dry": len(capped) - len(capped_wet),
          "nearest": {"km": capped_wet[0]["dist"], "ville": capped_wet[0]["ville"],
                      "adresse": capped_wet[0]["adresse"],
                      "maj": capped_wet[0]["maj"]} if capped_wet else None,
          "nearest_any": {"km": capped[0]["dist"], "ville": capped[0]["ville"],
                          "adresse": capped[0]["adresse"],
                          "dry": capped[0]["dry"].get("Gazole", "")} if capped else None,
          "castanet_in_town": castanet_in_town,
          "castanet": {"km": castanet["dist"], "price": castanet["prices"]["Gazole"],
                       "brand": castanet["brand"], "maj": castanet["maj"],
                       "ville": castanet["ville"], "adresse": castanet["adresse"]},
          "save": round(castanet["prices"]["Gazole"] - CAP, 3),
          "since": CAP_DAY.isoformat()},
}
open("data/report_data.json", "w").write(json.dumps(DATA, separators=(",", ":")))
print(f"days={len(days)} stations={len(stations)} months={len(monthly)}")
print(f"cap: {len(capped)}/{sum(1 for s in stations if s['prices']['Gazole'])} local at {CAP}, "
      f"{len(capped)-len(capped_wet)} of them flagged dry; nearest in stock "
      f"{capped_wet[0]['dist'] if capped_wet else None} km (nearest at any price {capped[0]['dist']} km); "
      f"save {round(castanet['prices']['Gazole']-CAP,3)} EUR/L")
print("ceilings (instant feed):", {f: (v["pct_at"], v["pct_below"]) for f, v in ceilings.items()})
print(f"brands: {len(brand_rows)}; Total group {len(total_st)} stations, "
      f"{sum(1 for s in total_st if s['prices']['Gazole'] is not None)} posting diesel, "
      f"{sum(1 for s in total_st if s['prices']['Gazole'] == CAP)} at the ceiling")
print("cards:", [(c['fuel'], c['value'], c['d30'], c['d365']) for c in cards])
print(f"dry: {sum(1 for s in stations if 'Gazole' in s['dry'])} stations with a diesel outage "
      f"open since {dry_cutoff} (snapshot {snap}); rivals in Total table: {len(rival_st)}")
print(f"dry cells: table {dry_table[-1]} (yesterday {dry_table[-2]}, week ago {dry_table[-8]}), "
      f"all local {dry_all[-1]}; series {dry_days[0]}..{dry_days[-1]}")
