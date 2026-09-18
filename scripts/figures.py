#!/usr/bin/env python3
"""All PNG figures for the README, from data/*/summary.json + data/compare.json."""
import csv, json, math, os
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from cities import CITIES, CEILING

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; SECOND = "#52514e"; MUTED = "#898781"
GRID = "#e1e0d9"; BASE = "#c3c2b7"; CRITICAL = "#d03b3b"; NAT = "#898781"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "sans-serif", "text.color": INK,
    "axes.edgecolor": BASE, "axes.labelcolor": SECOND, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 11,
})

def style(ax):
    ax.grid(axis="x", visible=False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(length=0)
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))

def arr(v):
    return np.array([np.nan if x is None else x for x in v], dtype=float)

def save(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=144, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path}")

def end_label(ax, x, y, text, color):
    ax.annotate(text, (x, y), xytext=(6, 0), textcoords="offset points",
                va="center", color=color, fontsize=10, fontweight="bold")

compare = json.load(open("data/compare.json"))
days = [date.fromisoformat(d) for d in compare["days"]]
summaries = {c["slug"]: json.load(open(f"data/{c['slug']}/summary.json")) for c in CITIES}

# ---- compare: diesel price history --------------------------------------
fig, ax = plt.subplots(figsize=(9.5, 4.6))
ax.plot(days, arr(compare["nat_series"]["Gazole"]), color=NAT, lw=1.6, ls=(0, (4, 3)),
        label="France (mean of ~9,600 stations)")
ends = []
for c in CITIES:
    s = summaries[c["slug"]]
    y = arr(s["series"]["loc"]["Gazole"])
    ax.plot(days, y, color=c["color"], lw=2, label=c["name"])
    ends.append([y[~np.isnan(y)][-1], c["name"], c["color"]])
# dodge the end labels: all three cities finish within a centime of each other
ends.sort(reverse=True)
for i in range(1, len(ends)):
    ends[i][0] = min(ends[i][0], ends[i - 1][0] - 0.035)
for yy, name, color in ends:
    end_label(ax, days[-1], yy, name, color)
ax.axhline(CEILING["Gazole"], color=BASE, lw=1, ls=":")
ax.annotate("TotalEnergies ceiling 2,250 €", (days[240], CEILING["Gazole"]),
            xytext=(0, 5), textcoords="offset points", color=MUTED, fontsize=9)
ax.set_title("Diesel, mean price within 15 km of each centre  (€/L)", loc="left", pad=12)
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.margins(x=0.01)
ax.set_xlim(days[0], days[-1] + (days[-1] - days[0]) / 9)
style(ax)
save(fig, "outputs/compare/figures/diesel_history.png")

# ---- compare: share of diesel stations at the ceiling --------------------
fig, ax = plt.subplots(figsize=(9.5, 4.2))
first = True
for c in CITIES:
    dd, pct, natpct = [], [], []
    for r in csv.DictReader(open(f"data/{c['slug']}/capshare.csv")):
        if r["fuel"] != "Gazole":
            continue
        d = date.fromisoformat(r["day"])
        if d < days[0]:
            continue
        dd.append(d)
        pct.append(100 * int(r["loc_cap"]) / max(1, int(r["loc_n"])))
        natpct.append(100 * int(r["nat_cap"]) / max(1, int(r["nat_n"])))
    if first:
        ax.plot(dd, natpct, color=NAT, lw=1.6, ls=(0, (4, 3)), label="France")
        first = False
    ax.plot(dd, pct, color=c["color"], lw=2, label=c["name"])
    end_label(ax, dd[-1], pct[-1], f"{pct[-1]:.0f}%", c["color"])
ax.set_title("Diesel stations posting exactly 2,250 €  (% of stations reporting within 30 days)",
             loc="left", pad=12)
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.margins(x=0.01)
style(ax)
save(fig, "outputs/compare/figures/ceiling_share.png")

# ---- compare: dry share, small multiples ---------------------------------
fig, axes = plt.subplots(1, 3, figsize=(9.5, 3.4), sharey=True)
ymax = max(max(x for x in summaries[c["slug"]]["series"]["dry_pct"] if x) for c in CITIES)
for ax, c in zip(axes, CITIES):
    s = summaries[c["slug"]]
    y = arr(s["series"]["dry_pct"])
    ax.fill_between(days, 0, np.nan_to_num(y), color=c["color"], alpha=0.25, lw=0)
    ax.plot(days, y, color=c["color"], lw=1.8)
    ax.set_title(c["name"], loc="left", fontsize=11)
    ax.set_ylim(0, ymax * 1.15)
    ax.text(0.97, 0.9, f"{s['dry_pct_now']:.1f}% now", transform=ax.transAxes,
            ha="right", color=c["color"], fontsize=10, fontweight="bold")
    style(ax)
    loc = mdates.AutoDateLocator(minticks=3, maxticks=5)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
fig.suptitle("Station-fuel pairs flagged out of stock  (% of pairs active in the archive)",
             x=0.005, ha="left", fontsize=12)
fig.tight_layout(rect=(0, 0, 1, 0.94))
save(fig, "outputs/compare/figures/dry_share.png")

# ---- locator map ----------------------------------------------------------
geo = json.load(open("data/geo/france.geojson"))
fig, ax = plt.subplots(figsize=(6.2, 6.2))
def rings_of(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [p[0] for p in geom["coordinates"]]
    return []
feats = geo["features"] if geo.get("type") == "FeatureCollection" else [geo]
for ft in feats:
    for ring in rings_of(ft["geometry"]):
        xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
        ax.fill(xs, ys, color="#f0efec", zorder=1)
        ax.plot(xs, ys, color=BASE, lw=0.7, zorder=2)
for c in CITIES:
    ax.plot(c["lon"], c["lat"], "o", color=c["color"], ms=10,
            mec=SURFACE, mew=1.5, zorder=3)
    ax.annotate(c["name"], (c["lon"], c["lat"]), xytext=(8, 4),
                textcoords="offset points", fontsize=11, color=INK, zorder=4)
ax.set_xlim(-5.5, 10); ax.set_ylim(41, 51.5)
ax.set_aspect(1 / math.cos(math.radians(46.2)))
ax.axis("off")
ax.set_title("The three cities", loc="left", pad=10)
save(fig, "outputs/compare/figures/locator_map.png")

# ---- per city -------------------------------------------------------------
for c in CITIES:
    s = summaries[c["slug"]]

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
    for ax, fuel, label in zip(axes, ("Gazole", "E10"), ("Diesel (Gazole)", "Petrol (E10)")):
        y = arr(s["series"]["loc"][fuel])
        ax.plot(days, arr(compare["nat_series"][fuel]), color=NAT, lw=1.4,
                ls=(0, (4, 3)), label="France")
        ax.plot(days, y, color=c["color"], lw=2, label=c["name"])
        if fuel in CEILING:
            ax.axhline(CEILING[fuel], color=BASE, lw=1, ls=":")
        ax.set_title(f"{label}  (€/L)", loc="left", fontsize=11)
        ax.legend(frameon=False, fontsize=8, loc="upper left")
        style(ax)
    fig.tight_layout()
    save(fig, f"outputs/{c['slug']}/figures/prices.png")

    # station map in km east/north of the centre
    kx = 111.32 * math.cos(math.radians(c["lat"]))
    fig, ax = plt.subplots(figsize=(6.8, 6.8))
    groups = {"cap": [], "diesel": [], "none": [], "dry": []}
    for p in s["points"]:
        x = (p["lon"] - c["lon"]) * kx
        y = (p["lat"] - c["lat"]) * 110.57
        k = ("dry" if p["dry_diesel"] else
             "cap" if p["at_cap"] else
             "diesel" if p["gazole"] else "none")
        groups[k].append((x, y))
    for k, spec in (("none", dict(marker="o", mfc="none", mec=BASE, ms=5, mew=1,
                                  label="no diesel reported")),
                    ("diesel", dict(marker="o", color=MUTED, ms=6,
                                    label="diesel above the ceiling")),
                    ("cap", dict(marker="o", color="#2a78d6", ms=8, mec=SURFACE, mew=1,
                                 label="diesel at 2,250 €")),
                    ("dry", dict(marker="x", color=CRITICAL, ms=8, mew=2.2,
                                 label="diesel dry (flagged ≤ 30 d)"))):
        if groups[k]:
            xs, ys = zip(*groups[k])
            ax.plot(xs, ys, ls="none", **spec)
    for r_km in (5, 10, 15):
        ax.add_patch(plt.Circle((0, 0), r_km, fill=False, color=GRID, lw=1, ls=(0, (3, 3))))
        ax.annotate(f"{r_km} km", (0, r_km), xytext=(0, 3), textcoords="offset points",
                    ha="center", color=MUTED, fontsize=8)
    ax.plot(0, 0, marker="*", color=INK, ms=13)
    ax.annotate(c["name"], (0, 0), xytext=(8, -12), textcoords="offset points",
                fontsize=10, color=INK, fontweight="bold")
    ax.set_xlim(-16.5, 16.5); ax.set_ylim(-16.5, 16.5)
    ax.set_aspect("equal"); ax.axis("off")
    ax.legend(loc="upper left", fontsize=9, numpoints=1, frameon=True,
              facecolor=SURFACE, edgecolor="none", framealpha=0.9)
    ax.set_title(f"Stations within 15 km — snapshot {s['end']}", loc="left", pad=10)
    save(fig, f"outputs/{c['slug']}/figures/stations_map.png")
