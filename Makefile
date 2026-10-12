# Benzinetudes — fetch the prix-carburants open data, rebuild every report.
#
# Builds run on poptiplex (matplotlib lives in its .venv); edit on the Mac and
#   make publish   rsync the sources to poptiplex, build there, commit, push,
#                  then bring this checkout up to the pushed commit
# On poptiplex:
#   make           fetch + everything below, under a lock
#   make report    the three-city README and figures
#   make dashboard dashboard/benzine-prices.html, the Castanet dashboard
#   make castanet  castanet/README.md, from dashboard/data/report_data.json
# Off the LAN, `make fetch dashboard` builds the dashboard on the Mac (no
# matplotlib needed); `make dashboard-html` rebuilds its HTML from data alone.
#
# One annual archive per year from 2025 to the current one. The current year's
# archive may not exist yet in early January; the build then goes without it.
THIS   := $(shell date +%Y)
YEARS  := $(shell seq 2025 $$(($(THIS) - 1))) \
          $(if $(wildcard work/PrixCarburants_annuel_$(THIS).xml),$(THIS))
ANNUAL := $(YEARS:%=PrixCarburants_annuel_%.xml)
INST   := PrixCarburants_instantane.xml
PY     := PYTHONPATH=scripts python3
VPY    := PYTHONPATH=scripts .venv/bin/python
# dashboard scripts run inside dashboard/ or work/dashboard/, shared ones from scripts/
DPY    := PYTHONPATH=$(CURDIR)/scripts python3
DS     := $(CURDIR)/dashboard/scripts
DW     := work/dashboard
LOCK   := /tmp/fuel-pipeline.lock
HOST   := psenin@192.168.10.51
RDIR   := git/benzinetudes
# what publish copies to poptiplex; everything else there is built on it.
# Each directory is mirrored on its own: rsync -R --delete would also delete
# every sibling of a copied directory, dashboard/data among them.
SRCDIRS  := scripts dashboard/scripts dashboard/tools
SRCFILES := Makefile .gitignore dashboard/report_template.html dashboard/README.md
BUILT  := README.md data outputs castanet dashboard/data dashboard/benzine-prices.html
# the dashboard parsers' products that its HTML step reads; px_<year>.csv come too
DPRODUCTS := nat_daily.csv loc_daily.csv stations_now.csv st_all.csv capshare.csv \
             ceilings_now.csv ruptures.csv rupture_hist.csv archive_end.txt

# The lock keeps two runs on one host from overlapping (two pipelines once
# crashed together on a malformed daily row; each passed alone). flock exists
# on poptiplex, not on the Mac; without it the run is unlocked. Two sub-makes,
# so the build sees the YEARS that fetch produced.
refresh:
	if command -v flock >/dev/null; then \
	  flock -w 3600 $(LOCK) sh -c '$(MAKE) fetch && $(MAKE) build'; \
	else $(MAKE) fetch && $(MAKE) build; fi

build: report dashboard castanet

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

# whole-country daily rows, read by both reports
daily:
	for y in $(YEARS); do \
	  $(PY) scripts/dump_daily.py work/PrixCarburants_annuel_$$y.xml work/d$$y.csv || exit 1; done
	cat $(YEARS:%=work/d%.csv) | LC_ALL=C sort -t, -k1,1 -k2,2 -k3,3 > work/daily_all.csv

parse: daily
	$(PY) scripts/extract.py $(ANNUAL:%=work/%) work/$(INST)
	$(PY) scripts/agg.py work/daily_all.csv
	$(PY) scripts/capshare.py work/daily_all.csv
	$(PY) scripts/ruptures.py $(ANNUAL:%=work/%)
	$(PY) scripts/snapshot.py work/$(INST)

osm:
	$(PY) scripts/osm_all.py

summary:
	$(PY) scripts/build_data.py

figures:
	$(VPY) scripts/figures.py

readme:
	$(PY) scripts/build_readme.py

dashboard: dashboard-parse dashboard-html

dashboard-parse: daily
	mkdir -p $(DW)
	cd $(DW) && for y in $(YEARS); do \
	  $(DPY) $(DS)/extract.py ../PrixCarburants_annuel_$$y.xml st_$$y.csv px_$$y.csv || exit 1; done
	cd $(DW) && $(DPY) $(DS)/extract.py ../$(INST) st_now.csv px_now.csv
	cd $(DW) && $(DPY) $(DS)/merge_stations.py st_all.csv $(YEARS:%=st_%.csv) st_now.csv
	cd $(DW) && $(DPY) $(DS)/agg.py ../daily_all.csv st_all.csv nat_daily.csv loc_daily.csv
	cd $(DW) && $(DPY) $(DS)/snapshot.py st_all.csv ../$(INST) stations_now.csv
	cd $(DW) && $(DPY) $(DS)/capshare.py ../daily_all.csv st_all.csv capshare.csv
	cd $(DW) && $(DPY) $(DS)/ceilings_now.py ../$(INST) ceilings_now.csv
	cd $(DW) && $(DPY) $(DS)/ruptures.py st_all.csv ruptures.csv rupture_hist.csv $(ANNUAL:%=../%)
	cd $(DW) && cp $(DPRODUCTS) $(YEARS:%=px_%.csv) $(CURDIR)/dashboard/data/
	# keeps the cached answer when every Overpass mirror fails
	$(DPY) scripts/fetch_osm.py dashboard/data/osm_fuel.json

dashboard-html:
	cd dashboard && $(DPY) ../scripts/brands.py data/osm_fuel.json data/stations_now.csv data/brands.csv
	# trend and weekday read the per-station price history and need brands.csv
	cd dashboard && $(DPY) scripts/trend.py data/brands.csv data/archive_end.txt \
	  data/trend_split.csv data/px_20*.csv
	cd dashboard && $(DPY) scripts/weekday.py data/px_20*.csv data/archive_end.txt \
	  data/weekday_dev.csv data/weekday_upd.csv
	cd dashboard && $(DPY) scripts/build_report.py
	cd dashboard && $(DPY) scripts/render_html.py report_template.html data/report_data.json \
	  benzine-prices.html

castanet:
	$(VPY) scripts/castanet_md.py dashboard/data/report_data.json castanet

venv:
	python3 -m venv .venv && .venv/bin/pip install -q matplotlib

# --- run on the Mac ----------------------------------------------------------
# MSG names the commit; the default is the daily data-refresh message.
publish:
	rsync -aR $(SRCFILES) $(HOST):$(RDIR)/
	for d in $(SRCDIRS); do \
	  rsync -a --delete --exclude __pycache__ $$d/ $(HOST):$(RDIR)/$$d/ || exit 1; done
	ssh $(HOST) 'cd $(RDIR) && make && make push MSG="$(MSG)"'
	git fetch -q origin
	git reset -q origin/main
	git checkout -- $(BUILT)
	git status --short

# --- run on poptiplex, by publish --------------------------------------------
push:
	git add -A
	git diff --cached --quiet || git commit -qm \
	  "$${MSG:-Refresh data through $$(cat data/archive_end.txt) (built $$(date +%F))}"
	git push -q

# the steps read one another's files; never run them in parallel
.NOTPARALLEL:
.PHONY: refresh build report fetch daily parse osm summary figures readme dashboard \
        dashboard-parse dashboard-html castanet venv publish push
