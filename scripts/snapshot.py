#!/usr/bin/env python3
"""Per-station current prices for the stations in st_all.csv, from the instant feed."""
import csv, sys
import xml.etree.ElementTree as ET

FUELS = ("Gazole","SP95","SP98","E10","E85","GPLc")
meta = {r["id"]: r for r in csv.DictReader(open("st_all.csv"))}
out = []
for _, el in ET.iterparse("PrixCarburants_instantane.xml", events=("end",)):
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
w = csv.DictWriter(open("stations_now.csv","w",newline=""), fieldnames=cols, extrasaction="ignore")
w.writeheader()
for r in sorted(out, key=lambda r: float(r["dist_km"])):
    w.writerow(r)
print(f"{len(out)} stations in instant feed", file=sys.stderr)
