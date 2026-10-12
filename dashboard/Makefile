# benzine — fuel prices around Castanet-Tolosan.
#
#   make            remote + report + castanet: the daily rebuild
#   make remote     heavy half on poptiplex, products copied into data/
#   make local      the same heavy half on this Mac, in work/ (~3 min)
#   make report     data/ -> benzine-prices.html
#   make castanet   render the Castanet deep-dive in benzinetudes (commit there)
HOST   := psenin@192.168.10.51
RDIR   := benzine
TUDES  := git/benzinetudes
# products of scripts/remote.sh that the report reads; px_<year>.csv come too
PRODUCTS := nat_daily.csv loc_daily.csv stations_now.csv st_all.csv capshare.csv \
            ceilings_now.csv ruptures.csv rupture_hist.csv osm_fuel.json archive_end.txt

all: remote report castanet

remote:
	ssh $(HOST) "mkdir -p ~/$(RDIR)"
	scp -q scripts/*.py scripts/remote.sh $(HOST):$(RDIR)/
	ssh $(HOST) "cd ~/$(RDIR) && sh ./remote.sh"
	for f in $(PRODUCTS) 'px_20*.csv'; do scp -q "$(HOST):$(RDIR)/$$f" data/ || exit 1; done

local:
	mkdir -p work
	cp data/osm_fuel.json work/ 2>/dev/null || true
	cd work && sh ../scripts/remote.sh
	cd work && cp $(PRODUCTS) px_20*.csv ../data/

report:
	python3 scripts/brands.py data/osm_fuel.json data/stations_now.csv data/brands.csv
	# trend and weekday read the per-station price history and need brands.csv
	python3 scripts/trend.py data/brands.csv data/archive_end.txt data/trend_split.csv data/px_20*.csv
	python3 scripts/weekday.py data/px_20*.csv data/archive_end.txt \
	  data/weekday_dev.csv data/weekday_upd.csv
	python3 scripts/build_report.py
	python3 scripts/render_html.py report_template.html data/report_data.json benzine-prices.html

castanet:
	scp -q data/report_data.json $(HOST):$(TUDES)/work/report_data.json
	ssh $(HOST) "cd ~/$(TUDES) && make castanet"

# the targets of `all` depend on one another's files; never run them in parallel
.NOTPARALLEL:
.PHONY: all remote local report castanet
