#!/usr/bin/env python3
"""Stock outages (rupture elements) per city, one pass over the annual XMLs.

Only the annual archive carries rupture elements; the instant feed has none, so
a current outage is invisible in the snapshot. A rupture with a debut and no fin
is still open; ancient open ones mean the station stopped selling that fuel.
Pass the XMLs in year order — the later file's fin wins.

Writes per city: ruptures.csv (latest open flag per station+fuel) and
rupture_hist.csv (every interval, open or closed, for the dry-count history).
"""
import csv, sys
import xml.etree.ElementTree as ET
from cities import CITIES

def main(*xml_paths):
    subs = {}
    for c in CITIES:
        for r in csv.DictReader(open(f"data/{c['slug']}/stations.csv")):
            subs.setdefault(r["id"], []).append(c["slug"])
    intervals = {slug: {} for slug in (c["slug"] for c in CITIES)}
    for xml_path in xml_paths:
        for _, pdv in ET.iterparse(xml_path):
            if pdv.tag != "pdv":
                continue
            slugs = subs.get(pdv.get("id"))
            if slugs:
                for r in pdv.iter("rupture"):
                    if r.get("debut"):
                        k = (pdv.get("id"), r.get("nom"), r.get("debut")[:10])
                        for slug in slugs:
                            intervals[slug][k] = (r.get("fin") or "")[:10]
            pdv.clear()
    for c in CITIES:
        slug = c["slug"]
        open_rup = {}
        for (sid, fuel, debut), fin in intervals[slug].items():
            if not fin:
                k = (sid, fuel)
                open_rup[k] = max(open_rup.get(k, ""), debut)
        with open(f"data/{slug}/ruptures.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "fuel", "debut"])
            for (sid, fuel), debut in sorted(open_rup.items()):
                w.writerow([sid, fuel, debut])
        with open(f"data/{slug}/rupture_hist.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["id", "fuel", "debut", "fin"])
            for (sid, fuel, debut), fin in sorted(intervals[slug].items()):
                w.writerow([sid, fuel, debut, fin])
        print(f"{c['name']}: {len(open_rup)} open ruptures, "
              f"{len(intervals[slug])} intervals", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:])
