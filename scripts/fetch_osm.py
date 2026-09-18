#!/usr/bin/env python3
"""Fetch OSM fuel stations around a point via Overpass.

Overpass rejects Python's default user-agent with HTTP 406, hence the header.
The public endpoints 504 under load, so each is tried in turn with a pause.
Usage: fetch_osm.py <out.json> [lat] [lon] [radius_m]
"""
import sys, time, urllib.parse, urllib.request

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

def main(out, lat="43.5161", lon="1.5000", radius="15500"):
    q = (f"[out:json][timeout:120];\n(\n"
         f"  node[amenity=fuel](around:{radius},{lat},{lon});\n"
         f"  way[amenity=fuel](around:{radius},{lat},{lon});\n"
         f"  relation[amenity=fuel](around:{radius},{lat},{lon});\n"
         f");\nout tags center;")
    last = None
    for attempt in range(6):
        url = ENDPOINTS[attempt % len(ENDPOINTS)]
        req = urllib.request.Request(
            url, data=urllib.parse.urlencode({"data": q}).encode(),
            headers={"User-Agent": "benzinetudes/1.0 (fuel price analysis)"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
            open(out, "wb").write(body)
            print(f"wrote {out}: {len(body)} bytes (via {url})", file=sys.stderr)
            return
        except Exception as e:
            last = e
            print(f"{url}: {e}, retrying", file=sys.stderr)
            time.sleep(10)
    raise last

if __name__ == "__main__":
    main(*sys.argv[1:5])
