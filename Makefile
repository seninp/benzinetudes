# Benzinetudes — fetch the prix-carburants open data, rebuild the whole report.
A2025 := work/PrixCarburants_annuel_2025.xml
A2026 := work/PrixCarburants_annuel_2026.xml
INST  := work/PrixCarburants_instantane.xml
PY    := PYTHONPATH=scripts python3
VPY   := PYTHONPATH=scripts .venv/bin/python

report: parse osm summary figures readme

fetch:
	mkdir -p work data/geo
	for y in 2025 2026; do \
	  curl -sS -o work/annuel_$$y.zip https://donnees.roulez-eco.fr/opendata/annee/$$y; done
	curl -sS -o work/instantane.zip https://donnees.roulez-eco.fr/opendata/instantane
	cd work && unzip -oq 'annuel_2025.zip' && unzip -oq 'annuel_2026.zip' && unzip -oq 'instantane.zip'
	test -s data/geo/france.geojson || curl -sS -o data/geo/france.geojson \
	  https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/metropole.geojson
	test -s data/geo/departements.geojson || curl -sS -o data/geo/departements.geojson \
	  https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson

parse:
	$(PY) scripts/extract_multi.py $(A2025) $(A2026) $(INST)
	python3 scripts/dump_daily.py $(A2025) work/d2025.csv
	python3 scripts/dump_daily.py $(A2026) work/d2026.csv
	cat work/d2025.csv work/d2026.csv | LC_ALL=C sort -t, -k1,1 -k2,2 -k3,3 > work/daily_all.csv
	$(PY) scripts/agg_multi.py work/daily_all.csv
	$(PY) scripts/capshare_multi.py work/daily_all.csv
	$(PY) scripts/ruptures_multi.py $(A2025) $(A2026)
	$(PY) scripts/snapshot_multi.py $(INST)

osm:
	$(PY) scripts/osm_all.py

summary:
	$(PY) scripts/build_data.py

figures:
	$(VPY) scripts/figures.py

readme:
	$(PY) scripts/build_readme.py

venv:
	python3 -m venv .venv && .venv/bin/pip install -q matplotlib

.PHONY: report fetch parse osm summary figures readme venv
