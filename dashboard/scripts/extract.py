#!/usr/bin/env python3
"""Extract fuel-price time series for stations near a point from PrixCarburants XML."""
import csv, sys
import xml.etree.ElementTree as ET
from common import haversine_km
from config import CENTER_LAT, CENTER_LON, RADIUS_KM

def run(xml_path, st_out, px_out):
    stations, rows = {}, []
    ctx = ET.iterparse(xml_path, events=("end",))
    for _, el in ctx:
        if el.tag != "pdv":
            continue
        try:
            lat = float(el.get("latitude") or 0) / 100000.0
            lon = float(el.get("longitude") or 0) / 100000.0
        except ValueError:
            el.clear(); continue
        if lat == 0.0 and lon == 0.0:
            el.clear(); continue
        d = haversine_km(CENTER_LAT, CENTER_LON, lat, lon)
        if d <= RADIUS_KM:
            sid = el.get("id")
            adr = (el.findtext("adresse") or "").strip()
            vil = (el.findtext("ville") or "").strip()
            stations[sid] = dict(id=sid, cp=el.get("cp"), ville=vil, adresse=adr,
                                 lat=round(lat, 5), lon=round(lon, 5),
                                 dist_km=round(d, 2), pop=el.get("pop"))
            for p in el.findall("prix"):
                v, maj = p.get("valeur"), p.get("maj")
                if not v or not maj:
                    continue
                try:
                    val = float(v)
                except ValueError:
                    continue
                if val > 10:        # older files store thousandths
                    val /= 1000.0
                rows.append((sid, p.get("nom"), maj, round(val, 3)))
        el.clear()
    with open(st_out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","cp","ville","adresse","lat","lon","dist_km","pop"])
        w.writeheader()
        for s in sorted(stations.values(), key=lambda s: s["dist_km"]):
            w.writerow(s)
    with open(px_out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["station_id","fuel","ts","price"])
        w.writerows(sorted(rows))
    print(f"{xml_path}: {len(stations)} stations <= {RADIUS_KM}km, {len(rows)} price points", file=sys.stderr)

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2], sys.argv[3])
