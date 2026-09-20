#!/usr/bin/env python3
"""Aggregate CSVs -> data/<slug>/summary.json + data/compare.json.

Everything the figures and the README show is computed here, once.
"""
import csv, json, sys
from collections import defaultdict
from datetime import date, timedelta
from cities import CITIES, FUELS, CEILING, START, DRY_WINDOW

def load_daily(path):
    s, n = defaultdict(dict), defaultdict(dict)
    for r in csv.DictReader(open(path)):
        d = date.fromisoformat(r["day"])
        if d >= START:
            s[r["fuel"]][d] = float(r["mean_price"])
            n[r["fuel"]][d] = int(r["n_stations"])
    return s, n

def dry_series(hist_path, days):
    """Dry station-fuel pairs per day: an outage counts while it is open and
    for at most DRY_WINDOW days after it began."""
    spans = []
    for r in csv.DictReader(open(hist_path)):
        if r["fuel"] not in FUELS:
            continue
        d0 = date.fromisoformat(r["debut"])
        d1 = date.fromisoformat(r["fin"]) if r["fin"] else None
        stop = d0 + timedelta(days=DRY_WINDOW)
        spans.append((d0, min(d1, stop) if d1 else stop))
    out = []
    for d in days:
        out.append(sum(1 for a, b in spans if a <= d <= b))
    return out

def main():
    nat, nat_n = load_daily("data/nat_daily.csv")
    end = max(nat["Gazole"])
    days = []
    d = START
    while d <= end:
        days.append(d); d += timedelta(days=1)

    compare = {"end": end.isoformat(), "start": START.isoformat(),
               "archive_end": open("data/archive_end.txt").read().strip(),
               "nat_diesel": round(nat["Gazole"][end], 3), "cities": []}
    nat_series = {f: [round(nat[f][d], 4) if d in nat[f] else None for d in days]
                  for f in ("Gazole", "E10")}

    for c in CITIES:
        slug = c["slug"]
        loc, loc_n = load_daily(f"data/{slug}/loc_daily.csv")
        stations = list(csv.DictReader(open(f"data/{slug}/stations.csv")))
        now = list(csv.DictReader(open(f"data/{slug}/stations_now.csv")))
        brands = {r["id"]: r for r in csv.DictReader(open(f"data/{slug}/brands.csv"))}
        open_rup = defaultdict(dict)
        for r in csv.DictReader(open(f"data/{slug}/ruptures.csv")):
            open_rup[r["id"]][r["fuel"]] = r["debut"]

        def dry_now(sid, fuel):
            deb = open_rup.get(sid, {}).get(fuel)
            return bool(deb) and date.fromisoformat(deb) >= end - timedelta(days=DRY_WINDOW)

        # capshare: archive share at the ceiling on the last day (30-day window)
        capshares = {}
        for r in csv.DictReader(open(f"data/{slug}/capshare.csv")):
            if r["day"] == end.isoformat():
                capshares[r["fuel"]] = {
                    "nat_pct": round(100 * int(r["nat_cap"]) / max(1, int(r["nat_n"])), 1),
                    "loc_pct": round(100 * int(r["loc_cap"]) / max(1, int(r["loc_n"])), 1),
                    "loc_n": int(r["loc_n"]), "loc_cap": int(r["loc_cap"])}

        dry = dry_series(f"data/{slug}/rupture_hist.csv", days)
        active = [sum(loc_n[f].get(d, 0) for f in FUELS) or None for d in days]
        dry_pct = [round(100 * a / b, 2) if b else None for a, b in zip(dry, active)]

        # nearest capped diesel station and the station table, from the snapshot
        def price(r, f):
            v = r.get(f)
            return round(float(v), 3) if v else None
        capped = [r for r in now if price(r, "Gazole") == CEILING["Gazole"]]
        nearest_cap = None
        if capped:
            r = min(capped, key=lambda r: float(r["dist_km"]))
            nearest_cap = {"km": float(r["dist_km"]), "ville": r["ville"], "adresse": r["adresse"]}

        table = []
        for r in now[:12]:
            b = brands.get(r["id"], {})
            table.append({
                "dist": float(r["dist_km"]), "ville": r["ville"], "adresse": r["adresse"],
                "brand": (b.get("brand") or "") + ("?" if b.get("shared") else ""),
                "prices": {f: price(r, f) for f in ("Gazole", "E10", "SP98")},
                "dry": [f for f in FUELS if dry_now(r["id"], f)]})

        pts = []
        for r in now:
            g = price(r, "Gazole")
            pts.append({"lat": float(r["lat"]), "lon": float(r["lon"]),
                        "gazole": g, "at_cap": g == CEILING["Gazole"],
                        "dry_diesel": dry_now(r["id"], "Gazole")})

        def delta(fuel, back):
            ref = end - timedelta(days=back)
            if end in loc[fuel] and ref in loc[fuel]:
                return round(loc[fuel][end] - loc[fuel][ref], 3)
            return None

        s = {"slug": slug, "name": c["name"], "color": c["color"], "blurb": c["blurb"],
             "lat": c["lat"], "lon": c["lon"],
             "end": end.isoformat(), "n_stations": len(stations),
             "n_now": len(now),
             "diesel": round(loc["Gazole"][end], 3), "diesel_nat": round(nat["Gazole"][end], 3),
             "d30": delta("Gazole", 30), "d365": delta("Gazole", 365),
             "e10": round(loc["E10"][end], 3) if end in loc["E10"] else None,
             "capshares": capshares,
             "dry_now": dry[-1], "dry_pct_now": dry_pct[-1],
             "nearest_cap": nearest_cap,
             "table": table, "points": pts,
             "series": {"days": [d.isoformat() for d in days],
                        "loc": {f: [round(loc[f][d], 4) if d in loc[f] else None for d in days]
                                for f in ("Gazole", "E10")},
                        "dry": dry, "dry_pct": dry_pct}}
        json.dump(s, open(f"data/{slug}/summary.json", "w"), ensure_ascii=False)
        compare["cities"].append({k: s[k] for k in
            ("slug", "name", "color", "blurb", "lat", "lon", "n_stations", "n_now", "diesel",
             "d30", "d365", "e10", "capshares", "dry_now", "dry_pct_now", "nearest_cap")})
        print(f"{c['name']}: diesel {s['diesel']}, dry {s['dry_now']} "
              f"({s['dry_pct_now']}%), cap archive {capshares.get('Gazole', {}).get('loc_pct')}%",
              file=sys.stderr)

    compare["nat_series"] = nat_series
    compare["days"] = [d.isoformat() for d in days]
    json.dump(compare, open("data/compare.json", "w"), ensure_ascii=False)
    print(f"series {START} .. {end}", file=sys.stderr)

if __name__ == "__main__":
    main()
