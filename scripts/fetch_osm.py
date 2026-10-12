#!/usr/bin/env python3
"""Fetch OSM fuel stations around a point via Overpass.

Overpass rejects Python's default user-agent with HTTP 406, hence the header.
Usage: fetch_osm.py <out.json> [lat] [lon] [radius_m]
"""
import sys, urllib.parse, urllib.request

def main(out, lat="43.5161", lon="1.5000", radius="15500"):
    q = (f"[out:json][timeout:90];\n(\n"
         f"  node[amenity=fuel](around:{radius},{lat},{lon});\n"
         f"  way[amenity=fuel](around:{radius},{lat},{lon});\n"
         f"  relation[amenity=fuel](around:{radius},{lat},{lon});\n"
         f");\nout tags center;")
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter",
        data=urllib.parse.urlencode({"data": q}).encode(),
        headers={"User-Agent": "benzine-report/1.0 (fuel price analysis)"})
    with urllib.request.urlopen(req, timeout=150) as r:
        body = r.read()
    open(out, "wb").write(body)
    print(f"wrote {out}: {len(body)} bytes", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:5])
