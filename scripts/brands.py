#!/usr/bin/env python3
"""Recover station brands by matching prix-carburants stations to OSM fuel features.

The official feed carries no brand field. OSM tags most stations, but
inconsistently: brand/operator/name disagree, and some brand tags are junk
(one Total station is tagged brand=kai). So each of the three tags is tried in
turn and the first *recognised* one wins, rather than the first non-empty one.

Usage: brands.py <osm_fuel.json> <stations_now.csv> <stations.csv> <out.csv>

Both station lists are matched: the instant feed's live sites, then every other
archive station. The archive holds old ids of today's sites, and a station
without a brand counts as "other" in the Total split.
"""
import csv, json, re, sys
from common import haversine_km

MATCH_M = 250          # a prix-carburants station and an OSM node this close are the same site

# (substring, label) — order matters only within a single tag's evaluation
PATTERNS = [
    ("total access",   "Total Access"),
    ("totalenergies access", "Total Access"),
    ("total",          "TotalEnergies"),
    ("totalenergies",  "TotalEnergies"),
    ("elan",           "Élan (TotalEnergies)"),
    ("esso express",   "Esso Express"),
    ("esso",           "Esso"),
    ("avia",           "Avia"),
    ("dyneff",         "Dyneff"),
    ("carrefour contact", "Carrefour Contact"),
    ("carrefour market",  "Carrefour Market"),
    ("carrefour",      "Carrefour"),
    ("intermarche",    "Intermarché"),
    ("leclerc",        "E.Leclerc"),
    ("eleclerc",       "E.Leclerc"),   # "E.Leclerc" once fold drops the dot
    ("auchan",         "Auchan"),
    ("super u",        "Super U"),
    ("station u",      "Super U"),
    ("hyper u",        "Super U"),
    ("systeme u",      "Super U"),
    ("u express",      "Super U"),
    ("casino",         "Casino"),
    ("geant",          "Casino"),
    ("lidl",           "Lidl"),
    ("cora",           "Cora"),
    ("netto",          "Netto"),
    ("bp",             "BP"),
    ("shell",          "Shell"),
    ("agip",           "Eni"),
    ("eni",            "Eni"),
    ("gnvert",         "GNVert (CNG)"),
    ("gaz up",         "Gaz UP (CNG)"),
]

def fold(s):
    k = (s or "").strip().lower()
    for a, b in (("é","e"), ("è","e"), ("ê","e"), ("-"," "), ("'"," "), (".","")):
        k = k.replace(a, b)
    return " ".join(k.split())

def recognise(s):
    k = fold(s)
    if not k:
        return None
    # longest pattern first, so "total access" beats "total"; whole words only,
    # so "eni" does not match "venise" nor "cora" "decoration"
    for pat, out in sorted(PATTERNS, key=lambda p: -len(p[0])):
        if re.search(rf"\b{re.escape(pat)}\b", k):
            return out
    return None

def brand_of(tags):
    """First recognised label across brand, operator, name; else the raw brand tag."""
    fields = [tags.get("brand"), tags.get("operator"), tags.get("name")]
    for f in fields:
        hit = recognise(f)
        if hit:
            return hit, "recognised"
    for f in fields:
        if (f or "").strip():
            return f.strip(), "raw"
    return "", "none"

def main(osm_path, st_path, archive_path, out_path):
    pts = []
    for e in json.load(open(osm_path))["elements"]:
        c = e.get("center") or ({"lat": e["lat"], "lon": e["lon"]} if "lat" in e else None)
        if not c:
            continue
        t = e.get("tags", {})
        label, how = brand_of(t)
        pts.append({"lat": c["lat"], "lon": c["lon"], "brand": label, "how": how,
                    "osm": f"{e['type']}/{e['id']}",
                    "tags": " | ".join(f"{k}={t[k]}" for k in ("brand","operator","name") if t.get(k))})

    live = list(csv.DictReader(open(st_path)))
    ids = {r["id"] for r in live}
    archive_only = [r for r in csv.DictReader(open(archive_path)) if r["id"] not in ids]
    rows, used = [], set()
    for r in live + archive_only:
        la, lo = float(r["lat"]), float(r["lon"])
        best, bd = None, 1e9
        for i, p in enumerate(pts):
            d = 1000 * haversine_km(la, lo, p["lat"], p["lon"])
            if d < bd:
                best, bd, bi = p, d, i
        ok = best and bd <= MATCH_M
        if ok:
            used.add(bi)
        rows.append({"id": r["id"], "ville": r["ville"], "adresse": r["adresse"],
                     "dist_km": r["dist_km"],
                     "brand": best["brand"] if ok else "",
                     "source": best["how"] if ok else "unmatched",
                     "osm": best["osm"] if ok else "",
                     "osm_tags": best["tags"] if ok else "",
                     "match_m": round(bd) if ok else "", "live": r["id"] in ids})
    # Some pairs of stations sit within ~100 m of one another (motorway aires with
    # two sides, twin sites on one street) and OSM maps only one of them. Both then
    # match the same feature, so the brand is inferred rather than observed for the
    # further one; flag it instead of presenting it as certain. A live station
    # beats an archive-only one, which is usually the same site's old id.
    claims = {}
    for r in rows:
        if r["osm"]:
            claims.setdefault(r["osm"], []).append(r)
    for osm, rs in claims.items():
        if len(rs) > 1:
            nearest = min(rs, key=lambda r: (not r["live"], r["match_m"]))
            for r in rs:
                r["shared"] = "" if r is nearest else "1"
    for r in rows:
        r.setdefault("shared", "")

    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","ville","adresse","dist_km","brand",
                                          "source","osm","osm_tags","match_m","shared"],
                           extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)
    named = sum(1 for r in rows if r["brand"])
    print(f"{named}/{len(rows)} stations ({len(ids)} live) matched to a brand within {MATCH_M} m "
          f"({sum(1 for r in rows if r['source']=='raw')} kept a raw OSM tag, "
          f"{sum(1 for r in rows if r['shared'])} share a feature with a closer station)",
          file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:5])
