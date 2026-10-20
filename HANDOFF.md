# Benzinetudes — handoff

Last session: 2026-10-20. Data refreshed as `dab378c`, then the prose fixes below
published on top. Nothing mid-operation; the Mac checkout equals `origin/main`.

## What this is

Two reports built from the French `prix-carburants` open data, in one repo:

- `README.md` — the three-city report (Castanet-Tolosan, Lyon, Gentilly).
- `dashboard/benzine-prices.html` — the interactive Castanet dashboard (v1.12).
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

## Baseline, build of 2026-10-20 (archive observed through 2026-10-19)

| | Castanet | Lyon | Gentilly |
|---|---|---|---|
| Stations within 15 km | 110 | 238 | 660 |
| Diesel €/L | 2.344 | 2.366 | 2.383 |
| vs French mean 2.361 | −0.017 | +0.005 | +0.022 |
| 30 days / 12 months | −0.033 / +0.739 | −0.042 / +0.747 | −0.026 / +0.681 |
| Diesel at 2,250 € (30-day archive) | 29.9 % (20/67) | 27.9 % (34/122) | 38.9 % (96/247) |
| Fuel pairs dry | 47 (17.9 %) | 44 (9.9 %) | 137 (15.8 %) |
| Nearest 2,250 € pump | 5.1 km | 2.6 km | 1.2 km |

France: 22.4 % of diesel stations at the ceiling in the 30-day archive.
Dashboard: 14 of 61 local diesel posts at 2,250 €, 2 of them flagged dry; nearest
in stock 6.6 km (Portet-sur-Garonne); Total group on the cap for 46 days, since
3 Sept; uncapped stations falling 1.8 ¢/week; dry table 40 (58 a day earlier, 62
a week earlier), all local stations 46. Diesel turned down after a 22 Sept peak
of 2.381.

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

- **`END` against `OBS_END`.** Cards, deltas, `cap_story.now`, archive ceiling
  shares and `meta.nat_n` read the forward-filled day; trend reads the observed
  one. Removing the filled day in `agg.py`/`capshare.py` would end the class.
  "Dry now" also counts back from different days in the two reports.
- **Brands match only the instant feed's 71 stations**, so 39 archive stations
  have no brand and count as "other"; dashboard `dry_all` uses the same 71.
  Matching `stations.csv` closes the 110 / 71 gap and the dry 78 / 77 gap.
- **SP95 is capped in the data** (9.6 % of posts at 1.990) and in the
  template's `CEIL_OF`, but missing from `config.CEILING`; `ceilings_now.py`
  and `tools/snapshot_churn.py` keep private copies.
- **The three outputs disagree on counts**: Total-group stations 17 (split)
  against 21 (brands); "stations on the cap" includes non-Total ones; dry
  pairs 47 against table 40.
- **Decimal separator**: the Markdown reports write prices "2.344 €/L" and the
  cap "2,250 €" in one sentence; the dashboard uses decimal commas with
  comma thousands ("9,431"). Needs a decision, not a fix.
- Remaining fixed prose in `castanet_md.py`: "Monday looks cheapest and Sunday
  dearest", "bound again since early September", the split-chart and dry-chart
  annotations ("2,250 € ceiling", "8 Apr 2026").
- Guards: an empty brand group in `build_report` split, `capped[0]` print,
  divisions in `ceilings_now.py:46`; publish's rsync runs outside the lock.
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
- Read `data/archive_end.txt` to know where observations stop; the last day of
  every series is forward-filled.
