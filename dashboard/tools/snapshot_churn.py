#!/usr/bin/env python3
"""Compare two instant snapshots: which stations start or stop reporting each fuel.

Motivation: most TotalEnergies sites show no petrol price, yet they sell petrol —
a station on the Toulouse rocade (id 31300008, "Rocade Purpan" in OSM) sold SP98
at 1,990 EUR on 2026-09-15 while reporting only diesel, E85 and LPG, with no
stock-outage flag. This measures how much of the feed's petrol coverage moves
between two consecutive snapshots, and at what price the arrivals report.

Usage: PYTHONPATH=scripts snapshot_churn.py <older.xml> <newer.xml>
"""
import sys
import xml.etree.ElementTree as ET
from config import CEILING
FUELS = tuple(CEILING)

def read(path):
    out = {}
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag != "pdv":
            continue
        sid = el.get("id")
        for p in el.findall("prix"):
            f, v = p.get("nom"), p.get("valeur")
            if f in FUELS and v:
                try:
                    out[(sid, f)] = float(v)
                except ValueError:
                    pass
        el.clear()
    return out

def main(old_path, new_path):
    old, new = read(old_path), read(new_path)
    print(f"{'fuel':7} {'ceil':>6} {'was':>6} {'now':>6} {'+rep':>6} {'-rep':>6} "
          f"{'arrivals at ceiling':>21} {'at ceiling now':>16}")
    for f in FUELS:
        o = {s for (s, g) in old if g == f}
        n = {s for (s, g) in new if g == f}
        arrived, left = n - o, o - n
        cap = CEILING[f]
        at_ceil = sum(1 for s in arrived if abs(new[(s, f)] - cap) < 1e-9)
        now_ceil = sum(1 for s in n if abs(new[(s, f)] - cap) < 1e-9)
        pct = f"{100*at_ceil/len(arrived):.0f}%" if arrived else "n/a"
        print(f"{f:7} {cap:6.3f} {len(o):6d} {len(n):6d} {len(arrived):6d} {len(left):6d} "
              f"{at_ceil:6d} of {len(arrived):<4d} ({pct:>4}) {now_ceil:10d}")
    print("\nA station that starts reporting petrol between two snapshots almost always\n"
          "reports it at the ceiling price, so the snapshot share is a lower bound.")

if __name__ == "__main__":
    main(*sys.argv[1:3])
