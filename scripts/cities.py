"""The cities and shared constants of benzinetudes.

Zurich was asked for and is absent deliberately: Switzerland publishes no
station-level fuel-price open data (no French-style transparency mandate),
so no Swiss city can be built from public feeds.
"""
from datetime import date

RADIUS_KM = 15.0
START = date(2025, 1, 15)   # before this the archive's own coverage is still ramping
STALE_DAYS = 30             # a station stops counting 30 days after its last update
DRY_WINDOW = 30             # an outage counts while open, at most 30 days after debut
FUELS = ("Gazole", "SP95", "SP98", "E10", "E85", "GPLc")
CEILING = {"Gazole": 2.250, "E10": 1.990, "SP98": 1.990}   # TotalEnergies' caps

CITIES = [
    dict(slug="castanet", name="Castanet-Tolosan", lat=43.5161, lon=1.5000,
         color="#2a78d6", blurb="a small commune south-east of Toulouse"),
    dict(slug="lyon", name="Lyon", lat=45.7640, lon=4.8357,
         color="#eb6834", blurb="France's second urban area"),
    dict(slug="gentilly", name="Gentilly", lat=48.8133, lon=2.3444,
         color="#1baf7a", blurb="just south of the Paris périphérique; the radius covers most of Paris"),
]
