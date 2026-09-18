#!/usr/bin/env python3
"""One pass over each PrixCarburants XML: the stations within radius of any city.

Later files win on station metadata (pass them in year order, instant last).
Writes data/<slug>/stations.csv sorted by distance.
"""
import csv, math, os, sys
import xml.etree.ElementTree as ET
from cities import CITIES, RADIUS_KM

def haversine(la1, lo1, la2, lo2):
    R = 6371.0088
    p1, p2 = math.radians(la1), math.radians(la2)
    a = (math.sin((p2 - p1) / 2) ** 2 +
         math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))

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
                d = haversine(c["lat"], c["lon"], lat, lon)
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
