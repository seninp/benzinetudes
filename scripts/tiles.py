#!/usr/bin/env python3
"""A real basemap under the station maps: OpenStreetMap raster tiles.

The standard OSM layer, desaturated and lifted towards the report's surface
here rather than fetched pre-muted: CARTO's Positron needs an API key now and
stamps "API KEY REQUIRED" across unkeyed tiles. Doing it locally keeps the
source unambiguously free and the styling under our control — the markers must
stay the loudest thing on the figure. Tiles are cached under data/geo/tiles, so
only the first build downloads anything.

Everything is plotted in kilometres east/north of the city centre. Mercator is
conformal, so at this scale one km-per-world-unit factor holds for both axes and
the tiles register with the station positions exactly; a 15 km circle stays a
circle to within 50 m.
"""
import math, os, time, urllib.request
from PIL import Image

TILE = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
UA = "benzinetudes/1.0 (+https://github.com/seninp/benzinetudes)"
ATTRIB = "basemap © OpenStreetMap contributors"
CACHE = "data/geo/tiles/osm"
EQUATOR_KM = 40075.017


def merc(lon, lat):
    """Web Mercator in world units: (0,0) at 180 W/85 N, (1,1) at 180 E/85 S."""
    s = math.sin(math.radians(lat))
    return (lon + 180.0) / 360.0, 0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)


def km_per_unit(lat):
    return EQUATOR_KM * math.cos(math.radians(lat))


def _tile(z, x, y):
    path = f"{CACHE}/{z}/{x}/{y}.png"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        req = urllib.request.Request(TILE.format(z=z, x=x, y=y),
                                    headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as f:
            blob = f.read()
        with open(path + ".part", "wb") as out:
            out.write(blob)
        os.replace(path + ".part", path)
        time.sleep(0.12)            # a polite tile client
    return Image.open(path).convert("RGB")


def basemap(lat, lon, half_km, zoom=12, desaturate=0.75, fade=0.30,
            surface="#fcfcfb", max_px=1800):
    """Stitch the tiles covering ±half_km around (lat, lon).

    Returns (image, extent) with extent in km east/north of the centre, ready
    for ax.imshow(img, extent=extent, origin="upper").
    """
    k = km_per_unit(lat)
    x0, y0 = merc(lon, lat)
    d = half_km / k
    n = 2 ** zoom
    xa, xb = int((x0 - d) * n), int((x0 + d) * n)
    ya, yb = int((y0 - d) * n), int((y0 + d) * n)
    px = 256
    img = Image.new("RGB", ((xb - xa + 1) * px, (yb - ya + 1) * px), surface)
    for tx in range(xa, xb + 1):
        for ty in range(ya, yb + 1):
            img.paste(_tile(zoom, tx, ty), ((tx - xa) * px, (ty - ya) * px))
    extent = ((xa / n - x0) * k, ((xb + 1) / n - x0) * k,
              -((yb + 1) / n - y0) * k, -(ya / n - y0) * k)
    if desaturate:                  # drop OSM's greens and yellows towards grey
        img = Image.blend(img, img.convert("L").convert("RGB"), desaturate)
    if fade:                        # lift the basemap towards the report's surface
        img = Image.blend(img, Image.new("RGB", img.size, surface), fade)
    if img.width > max_px:
        img = img.resize((max_px, round(img.height * max_px / img.width)), Image.LANCZOS)
    return img, extent
