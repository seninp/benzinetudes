#!/usr/bin/env python3
"""Fetch OSM brands for every city: Overpass query, then position match.

A response younger than 30 days is reused — brands change slowly, and the
public Overpass endpoints buckle under repeated big queries.
"""
import os, sys, time
from config import CITIES, RADIUS_KM
import fetch_osm, brands

for i, c in enumerate(CITIES):
    d = f"data/{c['slug']}"
    osm = f"{d}/osm_fuel.json"
    fresh = os.path.exists(osm) and time.time() - os.path.getmtime(osm) < 30 * 86400
    if not fresh:
        if i:
            time.sleep(5)   # be polite to Overpass
        fetch_osm.main(osm, str(c["lat"]), str(c["lon"]),
                       str(int(RADIUS_KM * 1000 + 500)))
    else:
        age = (time.time() - os.path.getmtime(osm)) / 86400
        print(f"{c['name']}: reusing OSM answer from {age:.0f} days ago", file=sys.stderr)
    brands.main(osm, f"{d}/stations_now.csv", f"{d}/stations.csv", f"{d}/brands.csv")
