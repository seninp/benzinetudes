# Benzinetudes — the French fuel squeeze, city by city

**Three places, one feed, one method. Diesel at every station within 15 km of
each centre, against the mean of all ~9,600 French stations, with
TotalEnergies' price ceilings and the out-of-stock flags that precede them.**

The data is the French government's `prix-carburants` open feed. Since March
2026 it shows a squeeze: diesel jumped half a euro a litre inside that month,
TotalEnergies holds a hard 2,250 € ceiling wherever the market runs above it,
and the count of pumps flagged dry keeps rising. This report tracks how that
plays out in three settings — Castanet-Tolosan (a small commune south-east of Toulouse), Lyon (France's second urban area), Gentilly (just south of the Paris périphérique; the radius covers most of Paris).

Zurich is absent because Switzerland publishes no station-level fuel-price
open data; no Swiss city can be built from public feeds.

Everything below is regenerated from the feed by `make report` — no number is
transcribed by hand. Data current through **2026-10-12**, built 2026-10-12; the annual
archive's observations stop at 2026-10-11, so the newest point in
each series is carried forward (see [Reading the data](#reading-the-data)).
A sibling of [climatudes](https://github.com/seninp/climatudes), which applies
the same one-method-many-cities idea to weather records.

[Method](#reading-the-data) · [Data sources](#data-sources) ·
[How to run](#how-to-run) · [Licence](#licence)

## The three cities, side by side

![Map of France with the three cities marked](outputs/compare/figures/locator_map.png?v=ac6e033e)

| City | Stations (15 km) | Diesel €/L | vs France | 30 days | 12 months | At 2,250 € (30-day archive) | Fuel-pairs dry | Nearest 2,250 € pump |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| [Castanet-Tolosan](#castanet) | 110 | **2.325** | -0.023 | +0.029 | +0.698 | 28.4% (19/67) | 78 (29.2%) | 3.2 km (Ramonville Saint Agne) |
| [Lyon](#lyon) | 238 | **2.361** | +0.013 | +0.024 | +0.719 | 27.9% (34/122) | 71 (15.9%) | 2.5 km (Lyon) |
| [Gentilly](#gentilly) | 660 | **2.378** | +0.030 | +0.024 | +0.658 | 39.8% (100/251) | 137 (15.5%) | 1.2 km (Paris) |

<sub>France mean diesel on 2026-10-12: **2.348 €/L**. "Fuel-pairs
dry" counts station-fuel combinations flagged out of stock, under the rule used
throughout: an outage counts while it is open and for at most 30 days after it
began. The share is against pairs active in the price archive.</sub>

![Diesel price history for the three cities against the French mean](outputs/compare/figures/diesel_history.png?v=1afc9e8a)

The ceiling is TotalEnergies'. It appeared on 8 April 2026, vanished in June
when the market fell below it, and has bound again since early September. How
much of a city sits on it depends on how many TotalEnergies stations the
radius holds:

![Share of diesel stations posting exactly the ceiling price, by city](outputs/compare/figures/ceiling_share.png?v=ee385d9a)

The dry count moves ahead of the visible price story. The dry share peaked in every city on 6 April 2026 (Castanet-Tolosan 32.2%, Lyon 21.7%, Gentilly 30.2%), two days before the ceiling first appeared:

![Share of station-fuel pairs flagged out of stock, by city](outputs/compare/figures/dry_share.png?v=d231b5da)

<a id="castanet"></a>
## Castanet-Tolosan

110 stations lie within 15 km of Castanet-Tolosan (a small commune south-east of Toulouse);
71 appear in the current snapshot. Diesel stands at
**2.325 €/L** against a French mean of 2.348 —
+0.029 over 30 days, +0.698 over a year.
28.4% of its diesel stations posted exactly 2,250 €
within the last 30 days, and 78 station-fuel pairs
(29.2% of those active) are flagged dry.
The nearest pump posting the 2,250 € ceiling right now is 3.2 km away (98 Avenue Tolosane, Ramonville Saint Agne).

![Castanet-Tolosan: diesel and E10 price history against the French mean](outputs/castanet/figures/prices.png?v=1b97d530)

![Castanet-Tolosan: map of stations within 15 km](outputs/castanet/figures/stations_map.png?v=966f8e2d)

The twelve nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry,
so a dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|
| 1.11 | Intermarché | Route De Labège, Castanet-Tolosan | 2.299 | 2.149 | 2.289 |  |
| 2.57 | Intermarché | Avenue De Lauragais - Lieu Dit Condamine, Pompertuzat | 2.309 | 2.159 | 2.289 |  |
| 2.80 | Intermarché | 1 Rue Louis Braille, Ramonville-Saint-Agne | 2.289 | 2.139 | 2.269 |  |
| 3.17 | TotalEnergies | 98 Avenue Tolosane, Ramonville Saint Agne | **2.250** | **1.990** | — | SP98, E85 |
| 3.27 | TotalEnergies | Centre Commercial De L'Autan, Labege | — | — | — | Gazole, SP95 |
| 3.89 | Carrefour | Centre Commercial Labege 2, LABèGE | 2.385 | 2.196 | 2.315 |  |
| 4.17 | Avia | 53 Av. Tolosane, Ramonville-Saint-Agne | 2.419 | 2.259 | 2.359 |  |
| 4.63 | Super U | Za De La Balme, Belberaud | 2.278 | 2.139 | 2.268 |  |
| 5.09 | TotalEnergies | 5 Av De Gameville, Saint-Orens-de-Gameville | — | — | — | Gazole, SP98, E10, E85 |
| 5.34 | Dyneff? | Autoroute A61Aire De Toulouse Sud Nord, Deyme | 2.496 | 2.280 | 2.344 |  |
| 5.35 | Dyneff | Autoroute A61Aire De Toulouse Sud Sud, Deyme | 2.466 | 2.250 | 2.314 |  |
| 5.65 | E.Leclerc | Allée Des Champs Pinsons, Saint-Orens-De-Gameville | 2.299 | 2.196 | 2.289 |  |

<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, petrol 1.990 €). Brand `?` — no OSM match within 250 m; a trailing `?` — two stations share one OSM feature.</sub>

<a id="lyon"></a>
## Lyon

238 stations lie within 15 km of Lyon (France's second urban area);
125 appear in the current snapshot. Diesel stands at
**2.361 €/L** against a French mean of 2.348 —
+0.024 over 30 days, +0.719 over a year.
27.9% of its diesel stations posted exactly 2,250 €
within the last 30 days, and 71 station-fuel pairs
(15.9% of those active) are flagged dry.
The nearest pump posting the 2,250 € ceiling right now is 2.5 km away (100 Avenue Barthelemy Buyer, Lyon).

![Lyon: diesel and E10 price history against the French mean](outputs/lyon/figures/prices.png?v=8433da62)

![Lyon: map of stations within 15 km](outputs/lyon/figures/stations_map.png?v=699f4c24)

The twelve nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry,
so a dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|
| 1.70 | Avia | 258 Rue Garibaldi, Lyon | 2.449 | 2.269 | — |  |
| 1.76 | Esso Express | 22 Rue Philippe De Lassalle, Lyon | 2.336 | 2.158 | 2.279 |  |
| 1.77 | Eni | 97 Rue Denfert Rochereau, Lyon | 2.499 | 2.274 | 2.374 |  |
| 2.44 | Esso | 87-89 Bd Stalingrad, Villeurbanne | 2.439 | 2.269 | 2.439 |  |
| 2.55 | Esso | 47 Cours Emile Zola, Villeurbanne | 2.479 | 2.289 | 2.469 |  |
| 2.55 | Total Access | 100 Avenue Barthelemy Buyer, Lyon | **2.250** | **1.990** | **1.990** | E85 |
| 2.64 | Eni | 55 Bis Quai Gillet, Lyon | 2.499 | 2.279 | 2.379 |  |
| 2.69 | TotalEnergies | 34 Rue Pasteur, Caluire-Et-Cuire | — | — | — | Gazole, SP98, E10 |
| 3.08 | Avia | 65 Cours Albert Thomas, Lyon | 2.449 | 2.269 | — |  |
| 3.14 | Avia | 44 Avenue Leclerc, Lyon 7 | 2.439 | — | 2.339 |  |
| 3.21 | Esso | 72 Cours Tolstoi, Villeurbanne | 2.459 | 2.269 | 2.449 |  |
| 3.21 | Esso | 110 Bd Du 11 Novembre 1918, Villeurbanne | 2.459 | 2.269 | 2.439 |  |

<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, petrol 1.990 €). Brand `?` — no OSM match within 250 m; a trailing `?` — two stations share one OSM feature.</sub>

<a id="gentilly"></a>
## Gentilly

660 stations lie within 15 km of Gentilly (just south of the Paris périphérique; the radius covers most of Paris);
263 appear in the current snapshot. Diesel stands at
**2.378 €/L** against a French mean of 2.348 —
+0.024 over 30 days, +0.658 over a year.
39.8% of its diesel stations posted exactly 2,250 €
within the last 30 days, and 137 station-fuel pairs
(15.5% of those active) are flagged dry.
The nearest pump posting the 2,250 € ceiling right now is 1.2 km away (27 Avenue De La Porte D'Italie, Paris).

![Gentilly: diesel and E10 price history against the French mean](outputs/gentilly/figures/prices.png?v=fba59e99)

![Gentilly: map of stations within 15 km](outputs/gentilly/figures/stations_map.png?v=4faa20d7)

The twelve nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry,
so a dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|
| 0.27 | Esso Express | 67 Avenue Raspail, Gentilly | 2.444 | 2.258 | 2.338 |  |
| 0.89 | Esso | 23 Avenue Paul Doumer, Arcueil | 2.529 | 2.319 | 2.499 |  |
| 0.92 | ? | 70-74 Av Aristide Briand, Montrouge | 2.589 | 2.459 | 2.629 |  |
| 1.21 | TotalEnergies | 27 Avenue De La Porte D'Italie, Paris | **2.250** | **1.990** | — | SP98 |
| 1.36 | Avia | 91 Avenue Aristide Briand, Montrouge | 2.599 | 2.469 | 2.549 |  |
| 1.41 | Esso | 20 Avenue Paul Vaillant-Couturier, Arcueil | 2.341 | 2.195 | 2.275 |  |
| 1.41 | Esso | 231 Rue De Tolbiac, Paris | 2.499 | 2.299 | 2.439 |  |
| 1.47 | E.Leclerc | Avenue De Fontainebleau, LE KREMLIN-BICêTRE | 2.435 | 2.249 | 2.349 |  |
| 1.76 | TotalEnergies | 89 Av A. Briand, Arcueil | — | — | — | Gazole, SP95, E10 |
| 2.21 | ? | Rue Legion Etrangere, Paris | — | **1.990** | **1.990** |  |
| 2.34 | Total Access | 181, Boulevard Vincent Auriol, Paris | **2.250** | — | — | SP98, E10 |
| 2.46 | TotalEnergies | 168-180 Bld De Stalingrad, Ivry-sur-Seine | **2.250** | — | — | SP98, E10, E85 |

<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, petrol 1.990 €). Brand `?` — no OSM match within 250 m; a trailing `?` — two stations share one OSM feature.</sub>

## Reading the data

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
report. Series start 2025-01-15; before that the archive's own
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

    make           # fetch + every report below, under a lock
    make fetch     # download one annual archive per year since 2025 + the instant feed
    make report    # parse, aggregate, draw figures, rewrite README.md
    make dashboard # dashboard/benzine-prices.html, the interactive Castanet dashboard
    make castanet  # castanet/README.md, from the dashboard's report_data.json
    make publish   # from a second checkout: rsync sources to the build host,
                   # build, commit and push there, then reset here to the pushed commit

The figures need matplotlib and Pillow (`make venv` creates `.venv` with both);
the parsers and the dashboard run on the system Python with the standard library alone.

## Project layout

    Makefile              refresh / fetch / report / dashboard / castanet / publish
    scripts/config.py     every constant: cities, dates, ceilings, brand groups
    scripts/common.py     daily-row reader, carry-forward, dry count, distance
    scripts/extract.py, dump_daily.py, agg.py, capshare.py, ruptures.py, snapshot.py
                          one-pass parsers over the country-wide files
    scripts/osm_all.py, fetch_osm.py, brands.py
                          OSM brands, matched to stations by position
    scripts/build_data.py CSVs -> per-city summary.json
    scripts/style.py      palette and plotting helpers
    scripts/figures.py    all PNGs under outputs/
    scripts/castanet_md.py castanet/README.md, the single-city deep-dive
    castanet/             that deep-dive and its figures
    scripts/tiles.py      OSM basemap tiles for the station maps
    scripts/build_readme.py  regenerates this README.md
    dashboard/            the single-city HTML dashboard and its own scripts and data
    data/<city>/          per-city aggregates (tracked; raw XML is not)
    data/geo/tiles/       tile cache, gitignored — only the first build downloads
    work/                 raw downloads, gitignored

## Licence

Price data: Ministère de l'Économie, [Licence Ouverte v2.0 (Etalab)](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
Brands and basemap: © OpenStreetMap contributors — data under ODbL, tiles from
openstreetmap.org under its [tile usage policy](https://operations.osmfoundation.org/policies/tiles/).
Code: MIT.
