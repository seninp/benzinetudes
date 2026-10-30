# Benzinetudes — handoff

Last session: 2026-10-30. Data refreshed through 2026-10-29 as `9a13d66`; no
code changed. Nothing mid-operation; the Mac checkout equals `origin/main`.

## What this is

Two reports built from the French `prix-carburants` open data, in one repo:

- `README.md` — the three-city report (Castanet-Tolosan, Lyon, Gentilly).
- `dashboard/benzine-prices.html` — the interactive Castanet dashboard (v1.14).
- `castanet/README.md` — the dashboard as static Markdown, for GitHub.

## Where it lives

| Machine | Path | Role |
|---|---|---|
| Mac | `~/git/benzine` | edit sources here, uncommitted |
| poptiplex `psenin@192.168.10.51` | `~/git/benzinetudes` | builds, commits, pushes; matplotlib in `.venv` |

## Git rules

`seninp/benzinetudes` is a personal repo. The Mac never commits, pushes or
writes to GitHub for it: `gh` here is the corporate `psenin-sanofi` account, and
a write from it is visible to Sanofi security (it also fails with a 403).
Edit sources uncommitted and run `make publish`; poptiplex commits as
`seninp <seninp@gmail.com>` and pushes. A HANDOFF-only edit goes the same way.
Reads (`git fetch`) are fine.

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

## Baseline, build of 2026-10-30 (archive observed through 2026-10-29)

| | Castanet | Lyon | Gentilly |
|---|---|---|---|
| Stations within 15 km | 110 | 238 | 660 |
| Diesel €/L | 2.369 | 2.376 | 2.384 |
| vs French mean 2.380 | −0.011 | −0.004 | +0.004 |
| 30 days / 12 months | +0.005 / +0.711 | −0.018 / +0.702 | −0.015 / +0.654 |
| Diesel at 2.250 € (30-day archive) | 29.9 % (20/67) | 27.7 % (33/119) | 41.8 % (102/244) |
| Fuel pairs dry | 41 (15.7 %) | 44 (10.2 %) | 117 (13.6 %) |
| Nearest 2.250 € pump | 8.1 km | 2.5 km | 2.3 km |

Dashboard: 7 of 54 local diesel posts at 2.250 €, none flagged dry; nearest in
stock 8.1 km (Portet sur Garonne); Total group pinned to the cap since 3 Sept
(17 stations at 2.250 against 50 others at 2.409, 15.9 ¢ apart); uncapped
stations flat (+0.3 ¢/week). Local diesel over 28 days is flat within the noise
(+0.4 ¢/week) and the 14-day slope is +1.0 ¢/week, so the post-peak decline
may have ended; the local peak since the cap was 2.381 on 22 Sept. Dry table 34
(39 a day earlier, 33 a week earlier), all local stations 41 (50 a day
earlier, 40 a week earlier); peak 85 on 6 April 2026.

Against the 2026-10-23 build (archive through 10-22): Castanet diesel +2.1 ¢,
dry pairs 40 → 41, Lyon 55 → 44, Gentilly 100 → 117; the nearest capped pump
moved from 3.2 km to 8.1 km (the Ramonville pump is flagged dry again). The
tail revises, so read the dry moves as provisional.

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

## Changes on 2026-10-20

Two critics (code, and the reports as a driver reads them) found that fixed
words in the prose had drifted from the computed numbers. Fixed:

- Trend verbs follow the computed direction. The dashboard's short answer and
  section 3 title said "Rising" whatever the slope ("climbing at -2,2 centimes
  a week" on 17 Oct); `castanet/README.md` said "both are still climbing".
- `castanet/README.md` called the Total group *cheaper* before the cap (it was
  5.7 ¢ dearer), claimed no Total station ever exceeded the cap (two days did,
  last 2026-07-21), said "almost all" of the rise came in one month (48 %),
  called the 30-day share "today", and advised "fill on Monday, before
  Tuesday's rise" while arguing there is no cheap day. All computed now.
- The cap streak tolerates one Total station a few tenths under the cap
  (`config.PIN_TOL`); it read "0 days" on 17 Oct, now 46.
- The rise day ranks weekdays by the z-score of their share of increases; the
  raw share had picked Sunday (26 of 41 moves) over Tuesday (487 of 789).
  `rise_day_sig` is now a real test (z > 1.96).
- "~9,600 French stations" is computed (`compare.nat_n`), ~9,400 today.
- `dry_pct_now` guarded; `castanet_md.py` places weekday rows by `dow`; town
  names like "LABèGE" title-cased; "1 days".

Second round, the same day:

- Brands are matched for every archive station (`stations.csv`), live ones
  first so an old id never takes a brand from today's site. 39 Castanet ids
  gained a brand; no live station changed. The split moves one station, in
  2025 only.
- The dashboard's `dry_all` counts the 110 archive stations, as the
  three-city report does: 47 in both (was 46 against 47), peak 85 (was 79).
- SP95 is in `config.CEILING`; `ceilings_now.py` and `snapshot_churn.py`
  import it instead of keeping copies.
- The Markdown reports and figures write the cap with a decimal point,
  "2.250 €", like every other price. The dashboard keeps decimal commas.

Third round: every series stops on the archive's last observed day.
`agg.py` and `capshare.py` no longer write the carried-forward days up to
the build, and `build_data.py` and `build_report.py` assert that the series
end equals `archive_end.txt`. Cards, 30-day and 12-month changes, ceiling
shares and station counts were measured on the unobserved day while the
trend used the observed one. The 12-month changes moved by 0.3–0.6 ¢
(Castanet +0.739 → +0.736) and now agree with the trend section; the prose
about a carried-forward point is gone from all three outputs.

Fourth round: `make check` (`scripts/check_outputs.py`) runs last in
`make build` and fails it, so nothing is pushed, when an output contradicts
its data or another output: direction words against slopes, the cap streak,
dearer/cheaper before the cap, the rise-day claim, Castanet diesel, dry count
and dry peak across the three outputs, the French station count, comma-decimal
prices, "1 days", stale `?v=` figure hashes, and the dashboard's version meta,
pill, changelog and this file's version line. Planting nine of these defects
in a copy produced ten failures. A new fixed sentence in the prose needs a
check here, or it can drift again.

Checked in `~/bz-test` on poptiplex (same archives, `make build`, diffed
against `dab378c`): only the intended text, `weekday.png`, the HTML and
`report_data.json` changed, plus a routine Lyon OSM refresh.

## How the restructure was checked

Sources rsynced to a scratch directory on poptiplex, same archives, `make build`,
every file compared by blob hash with the previous commit. The dashboard HTML,
`report_data.json` and `castanet/README.md` came out byte-identical. Every other
difference was one of the intended changes above.

## Open

From the 2026-10-20 critics, ranked by value; none is fixed yet.

- **The three outputs disagree on counts**: Total-group stations 17 (split)
  against 21 (brands); "stations on the cap" includes non-Total ones; dry
  pairs 47 against table 40 (the table covers only Total and its rivals).
- The dashboard mixes decimal commas with comma thousands ("9,431").
- Remaining fixed prose in `castanet_md.py`: "Monday looks cheapest and Sunday
  dearest", "bound again since early September", the dry-chart annotation ("8 Apr 2026").
- Guards: an empty brand group in `build_report` split, `capped[0]` print,
  publish's rsync runs outside the lock.
- Reader ideas: lead the dashboard with the nearest 2.250 € pumps not flagged
  dry, with the age of the stock flag; put `stations_map.png` in the Castanet
  outputs; start `ceiling_share.png` at March 2026; mark the provisional tail
  of the dry charts; move the 2,000-word changelog out of the shipped HTML.
- `build_report.py` (600 lines) and `castanet_md.py` are module-level scripts;
  one function per section would make the guards testable.

## Pitfalls

- Files under `BUILT` are never rsynced. A built file that should disappear
  must be deleted on poptiplex by hand before publish.
- Never `rsync -R --delete`: it deletes the siblings of every copied directory.
- Never run two pipelines on poptiplex at once; the flock serialises them.
- `overpass.osm.ch` is Switzerland-only and returns an empty answer for
  Toulouse.
- `data/archive_end.txt` is where every series stops (since 2026-10-20 no
  carried-forward day is written). That day is partial: posts after the
  evening's publication are missing.
