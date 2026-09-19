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
transcribed by hand. Data current through **2026-09-19**, built 2026-09-19.
A sibling of [climatudes](https://github.com/seninp/climatudes), which applies
the same one-method-many-cities idea to weather records.

[Method](#reading-the-data) · [Data sources](#data-sources) ·
[How to run](#how-to-run) · [Licence](#licence)

## The three cities, side by side

![Map of France with the three cities marked](outputs/compare/figures/locator_map.png?v=ac6e033e)

| City | Stations (15 km) | Diesel €/L | vs France | 30 days | 12 months | At 2,250 € (30-day archive) | Fuel-pairs dry | Nearest 2,250 € pump |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| [Castanet-Tolosan](#castanet) | 109 | **2.378** | -0.017 | +0.129 | +0.738 | 33.8% (24/71) | 69 (24.9%) | 5.1 km (Saint-Orens-de-Gameville) |
| [Lyon](#lyon) | 237 | **2.408** | +0.013 | +0.139 | +0.752 | 27.6% (34/123) | 40 (9.0%) | 2.5 km (Lyon) |
| [Gentilly](#gentilly) | 659 | **2.405** | +0.010 | +0.125 | +0.672 | 40.0% (100/250) | 73 (8.2%) | 1.2 km (Paris) |

<sub>France mean diesel on 2026-09-19: **2.395 €/L**. "Fuel-pairs
dry" counts station-fuel combinations flagged out of stock, under the rule used
throughout: an outage counts while it is open and for at most 30 days after it
began. The share is against pairs active in the price archive.</sub>

![Diesel price history for the three cities against the French mean](outputs/compare/figures/diesel_history.png?v=5cde1f52)

The ceiling is TotalEnergies'. It appeared on 8 April 2026, vanished in June
when the market fell below it, and has bound again since early September. How
much of a city sits on it depends on how many TotalEnergies stations the
radius holds:

![Share of diesel stations posting exactly the ceiling price, by city](outputs/compare/figures/ceiling_share.png?v=cd8bed37)

The dry count moves days ahead of the visible price story. Its all-time peak,
in early April 2026, came two days before the ceiling first appeared:

![Share of station-fuel pairs flagged out of stock, by city](outputs/compare/figures/dry_share.png?v=c5af75ba)

<a id="castanet"></a>
## Castanet-Tolosan

109 stations lie within 15 km of Castanet-Tolosan (a small commune south-east of Toulouse);
71 appear in the current snapshot. Diesel stands at
**2.378 €/L** against a French mean of 2.395 —
+0.129 over 30 days, +0.738 over a year.
33.8% of its diesel stations posted exactly 2,250 €
within the last 30 days, and 69 station-fuel pairs
(24.9% of those active) are flagged dry.
The nearest pump posting the 2,250 € ceiling right now is 5.1 km away (5 Av De Gameville, Saint-Orens-de-Gameville).

![Castanet-Tolosan: diesel and E10 price history against the French mean](outputs/castanet/figures/prices.png?v=8b861aef)

![Castanet-Tolosan: map of stations within 15 km](outputs/castanet/figures/stations_map.png?v=2680b549)

The twelve nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry,
so a dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|
| 1.11 | Intermarché | Route De Labège, Castanet-Tolosan | 2.429 | 2.139 | 2.269 |  |
| 2.57 | Intermarché | Avenue De Lauragais - Lieu Dit Condamine, Pompertuzat | 2.399 | 2.169 | 2.319 |  |
| 2.80 | Intermarché | 1 Rue Louis Braille, Ramonville-Saint-Agne | 2.429 | 2.139 | 2.269 |  |
| 3.17 | TotalEnergies | 98 Avenue Tolosane, Ramonville Saint Agne | — | — | — | Gazole, SP98, E10 |
| 3.27 | TotalEnergies | Centre Commercial De L'Autan, Labege | — | — | — | Gazole, SP95, E10 |
| 3.89 | Carrefour | Centre Commercial Labege 2, LABèGE | 2.463 | 2.181 | 2.297 |  |
| 4.17 | Avia | 53 Av. Tolosane, Ramonville-Saint-Agne | 2.419 | 2.219 | 2.319 |  |
| 4.63 | Super U | Za De La Balme, Belberaud | 2.388 | 2.138 | 2.258 |  |
| 5.09 | TotalEnergies | 5 Av De Gameville, Saint-Orens-de-Gameville | **2.250** | — | **1.990** | Gazole, SP98, E10, E85 |
| 5.34 | Dyneff? | Autoroute A61Aire De Toulouse Sud Nord, Deyme | 2.431 | 2.250 | 2.313 |  |
| 5.35 | Dyneff | Autoroute A61Aire De Toulouse Sud Sud, Deyme | 2.439 | 2.220 | 2.283 |  |
| 5.65 | E.Leclerc | Allée Des Champs Pinsons, Saint-Orens-De-Gameville | 2.439 | 2.181 | 2.269 |  |

<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, petrol 1.990 €). Brand `?` — no OSM match within 250 m; a trailing `?` — two stations share one OSM feature.</sub>

<a id="lyon"></a>
## Lyon

237 stations lie within 15 km of Lyon (France's second urban area);
125 appear in the current snapshot. Diesel stands at
**2.408 €/L** against a French mean of 2.395 —
+0.139 over 30 days, +0.752 over a year.
27.6% of its diesel stations posted exactly 2,250 €
within the last 30 days, and 40 station-fuel pairs
(9.0% of those active) are flagged dry.
The nearest pump posting the 2,250 € ceiling right now is 2.5 km away (100 Avenue Barthelemy Buyer, Lyon).

![Lyon: diesel and E10 price history against the French mean](outputs/lyon/figures/prices.png?v=ad9d1f9b)

![Lyon: map of stations within 15 km](outputs/lyon/figures/stations_map.png?v=7bfb1005)

The twelve nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry,
so a dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|
| 1.70 | Avia | 258 Rue Garibaldi, Lyon | 2.509 | 2.269 | — |  |
| 1.76 | Esso Express | 22 Rue Philippe De Lassalle, Lyon | 2.422 | 2.145 | 2.255 |  |
| 1.77 | Eni | 97 Rue Denfert Rochereau, Lyon | 2.549 | 2.274 | 2.374 |  |
| 2.44 | Esso | 87-89 Bd Stalingrad, Villeurbanne | 2.539 | 2.359 | 2.529 |  |
| 2.55 | Esso | 47 Cours Emile Zola, Villeurbanne | 2.589 | 2.369 | 2.549 |  |
| 2.55 | Total Access | 100 Avenue Barthelemy Buyer, Lyon | **2.250** | **1.990** | — | SP98 |
| 2.64 | Eni | 55 Bis Quai Gillet, Lyon | 2.549 | 2.279 | 2.379 |  |
| 2.69 | TotalEnergies | 34 Rue Pasteur, Caluire-Et-Cuire | **2.250** | — | — | SP98, E10 |
| 3.08 | Avia | 65 Cours Albert Thomas, Lyon | 2.509 | 2.269 | — |  |
| 3.14 | Avia | 44 Avenue Leclerc, Lyon 7 | 2.499 | — | 2.339 |  |
| 3.21 | Esso | 72 Cours Tolstoi, Villeurbanne | 2.569 | 2.299 | 2.479 |  |
| 3.21 | Esso | 110 Bd Du 11 Novembre 1918, Villeurbanne | 2.539 | 2.289 | 2.459 |  |

<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, petrol 1.990 €). Brand `?` — no OSM match within 250 m; a trailing `?` — two stations share one OSM feature.</sub>

<a id="gentilly"></a>
## Gentilly

659 stations lie within 15 km of Gentilly (just south of the Paris périphérique; the radius covers most of Paris);
263 appear in the current snapshot. Diesel stands at
**2.405 €/L** against a French mean of 2.395 —
+0.125 over 30 days, +0.672 over a year.
40.0% of its diesel stations posted exactly 2,250 €
within the last 30 days, and 73 station-fuel pairs
(8.2% of those active) are flagged dry.
The nearest pump posting the 2,250 € ceiling right now is 1.2 km away (27 Avenue De La Porte D'Italie, Paris).

![Gentilly: diesel and E10 price history against the French mean](outputs/gentilly/figures/prices.png?v=fe0730ca)

![Gentilly: map of stations within 15 km](outputs/gentilly/figures/stations_map.png?v=0ab033d4)

The twelve nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry,
so a dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|
| 0.27 | Esso Express | 67 Avenue Raspail, Gentilly | 2.468 | 2.238 | 2.318 |  |
| 0.89 | Esso | 23 Avenue Paul Doumer, Arcueil | 2.609 | 2.369 | 2.549 |  |
| 0.92 | ? | 70-74 Av Aristide Briand, Montrouge | 2.569 | 2.469 | 2.639 |  |
| 1.21 | TotalEnergies | 27 Avenue De La Porte D'Italie, Paris | **2.250** | **1.990** | — | SP98, GPLc |
| 1.36 | Avia | 91 Avenue Aristide Briand, Montrouge | 2.549 | 2.429 | 2.499 |  |
| 1.41 | Esso | 20 Avenue Paul Vaillant-Couturier, Arcueil | 2.425 | 2.214 | 2.294 |  |
| 1.41 | Esso | 231 Rue De Tolbiac, Paris | 2.499 | 2.359 | 2.499 |  |
| 1.47 | E.Leclerc | Avenue De Fontainebleau, LE KREMLIN-BICêTRE | 2.459 | 2.229 | 2.299 |  |
| 1.76 | TotalEnergies | 89 Av A. Briand, Arcueil | **2.250** | **1.990** | — | Gazole, E10 |
| 2.21 | ? | Rue Legion Etrangere, Paris | — | — | — |  |
| 2.34 | Total Access | 181, Boulevard Vincent Auriol, Paris | **2.250** | **1.990** | — |  |
| 2.46 | TotalEnergies | 168-180 Bld De Stalingrad, Ivry-sur-Seine | **2.250** | **1.990** | **1.990** |  |

<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, petrol 1.990 €). Brand `?` — no OSM match within 250 m; a trailing `?` — two stations share one OSM feature.</sub>

## Reading the data

Four properties of this feed are invisible in the files themselves and easy
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
4. **The dry series revises backwards.** Outage flags land in the archive one
   to two days late, so the last days of every dry-count chart are provisional
   and tend to move up on the next build.

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
