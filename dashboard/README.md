# benzine — fuel prices around Castanet-Tolosan (31320)

Pulls the official French fuel-price open data and builds `benzine-prices.html`,
a dated report of diesel and petrol prices within 15 km of Castanet-Tolosan
against the French mean.

## Running it

    make            # remote + report + castanet: the daily rebuild
    make local      # when poptiplex is unreachable: the heavy half on this Mac (~3 min)
    make report     # rebuild the HTML from data/ alone

The annual archives are ~300 MB of XML each unzipped, so `make remote` runs
`scripts/remote.sh` on **poptiplex** (`psenin@192.168.10.51`) and copies back
only the aggregated CSVs. `make local` runs the same script in `work/`. There is
one annual archive per year from 2025 on, picked up without edits. `make castanet`
sends `data/report_data.json` to the benzinetudes checkout on poptiplex and
renders its Castanet deep-dive there; commit and push happen in that repo.
`./fetch.sh` still works and calls `make`. Nothing in this pipeline touches
Sanofi infrastructure.

## Layout

    Makefile                 remote / local / report / castanet
    fetch.sh                 calls make, for the habit
    report_template.html     the dashboard, with a /*__DATA__*/ placeholder
    benzine-prices.html      the built report (open this)
    scripts/                 heavy half (remote.sh runs it on poptiplex or in work/)
      config.py              study area, dates, ceilings, brand groups
      common.py              daily-row reader, carry-forward, distance (shared with benzinetudes)
      remote.sh              download, then every step below down to fetch_osm.py
      extract.py             per-station price history within the radius
      merge_stations.py      one station list across the yearly files
      dump_daily.py          whole-country daily last-price rows
      agg.py                 forward-filled daily means, national and local
      snapshot.py            today's price at each local station
      capshare.py            daily share of stations pinned at a ceiling
      ceilings_now.py        today's ceiling shares from the instant feed
      ruptures.py            stock-outage flags: open ones, plus every interval
                             (rupture_hist.csv) for the dry-count history
      fetch_osm.py           Overpass query for OSM fuel stations
    scripts/                 report half, on the Mac
      brands.py              match stations to OSM brands
      trend.py               local means split Total-group / other brands
      weekday.py             day-of-week effect
      build_report.py        CSVs -> data/report_data.json
      render_html.py         report_data.json + template -> benzine-prices.html
    tools/snapshot_churn.py  one-off: per-fuel reporting churn between two snapshots
    data/                    every intermediate the report reads
    !backups/                HTML snapshots before each version bump

## Source

`donnees.roulez-eco.fr` (Ministry of the Economy):

| Endpoint | Contents |
|---|---|
| `/opendata/annee/<year>` | every price update of that year, station by station |
| `/opendata/instantane` | the current price at every station |

Station coordinates come as integers in units of 1e-5 degrees; prices are euros
per litre.

**Stock outages** live only in the annual archive: the instant feed carries no
`rupture` elements at all, so a station that is dry *today* still shows a plain
price (or a dash) in the snapshot. `scripts/ruptures.py` extracts the open
flags (a `debut` with no `fin`); the report marks those started within 30 days
as "dry", while older open flags mean the fuel is no longer sold and stay a
dash. Found the hard way on 2026-09-17, at a pump that had been dry since the
15th.

**Brands** are not in the official feed at all — neither annual file, nor the
instant feed, nor either dataset on `data.economie.gouv.fr`. They are recovered
from OpenStreetMap (`amenity=fuel` via Overpass) and matched to each station by
position within 250 m; 65 of the 71 stations match. OSM's own tagging disagrees
with itself — `brand`, `operator` and `name` often differ and one Total station
is tagged `brand=kai` — so `scripts/brands.py` tries all three tags and takes the
first it recognises, rather than the first that is non-empty. Where two stations
sit within ~100 m and OSM maps one feature, the further one is flagged `?`.

## Method

- Stations within 15 km great-circle of 43.5161 N, 1.5000 E.
- A station's last posted price each day is carried forward until its next
  update, and stops counting 30 days after its final update, so closed sites
  leave the average instead of freezing in it.
- A day enters a mean only where at least 3 stations report.
- Series start 2025-01-15. Before that the archive's own coverage is still
  ramping (1,876 stations on 1 January against ~9,600 in steady state), which
  would otherwise show up as a fake price move.

## Findings (data to 2026-09-13, snapshot 2026-09-17 evening)

A dated record of the first build. The current figures are in
`benzine-prices.html`, which recomputes each finding on every build.

1. Local diesel is **2,296 €/L**, up **0,664 €** in twelve months. Almost all of
   the rise happened in March 2026: 1,724 € on 1 March to 2,220 € on 31 March,
   peaking at 2,349 € on 8 April.
2. A **2,250 € ceiling** appeared on **8 April 2026**. The share of French
   stations posting *exactly* 2,250 € jumped from 1,5% to 25% in one day and the
   share below it fell to 1%. It binds only when the market runs above it: it
   disappeared in June, when diesel fell to 1,88 €, and is back today at 22% of
   French and 33% of local stations.
3. **The ceiling is TotalEnergies'.** Every Total-group station here that posts
   diesel posts exactly 2,250 €, none above and none below, and every other
   brand's median is higher. But the squeeze is emptying the snapshot: on the
   morning of 17 September 15 of the 21 Total-group stations posted diesel; by
   evening only 5 did, and the local stations on the ceiling fell from 18 to 6
   (5 Total-group, 1 unmatched in OSM). The archive share (33,8% of local
   diesel stations within 30 days) is the steadier figure.
4. **Petrol has its own ceiling, 1,990 €** — 15,7% of French stations post E10
   at exactly that price in the snapshot and 0,2% below it. The archive puts the
   reach at 23,5%; the archive is the better figure (see the caveat below).
   Every petrol price any local Total station reports is 1,990 €.
5. **A dash in the tables means "not reported", not "not sold".** Station
   31300008 (6 avenue du Goupe Morhange, Toulouse — "Rocade Purpan" in OSM,
   12,46 km) reports only diesel, E85 and LPG and flags no stock outage, yet it
   sold SP98 at 1,990 € on 2026-09-15.
6. The nearest pump is among the dearest — an Intermarché. Castanet-Tolosan
   (1,11 km) posts 2,389 €; the nearest ceiling-priced station still posting is
   now 6,62 km away in Portet-sur-Garonne — 13,9 centimes a litre less, about
   8 € a tank. The Ramonville Total (3,17 km), nearest on 14 September, has
   been dry since the 15th.
7. Local prices sit within a few centimes of the French mean, and have all year
   — 1,5 centimes below it today.
8. **The dry count tracks the squeezes.** Counting station-fuel pairs flagged
   dry in the Total/Intermarché/Super U table (33 stations, same 30-day rule
   the table uses), the 2025 baseline is ~1; the all-time peak is **69 on
   6 April 2026**, two days before the 2,250 € ceiling appeared; and the
   September squeeze took it from **12 on 10 September to 37–48 from the 11th
   on** (39 at the evening snapshot of the 17th, one fewer than in the
   morning). The history is reconstructed from every rupture interval, open or
   closed, in both annual archives (`data/rupture_hist.csv`).

### Why the two ceiling shares differ

Every ceiling share has two values. The instant feed counts what is reported
right now; the annual archive counts any station that reported within 30 days.
For diesel they nearly agree (20,0% against 22,0%); for petrol they do not
(15,7% against 23,5% for E10).

`tools/snapshot_churn.py` explains it. Between the 2026-09-14 and 2026-09-15
snapshots, 222 stations started reporting E10 and **220 of them at exactly
1,990 €**; 194 started reporting SP98, 191 at the ceiling. Diesel churns too but
on a base three times larger — 74 arrivals, 71 at the ceiling. So capped sites
drop in and out of the feed per fuel and always arrive at the ceiling. The
snapshot share is therefore a lower bound, the archive is the better estimate,
and the ceiling-share *history* is drawn for diesel only, where a 0,8% daily
churn is small enough to ignore.
