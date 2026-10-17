# Benzinetudes — handoff

Last session: 2026-10-12. Published as `7eabf8e` on github.com/seninp/benzinetudes.
Nothing mid-operation; the Mac checkout equals `origin/main`.

## What this is

Two reports built from the French `prix-carburants` open data, in one repo:

- `README.md` — the three-city report (Castanet-Tolosan, Lyon, Gentilly).
- `dashboard/benzine-prices.html` — the interactive Castanet dashboard (v1.11).
- `castanet/README.md` — the dashboard as static Markdown, for GitHub.

## Where it lives

| Machine | Path | Role |
|---|---|---|
| Mac | `~/git/benzine` | edit sources here, uncommitted |
| poptiplex `psenin@192.168.10.51` | `~/git/benzinetudes` | builds, commits, pushes; matplotlib in `.venv` |

## How to rebuild

    make publish                 # on the Mac
    make publish MSG="..."       # same, with a commit message (multi-line is safe)

Publish refuses to run unless the Mac is on `main`, `HEAD` equals `origin/main`,
and the built files are untouched. It rsyncs the sources, runs `make release` on
poptiplex (fetch, build, commit, push under `/tmp/fuel-pipeline.lock`), then
resets the Mac to the pushed commit. A full run takes about 5 minutes.

Off the LAN, `make fetch dashboard` builds the dashboard on the Mac; the
three-city figures need poptiplex.

## Layout since 2026-10-12

One parse feeds both reports. `scripts/` parses the archives into `data/` and
`data/<city>/`; the dashboard reads Castanet's aggregates, brands and outages
from `data/castanet/` and parses only its own price posts (`dashboard/data/px_*.csv`)
and the instant feed's ceiling shares. Every constant lives in `scripts/config.py`.
Both reports count dry pumps with `common.dry_series`.

## Baseline, build of 2026-10-12 (archive observed through 2026-10-11)

| | Castanet | Lyon | Gentilly |
|---|---|---|---|
| Stations within 15 km | 110 | 238 | 660 |
| Diesel €/L | 2.325 | 2.361 | 2.378 |
| vs French mean 2.348 | −0.023 | +0.013 | +0.030 |
| 30 days / 12 months | +0.029 / +0.698 | +0.024 / +0.719 | +0.024 / +0.658 |
| Diesel at 2,250 € (30-day archive) | 28.4 % (19/67) | 27.9 % (34/122) | 39.8 % (100/251) |
| Fuel pairs dry | 78 (29.2 %) | 71 (15.9 %) | 137 (15.5 %) |
| Nearest 2,250 € pump | 3.2 km | 2.6 km | 1.2 km |

France: 22.5 % of diesel stations at the ceiling in the 30-day archive.
Dashboard: 6 of 53 local diesel posts at 2,250 €, none flagged dry; 17 stations
with a diesel outage open since 12 Sept; dry table 63 (56 a day earlier, 61 a
week earlier), all local stations 77.

## Changes on 2026-10-12

- Merged benzine into this repo as `dashboard/`, history kept.
- Removed the dashboard's twin parsers (`agg`, `capshare`, `ruptures`,
  `snapshot`, `merge_stations`) and their duplicated outputs.
- `cities.py` → `config.py`; the dashboard's own `config.py` is gone. The README
  formats the radius and the ceiling from it.
- The three-city dry series now ends on the archive's last observed day. Before,
  the forward-filled day divided by a carried station count (Castanet 29.4 % →
  29.2 %, Gentilly 15.6 % → 15.5 %).
- Brand patterns match whole words; `eleclerc` added, because `fold()` drops the
  dot and a whole-word `leclerc` stopped matching two stations.
- Castanet's OSM cache now holds the 2026-10-12 answer the dashboard used, so
  Rocade Purpan (31300008) reads TotalEnergies in both reports.
- `fetch_osm.py` refuses an Overpass answer from an older database than the
  cache; a mirror on a 2026-07-15 base had reverted 23 tags.
- Makefile: fetch fails unless the missing year is January's; publish preflight;
  the commit message travels as a file.
- Guards: example station missing from the instant feed, an empty brand group
  in `trend.py`, a short day series in `castanet_md.py`.

## How the restructure was checked

Sources rsynced to a scratch directory on poptiplex, same archives, `make build`,
every file compared by blob hash with the previous commit. The dashboard HTML,
`report_data.json` and `castanet/README.md` came out byte-identical. Every other
difference was one of the intended changes above.

## Open

- **Critic findings not fixed.** `build_report.py` mixes `END` and `OBS_END`;
  the three-city and dashboard Castanet sets differ (110 archive stations
  against 71 in the instant feed, a one-pair gap in the dry count: 78 against
  77); `ceilings_now.py` adds SP95 to the caps; publish's rsync runs outside the
  lock; `build_report` crashes if a brand group has no price on the last day;
  `castanet_md.py` assumes seven weekday rows; `build_readme` prints
  `dry_pct_now` unguarded.
- The README still hardcodes "~9,600 French stations".
- `~/benzine` on poptiplex (the pre-merge work directory) was deleted on
  2026-10-12, along with the three one-off scripts it held.

## Pitfalls

- Files under `BUILT` are never rsynced. A built file that should disappear
  must be deleted on poptiplex by hand before publish.
- Never `rsync -R --delete`: it deletes the siblings of every copied directory.
- Never run two pipelines on poptiplex at once; the flock serialises them.
- `overpass.osm.ch` is Switzerland-only and returns an empty answer for
  Toulouse.
- Read `data/archive_end.txt` to know where observations stop; the last day of
  every series is forward-filled.
