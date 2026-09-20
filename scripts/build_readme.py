#!/usr/bin/env python3
"""Assemble README.md from data/compare.json and data/<slug>/summary.json.

Every figure link carries ?v=<md5[:8]> of the PNG so GitHub's image cache
never serves a stale build.
"""
import hashlib, json
from datetime import date
from cities import CITIES

def v(path):
    h = hashlib.md5(open(path, "rb").read()).hexdigest()[:8]
    return f"{path}?v={h}"

def eur(x, nd=3):
    return f"{x:.{nd}f} €" if x is not None else "—"

def sign(x):
    if x is None:
        return "—"
    return f"{x:+.3f}"

def ville(s):
    return s.title() if s.isupper() else s

compare = json.load(open("data/compare.json"))
summaries = {c["slug"]: json.load(open(f"data/{c['slug']}/summary.json")) for c in CITIES}
end = compare["end"]
today = date.today().isoformat()

L = []
add = L.append

add(f"""# Benzinetudes — the French fuel squeeze, city by city

**Three places, one feed, one method. Diesel at every station within 15 km of
each centre, against the mean of all ~9,600 French stations, with
TotalEnergies' price ceilings and the out-of-stock flags that precede them.**

The data is the French government's `prix-carburants` open feed. Since March
2026 it shows a squeeze: diesel jumped half a euro a litre inside that month,
TotalEnergies holds a hard 2,250 € ceiling wherever the market runs above it,
and the count of pumps flagged dry keeps rising. This report tracks how that
plays out in three settings — {", ".join(f"{c['name']} ({c['blurb']})" for c in CITIES)}.

Zurich is absent because Switzerland publishes no station-level fuel-price
open data; no Swiss city can be built from public feeds.

Everything below is regenerated from the feed by `make report` — no number is
transcribed by hand. Data current through **{end}**, built {today}; the annual
archive's observations stop at {compare['archive_end']}, so the newest point in
each series is carried forward (see [Reading the data](#reading-the-data)).
A sibling of [climatudes](https://github.com/seninp/climatudes), which applies
the same one-method-many-cities idea to weather records.

[Method](#reading-the-data) · [Data sources](#data-sources) ·
[How to run](#how-to-run) · [Licence](#licence)

## The three cities, side by side

![Map of France with the three cities marked]({v('outputs/compare/figures/locator_map.png')})
""")

add("| City | Stations (15 km) | Diesel €/L | vs France | 30 days | 12 months | At 2,250 € (30-day archive) | Fuel-pairs dry | Nearest 2,250 € pump |")
add("|---|---:|---:|---:|---:|---:|---:|---:|---|")
for c in compare["cities"]:
    cap = c["capshares"].get("Gazole", {})
    near = c["nearest_cap"]
    near_s = f"{near['km']:.1f} km ({ville(near['ville'])})" if near else "none posting"
    add(f"| [{c['name']}](#{c['slug']}) | {c['n_stations']} | **{c['diesel']:.3f}** "
        f"| {c['diesel'] - compare['nat_diesel']:+.3f} | {sign(c['d30'])} | {sign(c['d365'])} "
        f"| {cap.get('loc_pct', 0):.1f}% ({cap.get('loc_cap', 0)}/{cap.get('loc_n', 0)}) "
        f"| {c['dry_now']} ({c['dry_pct_now']:.1f}%) | {near_s} |")
add(f"""
<sub>France mean diesel on {end}: **{compare['nat_diesel']:.3f} €/L**. "Fuel-pairs
dry" counts station-fuel combinations flagged out of stock, under the rule used
throughout: an outage counts while it is open and for at most 30 days after it
began. The share is against pairs active in the price archive.</sub>

![Diesel price history for the three cities against the French mean]({v('outputs/compare/figures/diesel_history.png')})

The ceiling is TotalEnergies'. It appeared on 8 April 2026, vanished in June
when the market fell below it, and has bound again since early September. How
much of a city sits on it depends on how many TotalEnergies stations the
radius holds:

![Share of diesel stations posting exactly the ceiling price, by city]({v('outputs/compare/figures/ceiling_share.png')})

The dry count moves days ahead of the visible price story. Its all-time peak,
in early April 2026, came two days before the ceiling first appeared:

![Share of station-fuel pairs flagged out of stock, by city]({v('outputs/compare/figures/dry_share.png')})
""")

for c in CITIES:
    s = summaries[c["slug"]]
    cap = s["capshares"].get("Gazole", {})
    near = s["nearest_cap"]
    add(f"""<a id="{c['slug']}"></a>
## {s['name']}

{s['n_stations']} stations lie within 15 km of {s['name']} ({c['blurb']});
{s['n_now']} appear in the current snapshot. Diesel stands at
**{s['diesel']:.3f} €/L** against a French mean of {s['diesel_nat']:.3f} —
{sign(s['d30'])} over 30 days, {sign(s['d365'])} over a year.
{cap.get('loc_pct', 0):.1f}% of its diesel stations posted exactly 2,250 €
within the last 30 days, and {s['dry_now']} station-fuel pairs
({s['dry_pct_now']:.1f}% of those active) are flagged dry.""")
    if near:
        add(f"The nearest pump posting the 2,250 € ceiling right now is "
            f"{near['km']:.1f} km away ({near['adresse'].title()}, {ville(near['ville'])}).")
    add(f"""
![{s['name']}: diesel and E10 price history against the French mean]({v(f"outputs/{c['slug']}/figures/prices.png")})

![{s['name']}: map of stations within 15 km]({v(f"outputs/{c['slug']}/figures/stations_map.png")})

The twelve nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry,
so a dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |""")
    add("|---:|---|---|---:|---:|---:|---|")
    for r in s["table"]:
        p = r["prices"]
        cells = []
        for f in ("Gazole", "E10", "SP98"):
            x = p[f]
            cells.append("—" if x is None else
                         (f"**{x:.3f}**" if abs(x - (2.25 if f == "Gazole" else 1.99)) < 1e-9
                          else f"{x:.3f}"))
        dry = ", ".join(r["dry"]) if r["dry"] else ""
        add(f"| {r['dist']:.2f} | {r['brand'] or '?'} | {r['adresse'].title()}, {ville(r['ville'])} "
            f"| {cells[0]} | {cells[1]} | {cells[2]} | {dry} |")
    add("\n<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, "
        "petrol 1.990 €). Brand `?` — no OSM match within 250 m; a trailing `?` — "
        "two stations share one OSM feature.</sub>\n")

add(f"""## Reading the data

Five properties of this feed are invisible in the files themselves and easy
to get wrong:

1. **No brand field exists anywhere** — not in the annual archives, not in the
   instant feed. Brands here come from OpenStreetMap (`amenity=fuel` via
   Overpass), matched by position within 250 m. OSM's own `brand`, `operator`
   and `name` tags disagree, so the pipeline takes the first *recognised* one.
2. **A missing price means "not reported", never "not sold".** Capped stations
   report per fuel intermittently and always come back at exactly the ceiling.
   Any snapshot-based ceiling share is therefore a lower bound; the 30-day
   archive share used above is the better estimate.
3. **Out-of-stock flags exist only in the annual archive.** The instant feed
   carries zero `rupture` elements by schema, the annual files over 178,000. A
   flag with a start and no end is an open outage — but ancient open ones mean
   "stopped selling that fuel", which is why only flags at most 30 days old
   count as dry.
4. **The dry series revises backwards.** Outage flags and their end dates land
   in the archive one to two days late, so the last days of every dry-count
   chart are provisional and can move either way on the next build.
5. **The annual archive lags the build, and its last day is partial.** The
   newest point in every price series is each station's last posted price
   carried forward, not a day that was measured. The snapshot tables and the
   nearest-ceiling-pump lines come from the instant feed and are current.

Method: a station's last posted price each day is carried forward until its
next update and stops counting 30 days later, so closed sites leave the mean
instead of freezing in it. A day enters a mean only where at least 3 stations
report. Series start {compare['start']}; before that the archive's own
coverage is still ramping and would show up as a fake price move.

## Data sources

| Source | Contents |
|---|---|
| `donnees.roulez-eco.fr/opendata/annee/<year>` | every price update of the year, station by station, with outage flags |
| `donnees.roulez-eco.fr/opendata/instantane` | the current price at every station, no outage flags |
| OpenStreetMap via Overpass | station brands, matched by position |
| `tile.openstreetmap.org` | the basemap under each station map, desaturated and cached locally |
| `france-geojson` (Grégoire David) | France and its departments on the locator map |

## How to run

    make fetch    # download the two annual archives (~300 MB unzipped each) + instant feed
    make report   # parse, aggregate, draw figures, rewrite README.md

The figures need matplotlib and Pillow (`make venv` creates `.venv` with both);
the parsers run on the system Python with the standard library alone.

## Project layout

    Makefile              fetch / report / venv
    scripts/cities.py     the city list and shared constants
    scripts/*_multi.py    one-pass parsers over the country-wide files
    scripts/build_data.py CSVs -> per-city summary.json
    scripts/figures.py    all PNGs under outputs/
    scripts/tiles.py      OSM basemap tiles for the station maps
    scripts/build_readme.py  regenerates this README.md
    data/<city>/          per-city aggregates (tracked; raw XML is not)
    data/geo/tiles/       tile cache, gitignored — only the first build downloads
    work/                 raw downloads, gitignored

## Licence

Price data: Ministère de l'Économie, [Licence Ouverte v2.0 (Etalab)](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
Brands and basemap: © OpenStreetMap contributors — data under ODbL, tiles from
openstreetmap.org under its [tile usage policy](https://operations.osmfoundation.org/policies/tiles/).
Code: MIT.
""")

open("README.md", "w").write("\n".join(L))
print(f"wrote README.md (data through {end})")
