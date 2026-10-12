"""Constants shared by the dashboard scripts. Change the study area here, nowhere else."""
from datetime import date

CENTER_NAME = "Castanet-Tolosan (31320)"
CENTER_LAT, CENTER_LON = 43.5161, 1.5000
RADIUS_KM = 15.0
START = date(2025, 1, 15)   # before this the archive's own coverage is still ramping
STALE_DAYS = 30             # a station stops counting 30 days after its last update
DRY_WINDOW = 30             # an outage counts while open, at most 30 days after debut
MIN_STATIONS = 3            # a day enters a mean only where this many stations report
FUELS = ("Gazole", "SP95", "SP98", "E10", "E85", "GPLc")
DIESEL_CAP, PETROL_CAP = 2.250, 1.990
CAP_DAY = date(2026, 4, 8)  # the day the 2,250 EUR diesel cluster formed
TOTAL_GROUP = ("TotalEnergies", "Total Access", "Élan (TotalEnergies)")
