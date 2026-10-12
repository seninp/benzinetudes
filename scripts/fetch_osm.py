#!/usr/bin/env python3
"""Fetch OSM fuel stations around a point via Overpass.

Overpass rejects Python's default user-agent with HTTP 406, hence the header.
The public endpoints 504 under load, so each is tried in turn with a pause. An
answer with no elements counts as a failure: overpass.osm.ch, for one, is a
Swiss-only extract that answers 200 and empty for France, and writing that over
the cache would wipe every brand. A partial answer cut off by the server's own
timeout carries a "remark" and counts as a failure too. So does an answer from
a database older than the cached one: mirrors lag, and on 2026-10-12
overpass.private.coffee answered from a July 2026 base, which would have
reverted three months of tag edits. If every attempt fails and a previous
answer is on disk, it is kept — brands change far more slowly than prices.

Usage: fetch_osm.py <out.json> [lat] [lon] [radius_m]

The defaults are Castanet-Tolosan with 500 m beyond the 15 km radius, so a
station just inside the radius still finds an OSM feature just outside it.
"""
import json, os, sys, time, urllib.parse, urllib.request
from config import CENTER_LAT, CENTER_LON, RADIUS_KM

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

def main(out, lat=str(CENTER_LAT), lon=str(CENTER_LON), radius=str(int(RADIUS_KM * 1000 + 500))):
    q = (f"[out:json][timeout:120];\n(\n"
         f"  node[amenity=fuel](around:{radius},{lat},{lon});\n"
         f"  way[amenity=fuel](around:{radius},{lat},{lon});\n"
         f"  relation[amenity=fuel](around:{radius},{lat},{lon});\n"
         f");\nout tags center;")
    cached_base = ""
    if os.path.exists(out):
        cached_base = json.load(open(out)).get("osm3s", {}).get("timestamp_osm_base", "")
    # One try per endpoint: a run holds the pipeline lock while it waits here.
    for url in ENDPOINTS:
        req = urllib.request.Request(
            url, data=urllib.parse.urlencode({"data": q}).encode(),
            headers={"User-Agent": "benzine-fuel-prices/1.0 (github.com/seninp/benzinetudes)"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                body = r.read()
            ans = json.loads(body)
            n = len(ans.get("elements", []))
            if not n:
                raise ValueError("answer has no elements")
            if ans.get("remark"):
                raise ValueError(f"partial answer: {ans['remark']}")
            base = ans.get("osm3s", {}).get("timestamp_osm_base", "")
            if base < cached_base:
                raise ValueError(f"database from {base}, older than the cached {cached_base}")
            open(out, "wb").write(body)
            print(f"wrote {out}: {n} elements, {len(body)} bytes (via {url})", file=sys.stderr)
            return
        except Exception as e:
            print(f"{url}: {e}, retrying", file=sys.stderr)
            time.sleep(10)
    if os.path.exists(out):
        print(f"every Overpass attempt failed; keeping the cached {out}", file=sys.stderr)
        return
    raise SystemExit(f"every Overpass attempt failed and there is no cached {out}")

if __name__ == "__main__":
    main(*sys.argv[1:5])
