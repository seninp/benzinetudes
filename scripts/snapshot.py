#!/usr/bin/env python3
"""Per-station current prices for the stations in st_all.csv, from the instant feed.

Usage: snapshot.py <st_all.csv> <PrixCarburants_instantane.xml> <stations_now.csv>
"""
import csv, sys
import xml.etree.ElementTree as ET
from config import FUELS

def main(st_csv, instant_xml, out_csv):
    meta = {r["id"]: r for r in csv.DictReader(open(st_csv))}
    out = []
    for _, el in ET.iterparse(instant_xml, events=("end",)):
        if el.tag != "pdv":
            continue
        sid = el.get("id")
        if sid in meta:
            m = meta[sid]
            row = {"id": sid, "ville": m["ville"], "adresse": m["adresse"],
                   "cp": m["cp"], "dist_km": m["dist_km"], "lat": m["lat"], "lon": m["lon"]}
            maj = ""
            for p in el.findall("prix"):
                if p.get("nom") in FUELS and p.get("valeur"):
                    row[p.get("nom")] = p.get("valeur")
                    maj = max(maj, p.get("maj") or "")
            row["maj"] = maj
            out.append(row)
        el.clear()
    cols = ["id","ville","cp","adresse","dist_km","lat","lon"] + list(FUELS) + ["maj"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(out, key=lambda r: float(r["dist_km"])):
            w.writerow(r)
    print(f"{len(out)} stations in instant feed", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:4])
