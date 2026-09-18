#!/usr/bin/env python3
"""Stream a PrixCarburants annual XML -> daily last-price rows per station+fuel."""
import csv, sys
import xml.etree.ElementTree as ET

FUELS = ("Gazole", "SP95", "SP98", "E10", "E85", "GPLc")

def run(xml_path, out_csv):
    n = 0
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        for _, el in ET.iterparse(xml_path, events=("end",)):
            if el.tag != "pdv":
                continue
            sid = el.get("id")
            best = {}                      # (fuel, day) -> (ts, price)
            for p in el.findall("prix"):
                nom, v, maj = p.get("nom"), p.get("valeur"), p.get("maj")
                if not (nom in FUELS and v and maj):
                    continue
                try:
                    val = float(v)
                except ValueError:
                    continue
                if val > 10:
                    val /= 1000.0
                if not (0.3 < val < 5.0):
                    continue
                k = (nom, maj[:10])
                if k not in best or maj > best[k][0]:
                    best[k] = (maj, val)
            for (nom, day), (_, val) in best.items():
                w.writerow([sid, nom, day, round(val, 3)]); n += 1
            el.clear()
    print(f"{xml_path} -> {out_csv}: {n} daily rows", file=sys.stderr)

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
