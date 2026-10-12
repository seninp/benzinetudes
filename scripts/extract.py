#!/usr/bin/env python3
"""One pass over each PrixCarburants XML: the stations within radius of any city.

Later files win on station metadata (pass them in year order, instant last).
Writes data/<slug>/stations.csv sorted by distance.
"""
import csv, os, sys
import xml.etree.ElementTree as ET
from config import CITIES, RADIUS_KM
from common import haversine_km

def main(*xml_paths):
    found = {c["slug"]: {} for c in CITIES}
    for xml_path in xml_paths:
        n = 0
        for _, el in ET.iterparse(xml_path, events=("end",)):
            if el.tag != "pdv":
                continue
            try:
                lat = float(el.get("latitude") or 0) / 100000.0
                lon = float(el.get("longitude") or 0) / 100000.0
            except ValueError:
                el.clear(); continue
            if lat == 0.0 and lon == 0.0:
                el.clear(); continue
            for c in CITIES:
                d = haversine_km(c["lat"], c["lon"], lat, lon)
                if d <= RADIUS_KM:
                    found[c["slug"]][el.get("id")] = dict(
                        id=el.get("id"), cp=el.get("cp"),
                        ville=(el.findtext("ville") or "").strip(),
                        adresse=(el.findtext("adresse") or "").strip(),
                        lat=round(lat, 5), lon=round(lon, 5),
                        dist_km=round(d, 2), pop=el.get("pop"))
                    n += 1
            el.clear()
        print(f"{xml_path}: {n} in-radius station records", file=sys.stderr)
    for c in CITIES:
        rows = sorted(found[c["slug"]].values(), key=lambda r: r["dist_km"])
        os.makedirs(f"data/{c['slug']}", exist_ok=True)
        with open(f"data/{c['slug']}/stations.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        print(f"{c['name']}: {len(rows)} stations within {RADIUS_KM:g} km", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:])
