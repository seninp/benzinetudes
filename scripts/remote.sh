#!/bin/sh
# The heavy half of the pipeline: download the archives, parse, aggregate.
#
# Runs in the current directory and leaves the products there; the Makefile
# copies them into data/. It runs on poptiplex by default (`make remote`) and on
# the Mac when poptiplex is unreachable (`make local`). The XML is ~700 MB
# unzipped. SKIP_DOWNLOAD=1 reuses the archives already on disk.
#
# One annual archive per year from 2025 to the current one, so a new year is
# picked up without editing anything. The current year's archive may not exist
# yet in early January; then that year is skipped rather than failing the run.
set -eu
S=$(cd "$(dirname "$0")" && pwd)

# benzine and benzinetudes once crashed together on a malformed daily row when
# both ran on poptiplex at the same time, though each passed alone. Both take
# this lock, so one waits for the other.
if [ -z "${FUEL_LOCKED:-}" ] && command -v flock >/dev/null 2>&1; then
  FUEL_LOCKED=1 exec flock -w 3600 /tmp/fuel-pipeline.lock sh "$0" "$@"
fi

THIS=$(date +%Y)
YEARS=$(seq 2025 $((THIS - 1)))
if [ -z "${SKIP_DOWNLOAD:-}" ]; then
  for y in $YEARS; do
    curl -fsS -o PrixCarburants_annuel_$y.zip https://donnees.roulez-eco.fr/opendata/annee/$y
    unzip -oq PrixCarburants_annuel_$y.zip
  done
  if curl -fsS -o PrixCarburants_annuel_$THIS.zip https://donnees.roulez-eco.fr/opendata/annee/$THIS \
     && unzip -oq PrixCarburants_annuel_$THIS.zip; then
    :
  else
    echo "no $THIS archive yet; building from earlier years" >&2
    rm -f PrixCarburants_annuel_$THIS.zip PrixCarburants_annuel_$THIS.xml
  fi
  curl -fsS -o PrixCarburants_instantane.zip https://donnees.roulez-eco.fr/opendata/instantane
  unzip -oq PrixCarburants_instantane.zip
fi
[ -s PrixCarburants_annuel_$THIS.xml ] && YEARS="$YEARS $THIS"

ANNUAL=""
for y in $YEARS; do
  ANNUAL="$ANNUAL PrixCarburants_annuel_$y.xml"
  python3 "$S/extract.py" PrixCarburants_annuel_$y.xml st_$y.csv px_$y.csv
  python3 "$S/dump_daily.py" PrixCarburants_annuel_$y.xml d$y.csv
done
python3 "$S/extract.py" PrixCarburants_instantane.xml st_now.csv px_now.csv
# shellcheck disable=SC2046
python3 "$S/merge_stations.py" st_all.csv $(for y in $YEARS; do echo st_$y.csv; done) st_now.csv
# shellcheck disable=SC2046
cat $(for y in $YEARS; do echo d$y.csv; done) | LC_ALL=C sort -t, -k1,1 -k2,2 -k3,3 > daily_all.csv

python3 "$S/agg.py" daily_all.csv st_all.csv nat_daily.csv loc_daily.csv
python3 "$S/snapshot.py" st_all.csv PrixCarburants_instantane.xml stations_now.csv
python3 "$S/capshare.py" daily_all.csv st_all.csv capshare.csv
python3 "$S/ceilings_now.py" PrixCarburants_instantane.xml ceilings_now.csv
# shellcheck disable=SC2086
python3 "$S/ruptures.py" st_all.csv ruptures.csv rupture_hist.csv $ANNUAL
python3 "$S/fetch_osm.py" osm_fuel.json
