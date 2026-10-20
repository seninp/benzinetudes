#!/usr/bin/env python3
"""Ceiling statistics from the instantaneous feed — today's snapshot, all of France.

The annual archive and the instant feed agree closely for diesel (21,9% vs 19,8%
of stations at exactly 2,250 EUR) but not for petrol (23,4% vs 13,8% at 1,990):
about 860 stations carry an E10 price of 1,990 in the archive and no E10 entry at
all in the snapshot. Neither file explains the gap, so the report quotes this
snapshot for today's figures and uses the archive only for the diesel history.
"""
import csv, sys
import xml.etree.ElementTree as ET
from config import CEILING

def main(xml_path, out_csv):
    n = {f: 0 for f in CEILING}
    at = {f: 0 for f in CEILING}
    below = {f: 0 for f in CEILING}
    lowest = {f: None for f in CEILING}
    for _, el in ET.iterparse(xml_path, events=("end",)):
        if el.tag != "pdv":
            continue
        for p in el.findall("prix"):
            f, v = p.get("nom"), p.get("valeur")
            if f not in CEILING or not v:
                continue
            try:
                val = float(v)
            except ValueError:
                continue
            n[f] += 1
            if abs(val - CEILING[f]) < 1e-9:
                at[f] += 1
            elif val < CEILING[f]:
                below[f] += 1
            if lowest[f] is None or val < lowest[f]:
                lowest[f] = val
        el.clear()
    with open(out_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["fuel","ceiling","n","at_ceiling","below","lowest"])
        for f in CEILING:
            w.writerow([f, CEILING[f], n[f], at[f], below[f], lowest[f]])
            print(f"  {f:7} n={n[f]:5d} at {CEILING[f]}: {at[f]:5d} "
                  f"({100*at[f]/max(1, n[f]):4.1f}%)  below: {below[f]:4d} ({100*below[f]/max(1, n[f]):4.1f}%)  "
                  f"lowest {lowest[f]}", file=sys.stderr)

if __name__ == "__main__":
    main(*sys.argv[1:3])
