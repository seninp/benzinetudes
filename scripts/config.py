"""Every constant of both reports: study areas, dates, ceilings, brand groups.
Change them here, nowhere else.

Zurich was asked for and is absent deliberately: Switzerland publishes no
station-level fuel-price open data (no French-style transparency mandate),
so no Swiss city can be built from public feeds.
"""
from datetime import date

RADIUS_KM = 15.0
START = date(2025, 1, 15)   # before this the archive's own coverage is still ramping
STALE_DAYS = 30             # a station stops counting 30 days after its last update
MIN_STATIONS = 3            # a day enters a mean only where this many stations report
DRY_WINDOW = 30             # an outage counts while open, at most 30 days after debut
FUELS = ("Gazole", "SP95", "SP98", "E10", "E85", "GPLc")
CEILING = {"Gazole": 2.250, "E10": 1.990, "SP98": 1.990}   # TotalEnergies' caps
DIESEL_CAP, PETROL_CAP = CEILING["Gazole"], CEILING["E10"]
CEILING_DAY = date(2026, 4, 8)   # the diesel ceiling first appeared
# A brand group counts as "on the cap" while none of it posts above the ceiling
# and its mean sits within this many euros of it: one capped station posting a
# few centimes under 2.250 would otherwise reset the streak to zero.
PIN_TOL = 0.005
TOTAL_GROUP = ("TotalEnergies", "Total Access", "Élan (TotalEnergies)")

CITIES = [
    dict(slug="castanet", name="Castanet-Tolosan", lat=43.5161, lon=1.5000,
         color="#2a78d6", blurb="a small commune south-east of Toulouse"),
    dict(slug="lyon", name="Lyon", lat=45.7640, lon=4.8357,
         color="#eb6834", blurb="France's second urban area"),
    dict(slug="gentilly", name="Gentilly", lat=48.8133, lon=2.3444,
         color="#1baf7a", blurb="just south of the Paris périphérique; the radius covers most of Paris"),
]

# the dashboard covers the first city alone
CENTER_NAME = "Castanet-Tolosan (31320)"
CENTER_LAT, CENTER_LON = CITIES[0]["lat"], CITIES[0]["lon"]
