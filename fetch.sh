#!/bin/sh
# Pull the French fuel-price open data and rebuild the report.
# The archives are ~300 MB unzipped each, so the heavy parsing runs on poptiplex.
set -e
HOST=psenin@192.168.10.51
REMOTE=benzine

ssh $HOST "mkdir -p ~/$REMOTE"
scp scripts/*.py $HOST:$REMOTE/

ssh $HOST "cd ~/$REMOTE && \
  for y in 2025 2026; do curl -sS -o PrixCarburants_annuel_\$y.zip https://donnees.roulez-eco.fr/opendata/annee/\$y; done && \
  curl -sS -o PrixCarburants_instantane.zip https://donnees.roulez-eco.fr/opendata/instantane && \
  unzip -oq 'PrixCarburants_*.zip' && \
  python3 extract.py PrixCarburants_annuel_2025.xml st_2025.csv px_2025.csv && \
  python3 extract.py PrixCarburants_annuel_2026.xml st_2026.csv px_2026.csv && \
  python3 extract.py PrixCarburants_instantane.xml st_now.csv px_now.csv && \
  python3 -c \"
import csv
rows={}
for f in ('st_2025.csv','st_2026.csv','st_now.csv'):
    for r in csv.DictReader(open(f)): rows[r['id']]=r
w=csv.DictWriter(open('st_all.csv','w',newline=''),fieldnames=list(next(iter(rows.values())).keys()))
w.writeheader()
for r in sorted(rows.values(), key=lambda r: float(r['dist_km'])): w.writerow(r)
\" && \
  python3 dump_daily.py PrixCarburants_annuel_2025.xml d2025.csv && \
  python3 dump_daily.py PrixCarburants_annuel_2026.xml d2026.csv && \
  cat d2025.csv d2026.csv | LC_ALL=C sort -t, -k1,1 -k2,2 -k3,3 > daily_all.csv && \
  python3 agg.py daily_all.csv st_all.csv nat_daily.csv loc_daily.csv && \
  python3 snapshot.py && \
  python3 capshare.py daily_all.csv st_all.csv capshare.csv && \
  python3 ceilings_now.py PrixCarburants_instantane.xml ceilings_now.csv && \
  python3 ruptures.py st_all.csv ruptures.csv rupture_hist.csv \
    PrixCarburants_annuel_2025.xml PrixCarburants_annuel_2026.xml && \
  python3 fetch_osm.py osm_fuel.json"

for f in nat_daily.csv loc_daily.csv stations_now.csv st_all.csv capshare.csv \
         ceilings_now.csv ruptures.csv rupture_hist.csv osm_fuel.json \
         px_2025.csv px_2026.csv archive_end.txt; do
  scp -q $HOST:$REMOTE/$f data/
done

python3 scripts/brands.py data/osm_fuel.json data/stations_now.csv data/brands.csv
# Both of these read the per-station price history, so they need brands.csv (for the
# capped/uncapped split) and must run before build_report.py consumes their output.
python3 scripts/trend.py data/brands.csv data/archive_end.txt data/trend_split.csv \
  data/px_2025.csv data/px_2026.csv
python3 scripts/weekday.py data/px_2025.csv data/px_2026.csv data/archive_end.txt \
  data/weekday_dev.csv data/weekday_upd.csv
python3 build_report.py
python3 -c "
h=open('report_template.html').read(); d=open('data/report_data.json').read()
open('benzine-prices.html','w').write(h.replace('/*__DATA__*/', d))
print('wrote benzine-prices.html')"
