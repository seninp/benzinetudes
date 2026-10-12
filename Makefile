# Benzinetudes — fetch the prix-carburants open data, rebuild the whole report.
#
#   make           fetch + report under the lock benzine's remote.sh also takes
#   make castanet  the Castanet deep-dive from work/report_data.json (sent by benzine)
#
# One annual archive per year from 2025 to the current one. The current year's
# archive may not exist yet in early January; parse then builds without it.
THIS   := $(shell date +%Y)
YEARS  := $(shell seq 2025 $$(($(THIS) - 1))) \
          $(if $(wildcard work/PrixCarburants_annuel_$(THIS).xml),$(THIS))
ANNUAL := $(YEARS:%=work/PrixCarburants_annuel_%.xml)
INST   := work/PrixCarburants_instantane.xml
PY     := PYTHONPATH=scripts python3
VPY    := PYTHONPATH=scripts .venv/bin/python
LOCK   := /tmp/fuel-pipeline.lock

# benzine and benzinetudes once crashed together on a malformed daily row when
# both ran on this host at the same time, though each passed alone.
# Two sub-makes, so report sees the YEARS that fetch produced.
# flock exists on poptiplex, not on the Mac; without it the run is unlocked.
refresh:
	if command -v flock >/dev/null; then \
	  flock -w 3600 $(LOCK) sh -c '$(MAKE) fetch && $(MAKE) report'; \
	else $(MAKE) fetch && $(MAKE) report; fi

report: parse osm summary figures readme

fetch:
	mkdir -p work data/geo
	for y in $$(seq 2025 $$(($(THIS) - 1))); do \
	  curl -fsS -o work/annuel_$$y.zip https://donnees.roulez-eco.fr/opendata/annee/$$y \
	  && (cd work && unzip -oq annuel_$$y.zip) || exit 1; done
	if curl -fsS -o work/annuel_$(THIS).zip https://donnees.roulez-eco.fr/opendata/annee/$(THIS) \
	   && (cd work && unzip -oq annuel_$(THIS).zip); then :; else \
	  echo "no $(THIS) archive yet; building from earlier years" >&2; \
	  rm -f work/annuel_$(THIS).zip work/PrixCarburants_annuel_$(THIS).xml; fi
	curl -fsS -o work/instantane.zip https://donnees.roulez-eco.fr/opendata/instantane
	cd work && unzip -oq instantane.zip
	test -s data/geo/france.geojson || curl -fsS -o data/geo/france.geojson \
	  https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/metropole.geojson
	test -s data/geo/departements.geojson || curl -fsS -o data/geo/departements.geojson \
	  https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson

parse:
	$(PY) scripts/extract.py $(ANNUAL) $(INST)
	for y in $(YEARS); do \
	  $(PY) scripts/dump_daily.py work/PrixCarburants_annuel_$$y.xml work/d$$y.csv || exit 1; done
	cat $(YEARS:%=work/d%.csv) | LC_ALL=C sort -t, -k1,1 -k2,2 -k3,3 > work/daily_all.csv
	$(PY) scripts/agg.py work/daily_all.csv
	$(PY) scripts/capshare.py work/daily_all.csv
	$(PY) scripts/ruptures.py $(ANNUAL)
	$(PY) scripts/snapshot.py $(INST)

osm:
	$(PY) scripts/osm_all.py

summary:
	$(PY) scripts/build_data.py

figures:
	$(VPY) scripts/figures.py

readme:
	$(PY) scripts/build_readme.py

castanet:
	@test -s work/report_data.json || { echo "no work/report_data.json: run make castanet in benzine" >&2; exit 1; }
	$(VPY) scripts/castanet_md.py work/report_data.json castanet

venv:
	python3 -m venv .venv && .venv/bin/pip install -q matplotlib

# report's steps read one another's files; never run them in parallel
.NOTPARALLEL:
.PHONY: refresh report fetch parse osm summary figures readme castanet venv
