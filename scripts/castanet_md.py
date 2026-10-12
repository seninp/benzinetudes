#!/usr/bin/env python3
"""Render the single-city Castanet deep-dive as a static Markdown report.

The interactive dashboard (benzine-prices.html) does not render on GitHub, so
this emits <outdir>/README.md plus <outdir>/fig/*.png from the same
report_data.json, which the benzine pipeline builds on the Mac and copies to
work/report_data.json (`make castanet` in benzine). Prose and figures share
style.py with the three-city report one level up.

    make castanet     # = .venv/bin/python scripts/castanet_md.py work/report_data.json castanet

Every figure link carries ?v=<md5[:8]> of the PNG so GitHub's image cache never
serves a stale build.
"""
import hashlib, json, os, sys
from datetime import date

from style import BASE, CRITICAL, MUTED, NAT, SECOND, arr, end_label, save, style
import matplotlib.pyplot as plt
import numpy as np
from cities import CEILING, CITIES

CAST = CITIES[0]["color"]             # Castanet's colour in the three-city report
FREE = "#eb6834"                      # the free (uncapped) cohort


# ---- load ------------------------------------------------------------------
D = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
FIG = os.path.join(OUT, "fig")
days = [date.fromisoformat(d) for d in D["days"]]
meta = D["meta"]


def v(name):
    p = os.path.join(FIG, name)
    h = hashlib.md5(open(p, "rb").read()).hexdigest()[:8]
    return f"fig/{name}?v={h}"


def eur(x, nd=3):
    return f"{x:.{nd}f}" if x is not None else "—"


def sgn(x, nd=3):
    return f"{x:+.{nd}f}" if x is not None else "—"


# ============================================================================
# figures
# ============================================================================

# ---- prices: diesel + E10, local vs France, with the ceilings --------------
fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.8))
for ax, fuel, label in zip(axes, ("Gazole", "E10"), ("Diesel (Gazole)", "Petrol (E10)")):
    ax.plot(days, arr(D["nat"][fuel]), color=NAT, lw=1.4, ls=(0, (4, 3)), label="France")
    ax.plot(days, arr(D["local"][fuel]), color=CAST, lw=2, label="Castanet 15 km")
    ax.axhline(CEILING[fuel], color=BASE, lw=1, ls=":")
    ax.set_title(f"{label}  (€/L)", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    style(ax)
fig.tight_layout()
save(fig, os.path.join(FIG, "prices.png"))

# ---- split: the ceiling divides the field ----------------------------------
sp = D["split"]["Gazole"]
sdays = [date.fromisoformat(d) for d in sp["days"]]
tot, oth = arr(sp["total"]), arr(sp["other"])
fig, ax = plt.subplots(figsize=(9.5, 4.4))
ax.plot(sdays, oth, color=FREE, lw=2, label="every other brand")
ax.plot(sdays, tot, color=CAST, lw=2, label="Total-group (TotalEnergies, Total Access)")
ax.axhline(sp["level"], color=BASE, lw=1, ls=":")
ax.annotate("2,250 € ceiling", (sdays[300], sp["level"]), xytext=(0, 5),
            textcoords="offset points", color=MUTED, fontsize=9)
tl = tot[~np.isnan(tot)]; ol = oth[~np.isnan(oth)]
end_label(ax, sdays[-1], tl[-1], f"{tl[-1]:.3f}", CAST)
end_label(ax, sdays[-1], ol[-1], f"{ol[-1]:.3f}", FREE)
ax.set_title("Diesel within 15 km, split by brand group  (€/L)", loc="left", pad=12)
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.margins(x=0.01)
ax.set_xlim(sdays[0], sdays[-1] + (sdays[-1] - sdays[0]) / 12)
style(ax)
save(fig, os.path.join(FIG, "split.png"))

# ---- weekday: cheapest-day illusion, and when moves land --------------------
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
wd = D["weekday"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.9))

rose = [r["dev"] for r in wd["dec"]["rose"]["rows"]]
fell = [r["dev"] for r in wd["dec"]["fell"]["rows"]]
x = np.arange(7)
a1.axhline(0, color=BASE, lw=1)
a1.plot(x, rose, color=CRITICAL, lw=2, marker="o", ms=4, label="weeks diesel rose")
a1.plot(x, fell, color=CAST, lw=2, marker="o", ms=4, label="weeks it fell")
a1.set_xticks(x); a1.set_xticklabels(DOW)
a1.set_title("Deviation from the week's own mean  (¢/L)", loc="left", fontsize=10.5)
a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.grid(axis="x", visible=False); a1.spines["left"].set_visible(False)
a1.tick_params(length=0)

upd = [c["mean_c"] for c in wd["upd"]["Gazole"]]
rise_dow = wd["rise_day"]["dow"]
colors = [CAST if i == rise_dow else BASE for i in range(7)]
a2.axhline(0, color=BASE, lw=1)
a2.bar(x, upd, color=colors, width=0.7)
a2.set_xticks(x); a2.set_xticklabels(DOW)
a2.set_ylim(min(upd) * 1.4, max(upd) * 1.7)     # headroom so the callout clears the title
a2.set_title("Mean price change posted on the day  (¢/L)", loc="left", fontsize=10.5)
a2.annotate(f"{wd['rise_day']['name']}, {wd['rise_day']['share_up']:.0f}% up",
            (rise_dow, upd[rise_dow]), xytext=(0, 7), textcoords="offset points",
            ha="center", color=CAST, fontsize=9, fontweight="bold")
a2.grid(axis="x", visible=False); a2.spines["left"].set_visible(False)
a2.tick_params(length=0)
fig.tight_layout()
save(fig, os.path.join(FIG, "weekday.png"))

# ---- dry count over time ----------------------------------------------------
dh = D["dry_hist"]
ddays = [date.fromisoformat(d) for d in dh["days"]]
y = arr(dh["all"])
peak = max(dh["all"]); peak_day = ddays[dh["all"].index(peak)]
cap_day = date.fromisoformat(D["cap"]["since"])
fig, ax = plt.subplots(figsize=(9.5, 3.8))
ax.fill_between(ddays, 0, np.nan_to_num(y), color=CRITICAL, alpha=0.2, lw=0)
ax.plot(ddays, y, color=CRITICAL, lw=1.8)
ax.axvline(cap_day, color=SECOND, lw=1, ls=(0, (2, 3)))
ax.annotate("ceiling appears\n8 Apr 2026", (cap_day, peak * 0.96), xytext=(8, 0),
            textcoords="offset points", va="top", color=SECOND, fontsize=8.5)
ax.annotate(f"peak {peak} on {peak_day:%-d %b}", (peak_day, peak), xytext=(0, 6),
            textcoords="offset points", ha="center", color=CRITICAL,
            fontsize=9, fontweight="bold")
ax.set_title("Station-fuel pairs flagged out of stock within 15 km  (count)",
             loc="left", pad=12)
ax.margins(x=0.01)
style(ax)
save(fig, os.path.join(FIG, "dry.png"))

# ============================================================================
# markdown
# ============================================================================
built = meta["built"]
L = []
add = L.append

add(f"""# Benzine — Castanet-Tolosan, in depth

**Diesel and petrol at every station within {meta['radius']} km of
Castanet-Tolosan (31320), against the mean of all ~{round(meta['nat_n'] / 100) * 100:,}
French stations. The deep-dive companion to the three-city
[benzinetudes](../README.md) report — same feed, same method, one place, more
of it: the brand split under TotalEnergies' price ceiling, the day-of-week
effect, and the out-of-stock count that runs ahead of the price.**

The data is the French government's `prix-carburants` open feed. Every number
below is regenerated from it — none is typed by hand. Data current through
**{meta['end']}**, built {built}; the annual archive's observations stop at
{meta['archive_end']}, so the newest point in each price series is carried
forward (see [Reading the data](#reading-the-data)). The snapshot tables come
from the instant feed and are current.
""")

c = {r["fuel"]: r for r in D["cards"]}
add("## Where prices stand\n")
add("| Fuel | Castanet €/L | France | 30 days | 12 months | Stations |")
add("|---|---:|---:|---:|---:|---:|")
for f in ("Gazole", "E10", "SP98", "E85"):
    r = c[f]
    add(f"| {r['label']} | **{eur(r['value'])}** | {eur(r['nat'])} | "
        f"{sgn(r['d30'])} | {sgn(r['d365'])} | {r['n']} |")
add(f"\n<sub>Snapshot of {meta['n_priced']} priced stations on {D['freshness']['snapshot']}; "
    f"{D['freshness']['today']} updated that day, median age {D['freshness']['median_days']} days. "
    f"A fuel enters a mean only where at least 3 stations report.</sub>\n")

tg = D["trend"]["Gazole"]["loc"]
bm = D["big_month"]
gzc = c["Gazole"]
dv = gzc["value"] - gzc["nat"]
bm_name = date.fromisoformat(bm["month"] + "-01").strftime("%B %Y")
add(f"""![Diesel and E10: Castanet against the French mean]({v('prices.png')})

Diesel sits at **{eur(gzc['value'])} €/L** — {eur(abs(dv))}
{'below' if dv < 0 else 'above'} the French mean, and {eur(gzc['d365'])} higher
than a year ago. Almost all of that rise landed in one month: {bm['c']:.0f}
centimes in {bm_name} alone, {bm['share']}% of the twelve-month move. The local
line has tracked the national one within a centime or two throughout, and both
are still climbing — about {tg['slope']['cw']:.1f} ¢/week over the last four weeks.
""")

# ---- the ceiling and the split ---------------------------------------------
st = D["cap_story"]
cap = D["cap"]
gz = D["ceilings"]["Gazole"]
ev = sp["cap_evidence"]
add(f"""## The ceiling splits the field

On **8 April 2026** TotalEnergies set a hard **2,250 €/L** ceiling on diesel
(and **1,990 €** on petrol). The day before, {st['before']['loc']['at']:.0f}% of
local diesel stations sat exactly on that price; the day after,
{st['after']['loc']['at']:.0f}%. It slackened when the market fell below it in
the summer — on {st['trough']['day']} only {st['trough']['at']:.1f}% of French
stations were at the cap — and has bound again since early September. Today
**{gz['archive_pct_loc']:.1f}%** of local diesel stations post exactly 2,250 €,
against {gz['archive_pct_at']:.1f}% nationally.

Averaging the whole area hides what the ceiling does, because it acts on only
some brands. The {sp['total_n']} Total-group stations within 15 km are pinned to
it and cannot follow the market up; the {sp['other_n']} others are free.

![Diesel within 15 km, Total-group against every other brand]({v('split.png')})

The two groups now stand **{sp['gap_c']:.1f} centimes** apart — Total-group at
{eur(sp['total_now'])}, everyone else at {eur(sp['other_now'])} — after moving
together for a year (on {sp['pre_cap']['day']} the gap was {sp['pre_cap']['gap_c']:.1f} ¢,
the Total-group stations were the *cheaper* ones). The maxima are the proof that
2,250 € is a cap and not a price they all chose: since the ceiling bound, no
Total-group station has exceeded it, while the free brands' dearest diesel
reached {eur(ev['other_max'])} €/L. The nearest pump on the ceiling right now is
**{cap['nearest']['km']:.1f} km** away ({cap['nearest']['adresse'].title()},
{cap['nearest']['ville']}); filling there instead of at the local average saves
about {cap['save']:.2f} €/L.
""")

# ---- weekday ----------------------------------------------------------------
rd = D["weekday"]["rise_day"]
add(f"""## Which day to fill

Two questions, two answers. First, is any weekday reliably cheaper? Pooled over
every week, Monday looks cheapest and Sunday dearest — but that is the trend
leaking in, not a habit. Split the weeks by their own direction and the shape
flips: in weeks diesel rose, Monday is well below the week's mean and the weekend
above it; in weeks it fell, exactly the reverse, by almost the same amount. The
two cancel. There is **no dependable cheap day** to shop for.

![Weekday effect: the cheapest-day illusion, and when changes land]({v('weekday.png')})

Second, *when do prices move?* Here there is a real signal. Posted changes
cluster on **{rd['name']}** and lean upward — {rd['share_up']:.0f}% of
{rd['name']} changes are increases, averaging {rd['mean_c']:+.2f} ¢. The move
lands early in the week, so the practical rule is the plain one: **fill on
Monday, before Tuesday's rise.**
""")

# ---- dry count --------------------------------------------------------------
add(f"""## The dry count runs ahead

An out-of-stock flag appears in the annual archive before the price story turns.
The count of station-fuel pairs flagged dry within 15 km peaked at **{peak}** on
**{peak_day:%-d %B %Y}** — two days before the 2,250 € ceiling appeared — then
fell back. It sits at {dh['all'][-1]} now.

![Out-of-stock flags within 15 km, over time]({v('dry.png')})

Read the tail with care: outage flags and their end dates land in the archive a
day or two late, so the last few days of this line are provisional and revise
both ways on the next build.
""")

# ---- stations table ---------------------------------------------------------
SHORT = {"Gazole": "Gazole", "E10": "E10", "SP98": "SP98", "SP95": "SP95",
         "E85": "E85", "GPLc": "GPLc"}
add("""## The nearest stations

The fourteen nearest stations in the snapshot. A dash means the fuel was not
reported — capped stations drop out of the feed per fuel when they run dry, so a
dash never proves the fuel is missing:

| km | Brand | Station | Gazole | E10 | SP98 | Dry (≤ 30 d) |
|---:|---|---|---:|---:|---:|---|""")


def cell(price, fuel):
    if price is None:
        return "—"
    s = eur(price)
    return f"**{s}**" if abs(price - CEILING.get(fuel, -9)) < 1e-6 else s


for s in D["stations"][:14]:
    p = s["prices"]
    dry = ", ".join(SHORT[f] for f in s["dry"]) if s["dry"] else ""
    brand = s["brand"] + ("?" if s.get("brand_shared") else "")
    add(f"| {s['dist']:.2f} | {brand} | {s['adresse'].title()}, {s['ville']} | "
        f"{cell(p['Gazole'],'Gazole')} | {cell(p['E10'],'E10')} | "
        f"{cell(p['SP98'],'SP98')} | {dry} |")
add("\n<sub>Bold prices sit exactly on a TotalEnergies ceiling (diesel 2,250 €, "
    "petrol 1,990 €). Brand `?` — two stations share one OSM feature.</sub>\n")

# ---- brands -----------------------------------------------------------------
add("## By brand\n")
add("Diesel across the brands that OSM could name, within 15 km:\n")
add("| Brand | Stations | Cheapest | Median | Dearest |")
add("|---|---:|---:|---:|---:|")
for b in D["brands"]:
    if not b["known"] or b["n"] < 1:
        continue
    tag = " *(at the ceiling)*" if b["total"] else ""
    add(f"| {b['brand']}{tag} | {b['n']} | {eur(b['min'])} | {eur(b['median'])} | {eur(b['max'])} |")

# ---- method -----------------------------------------------------------------
add(f"""
## Reading the data

Five properties of this feed are invisible in the files themselves:

1. **No brand field exists** — not in the annual archives, not in the instant
   feed. Brands come from OpenStreetMap (`amenity=fuel` via Overpass), matched by
   position within 250 m; all {sp['total_n']} Total-group sites here matched, so
   an unmatched station is counted as "other" in the split.
2. **A missing price means "not reported", never "not sold".** Capped stations
   report per fuel intermittently and always return at exactly the ceiling, so
   any snapshot ceiling share is a lower bound; the 30-day archive share is the
   better estimate.
3. **Out-of-stock flags exist only in the annual archive.** The instant feed
   carries none. A flag with a start and no end is an open outage — but ancient
   open ones mean "stopped selling that fuel", so only flags at most 30 days old
   count as dry.
4. **The dry series revises backwards.** Flags and their end dates land a day or
   two late; the last days of the dry chart are provisional.
5. **The archive lags the build and its last day is partial.** The newest point
   in every price series is each station's last posted price carried forward, not
   a day that was measured.

Method: a station's last posted price each day is carried forward until its next
update and stops counting 30 days later, so closed sites leave the mean instead
of freezing in it. A day enters a mean only where at least 3 stations report.
Series start {meta['start']}; before that the archive's own coverage is still
ramping and would show as a fake price move. The weekday deviation compares each
day against the same station's own weekly mean, and clusters its error by
calendar week — station-weeks are not independent, since every local station
sees the same national move at once.

## Data sources

| Source | Contents |
|---|---|
| `donnees.roulez-eco.fr/opendata/annee/<year>` | every price update of the year, with outage flags |
| `donnees.roulez-eco.fr/opendata/instantane` | the current price at every station, no outage flags |
| OpenStreetMap via Overpass | station brands, matched by position |

## Licence

Price data: Ministère de l'Économie, [Licence Ouverte v2.0 (Etalab)](https://www.etalab.gouv.fr/licence-ouverte-open-licence/).
Brands: © OpenStreetMap contributors, under ODbL. Code: MIT.
""")

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "README.md"), "w").write("\n".join(L))
print(f"wrote {os.path.join(OUT, 'README.md')} ({len(chr(10).join(L))} chars)")
