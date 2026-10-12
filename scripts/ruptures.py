#!/usr/bin/env python3
"""Stock outages (rupture elements) per local station.

Only the annual archive carries rupture elements; the instant feed has none at
all, so a current outage is invisible in the snapshot. A rupture with a debut
and no fin is still open. Ancient open ruptures mean the station stopped
selling that fuel; deciding what counts as "recently dry" is the report's job.
Where a station declares several open ruptures for one fuel, the latest wins.

Writes two files: the open flags, and every interval closed or open, so the
report can reconstruct the dry count on any past day. A rupture that opened in
one annual file and closed in the next appears in both; the later file's fin
wins, so pass the XMLs in year order.
"""
import csv, sys
import xml.etree.ElementTree as ET

def main(subset_csv, out_open, out_hist, *xml_paths):
    sub = set(r["id"] for r in csv.DictReader(open(subset_csv)))
    intervals = {}   # (id, fuel, debut) -> fin, "" while open
    for xml_path in xml_paths:
        for _, pdv in ET.iterparse(xml_path):
            if pdv.tag != "pdv":
                continue
            if pdv.get("id") in sub:
                for r in pdv.iter("rupture"):
                    if r.get("debut"):
                        k = (pdv.get("id"), r.get("nom"), r.get("debut")[:10])
                        intervals[k] = (r.get("fin") or "")[:10]
            pdv.clear()
    open_rup = {}   # (id, fuel) -> latest debut
    for (sid, fuel, debut), fin in intervals.items():
        if not fin:
            k = (sid, fuel)
            open_rup[k] = max(open_rup.get(k, ""), debut)
    with open(out_open, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "fuel", "debut"])
        for (sid, fuel), debut in sorted(open_rup.items()):
            w.writerow([sid, fuel, debut])
    with open(out_hist, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "fuel", "debut", "fin"])
        for (sid, fuel, debut), fin in sorted(intervals.items()):
            w.writerow([sid, fuel, debut, fin])
    print(f"wrote {out_open}: {len(open_rup)} open ruptures at "
          f"{len(set(k[0] for k in open_rup))} stations; "
          f"{out_hist}: {len(intervals)} intervals", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:])
