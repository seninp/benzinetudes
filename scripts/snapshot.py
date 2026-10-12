#!/usr/bin/env python3
"""Per-station current prices per city from the instant feed.

A missing fuel means "not reported", not "not sold": capped stations drop in
and out of the instant feed per fuel and always come back at the ceiling.
"""
import csv, sys
import xml.etree.ElementTree as ET
from cities import CITIES, FUELS

def main(instant_xml):
    metas = {}
    for c in CITIES:
        for r in csv.DictReader(open(f"data/{c['slug']}/stations.csv")):
            metas.setdefault(r["id"], []).append((c["slug"], r))
    out = {c["slug"]: [] for c in CITIES}
    for _, el in ET.iterparse(instant_xml, events=("end",)):
        if el.tag != "pdv":
            continue
        for slug, m in metas.get(el.get("id"), ()):
            row = {"id": el.get("id"), "ville": m["ville"], "adresse": m["adresse"],
                   "cp": m["cp"], "dist_km": m["dist_km"], "lat": m["lat"], "lon": m["lon"]}
            maj = ""
            for p in el.findall("prix"):
                if p.get("nom") in FUELS and p.get("valeur"):
                    row[p.get("nom")] = p.get("valeur")
                    maj = max(maj, p.get("maj") or "")
            row["maj"] = maj
            out[slug].append(row)
        el.clear()
    cols = ["id", "ville", "cp", "adresse", "dist_km", "lat", "lon"] + list(FUELS) + ["maj"]
    for c in CITIES:
        path = f"data/{c['slug']}/stations_now.csv"
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for r in sorted(out[c["slug"]], key=lambda r: float(r["dist_km"])):
                w.writerow(r)
        print(f"{c['name']}: {len(out[c['slug']])} stations in instant feed", file=sys.stderr)

if __name__ == "__main__":
    main(sys.argv[1])
