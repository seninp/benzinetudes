#!/usr/bin/env python3
"""Embed report_data.json into the HTML template at its /*__DATA__*/ marker.

Usage: render_html.py <template.html> <report_data.json> <out.html>
"""
import sys

def main(template, data, out):
    h = open(template).read()
    if "/*__DATA__*/" not in h:
        raise SystemExit(f"{template}: no /*__DATA__*/ marker")
    open(out, "w").write(h.replace("/*__DATA__*/", open(data).read()))
    print(f"wrote {out}")

if __name__ == "__main__":
    main(*sys.argv[1:4])
