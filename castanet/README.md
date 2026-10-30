# Benzine — Castanet-Tolosan, in depth

**Diesel and petrol at every station within 15 km of
Castanet-Tolosan (31320), against the mean of all ~9,300
French stations. The deep-dive companion to the three-city
[benzinetudes](../README.md) report — same feed, same method, one place, more
of it: the brand split under TotalEnergies' price ceiling, the day-of-week
effect, and the out-of-stock count that runs ahead of the price.**

The data is the French government's `prix-carburants` open feed. Every number
below is regenerated from it — none is typed by hand. Every series runs to
**2026-10-29**, the last day the annual archive observed; built
2026-10-30 (see [Reading the data](#reading-the-data)). The snapshot tables come
from the instant feed and are current.

## Where prices stand

| Fuel | Castanet €/L | France | 30 days | 12 months | Stations |
|---|---:|---:|---:|---:|---:|
| Diesel (Gazole) | **2.369** | 2.380 | +0.005 | +0.711 | 67 |
| Petrol E10 (SP95-E10) | **2.091** | 2.109 | -0.052 | +0.395 | 63 |
| Petrol SP98 | **2.167** | 2.202 | -0.050 | +0.377 | 62 |
| Superethanol E85 | **0.928** | 0.908 | +0.011 | +0.194 | 45 |

<sub>Snapshot of 64 priced stations on 2026-10-30; 12 updated that day, median age 1 day. A fuel enters a mean only where at least 3 stations report.</sub>

![Diesel and E10: Castanet against the French mean](fig/prices.png?v=d1a986c8)

Diesel sits at **2.369 €/L**, 0.011
below the French mean and 0.711 higher
than a year ago. Much of that rise landed in one month: 35
centimes in March 2026 alone, 49% of the twelve-month move. The local
line has tracked the national one within a centime or two throughout. Over the
last 28 days local diesel has been flat within the noise (+0.4 ¢/week).

## The ceiling splits the field

On **8 April 2026** TotalEnergies set a hard **2.250 €/L** ceiling on diesel
(and **1.990 €** on petrol). The day before, 2% of
local diesel stations sat exactly on that price; the day after,
22%. It slackened when the market fell below it in
the summer — on 2026-07-01 only 0.1% of French
stations were at the cap — and has bound again since early September. Over the
last 30 days of the archive **29.9%** of local diesel
stations posted exactly 2.250 €, against 22.4% nationally.

Averaging the whole area hides what the ceiling does, because it acts on only
some brands. The 17 Total-group stations within 15 km are pinned to
it and cannot follow the market up; the 50 others are free.

![Diesel within 15 km, Total-group against every other brand](fig/split.png?v=204228ae)

The two groups now stand **15.9 centimes** apart — Total-group at
2.250, everyone else at 2.409 — after moving
together for a year (on 2026-03-01 the Total-group stations were the *dearer* ones, by 5.7 ¢). The maxima are the proof that
2.250 € is a cap and not a price they all chose: no Total-group station has posted above it since 2026-07-22 (it was over on 2 of 653 days, the last on 2026-07-21), while the free
brands' dearest diesel reached 2.499 €/L.

The nearest pump on the ceiling and not flagged dry is
**8.1 km** away (43 Route D Espagne, Portet sur Garonne); filling there instead of at Intermarché in Castanet (2.369) saves about 0.12 €/L.

## Which day to fill

Two questions, two answers. First, is any weekday reliably cheaper? Pooled over
every week, Monday looks cheapest and Sunday dearest — but that is the trend
leaking in, not a habit. Split the weeks by their own direction and the shape
flips: in weeks diesel rose, Monday is well below the week's mean and the weekend
above it; in weeks it fell, exactly the reverse, by almost the same amount. The
two cancel. There is **no dependable cheap day** to shop for.

![Weekday effect: the cheapest-day illusion, and when changes land](fig/weekday.png?v=8e786737)

Second, *when do prices move?* Rises cluster on **Tuesday**: 61% of its
789 changes were increases, averaging +0.49 ¢.
That shifts *when* a price moves more than what the week costs, so the
practical rule stays the station, not the day: the gap between pumps is many
times the whole weekday effect.

## The dry count runs ahead

An out-of-stock flag appears in the annual archive before the price story turns.
The count of station-fuel pairs flagged dry within 15 km peaked at **85** on
**6 April 2026** — two days before the 2.250 € ceiling appeared — then
fell back. It sits at 41 now.

![Out-of-stock flags within 15 km, over time](fig/dry.png?v=ea49d40b)

Read the tail with care: outage flags and their end dates land in the archive a
day or two late, so the last few days of this line are provisional and revise
both ways on the next build.

## The nearest stations

The fourteen nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry, so a
dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|
| 1.11 | Intermarché | Route De Labège, Castanet-Tolosan | 2.369 | 2.049 | 2.179 |  |
| 2.57 | Intermarché | Avenue De Lauragais - Lieu Dit Condamine, Pompertuzat | 2.399 | 2.069 | 2.194 |  |
| 2.80 | Intermarché | 1 Rue Louis Braille, Ramonville-Saint-Agne | 2.369 | 2.049 | 2.179 |  |
| 3.17 | TotalEnergies | 98 Avenue Tolosane, Ramonville Saint Agne | — | — | — | E10, Gazole, SP98 |
| 3.27 | TotalEnergies | Centre Commercial De L'Autan, Labege | — | — | — |  |
| 3.89 | Carrefour | Centre Commercial Labege 2, Labège | 2.400 | 2.128 | 2.239 |  |
| 4.17 | Avia | 53 Av. Tolosane, Ramonville-Saint-Agne | 2.459 | 2.239 | 2.339 |  |
| 4.63 | Super U | Za De La Balme, Belberaud | 2.358 | 2.034 | 2.158 |  |
| 5.09 | TotalEnergies | 5 Av De Gameville, Saint-Orens-de-Gameville | — | — | — | E10, Gazole, SP98 |
| 5.34 | Dyneff? | Autoroute A61Aire De Toulouse Sud Nord, Deyme | 2.492 | 2.256 | 2.329 |  |
| 5.35 | Dyneff | Autoroute A61Aire De Toulouse Sud Sud, Deyme | 2.462 | 2.226 | 2.299 |  |
| 5.65 | E.Leclerc | Allée Des Champs Pinsons, Saint-Orens-de-Gameville | 2.399 | 2.128 | 2.239 |  |
| 6.46 | Esso Express | 105 Route De Narbonne, Toulouse | 2.438 | 2.138 | 2.238 |  |
| 6.60 | Esso | 68 Route De Revel, Toulouse | 2.439 | 2.199 | 2.279 |  |

<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2.250 €, petrol 1.990 €). Brand `?` — two stations share one OSM feature.</sub>

## By brand

Diesel across the brands that OSM could name, within 15 km:

| Brand | Stations | Cheapest | Median | Dearest |
|---|---:|---:|---:|---:|
| Total Access *(at the ceiling)* | 3 | 2.250 | 2.250 | 2.250 |
| TotalEnergies *(at the ceiling)* | 2 | 2.250 | 2.250 | 2.250 |
| Super U | 3 | 2.335 | 2.358 | 2.399 |
| Carrefour | 6 | 2.369 | 2.394 | 2.420 |
| E.Leclerc | 2 | 2.389 | 2.394 | 2.399 |
| Intermarché | 9 | 2.369 | 2.399 | 2.499 |
| Carrefour Market | 2 | 2.389 | 2.406 | 2.424 |
| Auchan | 2 | 2.389 | 2.419 | 2.449 |
| Esso | 6 | 2.384 | 2.420 | 2.442 |
| Avia | 6 | 2.439 | 2.439 | 2.479 |
| Esso Express | 4 | 2.250 | 2.447 | 2.467 |
| Carrefour Contact | 1 | 2.459 | 2.459 | 2.459 |
| Dyneff | 3 | 2.439 | 2.462 | 2.492 |

## Reading the data

Five properties of this feed are invisible in the files themselves:

1. **No brand field exists** — not in the annual archives, not in the instant
   feed. Brands come from OpenStreetMap (`amenity=fuel` via Overpass), matched by
   position within 250 m, for every station the archive lists here, old ids
   included; an unmatched station is counted as "other" in the split.
2. **A missing price means "not reported", never "not sold".** Capped stations
   report per fuel intermittently and always return at exactly the ceiling, so
   any snapshot ceiling share is a lower bound; the 30-day archive share is the
   better estimate.
3. **Out-of-stock flags exist only in the annual archive.** The instant feed
   carries none. A flag with a start and no end is an open outage — but ancient
   open ones mean "stopped selling that fuel", so only flags at most 30 days old
   count as dry.
4. **The dry series revises backwards.** Flags and their end dates land a day or
   two late; the last days of the dry chart are provisional.
5. **The archive lags the build and its last day is partial.** Every series
   stops on the archive's last day, which misses whatever was posted after the
   evening's publication.

Method: a station's last posted price each day is carried forward until its next
update and stops counting 30 days later, so closed sites leave the mean instead
of freezing in it. A day enters a mean only where at least 3 stations report.
Series start 2025-01-15; before that the archive's own coverage is still
ramping and would show as a fake price move. The weekday deviation compares each
day against the same station's own weekly mean, and clusters its error by
calendar week — station-weeks are not independent, since every local station
sees the same national move at once.

## Data sources

| Source | Contents |
|---|---|
| `donnees.roulez-eco.fr/opendata/annee/<year>` | every price update of the year, with outage flags |
| `donnees.roulez-eco.fr/opendata/instantane` | the current price at every station, no outage flags |
| OpenStreetMap via Overpass | station brands, matched by position |

## Licence

Price data: Ministère de l'Économie, [Licence Ouverte v2.0 (Etalab)](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
Brands: © OpenStreetMap contributors, under ODbL. Code: MIT.
