# Benzinetudes — fetch the prix-carburants open data, rebuild every report.
#
# Builds run on poptiplex (matplotlib lives in its .venv). Edit on the Mac, then
#   make publish   check this checkout matches origin, rsync the sources to
#                  poptiplex, fetch + build + commit + push there under the
#                  lock, then move this checkout to the pushed commit.
#                  MSG="..." names the commit (default: the data-refresh line).
# On poptiplex:
#   make           fetch + build, under the lock, without committing
#   make report    the three-city README and figures
#   make dashboard dashboard/benzine-prices.html, the Castanet dashboard
#   make castanet  castanet/README.md, from dashboard/data/report_data.json
# Off the LAN, `make fetch && make dashboard` builds the dashboard on the Mac
# (no matplotlib needed); `make dashboard-html` rebuilds its HTML from data alone.
#
# One annual archive per year from 2025 to the current one. The current year's
# archive may not exist yet in January; the build then goes without it. YEARS is
# read once, when make starts, so fetch and the build run in separate makes.
THIS   := $(shell date +%Y)
YEARS  := $(shell seq 2025 $$(($(THIS) - 1))) \
          $(if $(wildcard work/PrixCarburants_annuel_$(THIS).xml),$(THIS))
ANNUAL := $(YEARS:%=work/PrixCarburants_annuel_%.xml)
INST   := work/PrixCarburants_instantane.xml
PY     := PYTHONPATH=scripts python3
VPY    := PYTHONPATH=scripts .venv/bin/python
# dashboard scripts run inside dashboard/, shared modules come from scripts/
DPY    := PYTHONPATH=$(CURDIR)/scripts python3
LOCK   := /tmp/fuel-pipeline.lock
HOST   := psenin@192.168.10.51
RDIR   := git/benzinetudes
# What publish copies to poptiplex; everything else there is built on it.
# Each directory is mirrored on its own: rsync -R --delete would also delete
# every sibling of a copied directory, dashboard/data among them.
SRCDIRS  := scripts dashboard/scripts dashboard/tools dashboard/!backups
SRCFILES := Makefile .gitignore HANDOFF.md dashboard/report_template.html dashboard/README.md
BUILT    := README.md data outputs castanet dashboard/data dashboard/benzine-prices.html
RSYNC    := rsync -a --exclude __pycache__ --exclude .DS_Store

# The lock keeps two runs on one host from overlapping (two pipelines once
# crashed together writing one daily_all.csv). flock exists on poptiplex, not
# on the Mac; without it the run is unlocked.
refresh:
	if command -v flock >/dev/null; then \
	  flock -w 3600 $(LOCK) sh -c '$(MAKE) fetch && $(MAKE) build'; \
	else $(MAKE) fetch && $(MAKE) build; fi

build: report dashboard castanet

report: parse osm summary figures readme

# A missing current-year archive is expected in January only; any other
# failure stops the build rather than silently dropping the year.
fetch:
	mkdir -p work data/geo
	for y in $$(seq 2025 $$(($(THIS) - 1))); do \
	  curl -fsS -o work/annuel_$$y.zip https://donnees.roulez-eco.fr/opendata/annee/$$y \
	  && (cd work && unzip -oq annuel_$$y.zip) || exit 1; done
	if curl -fsS -o work/annuel_$(THIS).zip https://donnees.roulez-eco.fr/opendata/annee/$(THIS) \
	   && (cd work && unzip -oq annuel_$(THIS).zip); then :; \
	elif [ "$$(date +%m)" = 01 ]; then \
	  echo "no $(THIS) archive yet; building from earlier years" >&2; \
	  rm -f work/annuel_$(THIS).zip work/PrixCarburants_annuel_$(THIS).xml; \
	else echo "the $(THIS) archive failed to download" >&2; exit 1; fi
	curl -fsS -o work/instantane.zip https://donnees.roulez-eco.fr/opendata/instantane
	cd work && unzip -oq instantane.zip
	test -s data/geo/france.geojson || curl -fsS -o data/geo/france.geojson \
	  https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/metropole.geojson
	test -s data/geo/departements.geojson || curl -fsS -o data/geo/departements.geojson \
	  https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson

# whole-country daily rows, read by every aggregate
daily:
	test -n "$(YEARS)"
	for y in $(YEARS); do \
	  $(PY) scripts/dump_daily.py work/PrixCarburants_annuel_$$y.xml work/d$$y.csv || exit 1; done
	LC_ALL=C sort -t, -k1,1 -k2,2 -k3,3 $(YEARS:%=work/d%.csv) > work/daily_all.csv

parse: daily
	$(PY) scripts/extract.py $(ANNUAL) $(INST)
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

# The dashboard reads Castanet's aggregates and brands from data/castanet/ and
# adds what only it needs: every timestamped price post, and the instant
# feed's national ceiling shares.
dashboard: parse osm dashboard-parse dashboard-html

dashboard-parse:
	for y in $(YEARS); do $(DPY) dashboard/scripts/extract.py \
	  work/PrixCarburants_annuel_$$y.xml dashboard/data/px_$$y.csv || exit 1; done
	$(DPY) dashboard/scripts/ceilings_now.py $(INST) dashboard/data/ceilings_now.csv

dashboard-html:
	# trend and weekday read the per-station price posts and need the brands
	cd dashboard && $(DPY) scripts/trend.py ../data/castanet/brands.csv ../data/archive_end.txt \
	  data/trend_split.csv data/px_20*.csv
	cd dashboard && $(DPY) scripts/weekday.py data/px_20*.csv ../data/archive_end.txt \
	  data/weekday_dev.csv data/weekday_upd.csv
	cd dashboard && $(DPY) scripts/build_report.py
	cd dashboard && $(DPY) scripts/render_html.py report_template.html data/report_data.json \
	  benzine-prices.html

castanet:
	$(VPY) scripts/castanet_md.py dashboard/data/report_data.json castanet

venv:
	python3 -m venv .venv && .venv/bin/pip install -q matplotlib pillow numpy

# --- run on the Mac ----------------------------------------------------------
# Refuses to run unless this checkout is main, equal to origin/main, with the
# built files untouched: the final reset would otherwise drop local commits or
# edits. The message travels as a file, so any character in MSG is safe.
export MSG
publish:
	test "$$(git rev-parse --abbrev-ref HEAD)" = main
	git fetch -q origin
	@test "$$(git rev-parse HEAD)" = "$$(git rev-parse origin/main)" || \
	  { echo "HEAD differs from origin/main: pull or push first" >&2; exit 1; }
	@test -z "$$(git status --porcelain -- $(BUILT))" || \
	  { echo "built files changed here: git checkout -- them first" >&2; exit 1; }
	ssh $(HOST) 'cd $(RDIR) && git pull -q --ff-only && mkdir -p work'
	$(RSYNC) -R $(SRCFILES) $(HOST):$(RDIR)/
	for d in $(SRCDIRS); do \
	  $(RSYNC) --delete "$$d/" "$(HOST):$(RDIR)/$$d/" || exit 1; done
	printf '%s\n' "$$MSG" | ssh $(HOST) 'cat > $(RDIR)/work/MSG'
	ssh $(HOST) 'cd $(RDIR) && make release'
	git fetch -q origin
	git reset -q origin/main
	git checkout -- $(BUILT)
	git status --short

# --- run on poptiplex, by publish --------------------------------------------
release:
	flock -w 3600 $(LOCK) sh -c '$(MAKE) fetch && $(MAKE) build && $(MAKE) push'

push:
	git add -A
	if git diff --cached --quiet; then echo "nothing to commit"; \
	elif grep -q . work/MSG 2>/dev/null; then git commit -qF work/MSG; \
	else git commit -qm "Refresh data through $$(cat data/archive_end.txt) (built $$(date +%F))"; fi
	rm -f work/MSG
	git push -q

# the steps read one another's files; never run them in parallel
.NOTPARALLEL:
.PHONY: refresh build report fetch daily parse osm summary figures readme dashboard \
        dashboard-parse dashboard-html castanet venv publish release push
