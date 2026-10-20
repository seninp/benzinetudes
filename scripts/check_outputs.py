#!/usr/bin/env python3
"""Fail the build when the published outputs contradict their data or each other.

Every check here stands for a defect that once shipped: prose that said "rising"
over a falling slope, "cheaper" for the dearer group, a cap streak of 0 days, dry
counts that differed between reports, a hand-typed station count, a cap written
"2,250 €" beside prices written "2.344", a dashboard version pill out of step
with its meta tag. Run from the repo root after the build:

    python3 scripts/check_outputs.py      # = make check; exit 1 on any failure
"""
import hashlib, json, os, re, sys
from config import CEILING, PIN_TOL

FAIL = []


def check(ok, what):
    if not ok:
        FAIL.append(what)


def num(pattern, text, what):
    """The first group of pattern in text as a float, or None after recording a failure."""
    m = re.search(pattern, text, re.S)
    if not m:
        FAIL.append(f"{what}: pattern not found ({pattern})")
        return None
    return float(m.group(1).replace(",", ""))


cmp_ = json.load(open("data/compare.json"))
cast = json.load(open("data/castanet/summary.json"))
D = json.load(open("dashboard/data/report_data.json"))
readme = open("README.md").read()
cmd = open("castanet/README.md").read()
html = open("dashboard/benzine-prices.html").read()
meta = D["meta"]
archive_end = open("data/archive_end.txt").read().strip()
city = next(c for c in cmp_["cities"] if c["slug"] == "castanet")

# ---- one end date everywhere -------------------------------------------------
for name, v in (("compare.end", cmp_["end"]), ("compare.archive_end", cmp_["archive_end"]),
                ("dashboard meta.end", meta["end"]), ("dashboard meta.archive_end", meta["archive_end"]),
                ("dashboard obs_end", D["obs_end"])):
    check(v == archive_end, f"{name} is {v}, archive_end.txt says {archive_end}")

# ---- direction words follow the slopes --------------------------------------
SIGN = {"rising": 1, "falling": -1}


def dir_ok(d, sl, what):
    if d in SIGN:
        check(sl and sl["cw"] * SIGN[d] > 0, f"{what} is '{d}' but the slope is {sl and sl['cw']}")


tg = D["trend"]["Gazole"]["loc"]
sp = D["split"]["Gazole"]
dir_ok(tg["dir"], tg["slope"], "trend.Gazole.loc.dir")
dir_ok(sp.get("other_dir"), sp["other_slope"], "split.Gazole.other_dir")
check(f"local diesel has been {tg['dir']}" in " ".join(cmd.split()),
      f"castanet/README.md does not say local diesel has been '{tg['dir']}'")

# ---- the cap streak ----------------------------------------------------------
on_cap = (sp["total_now"] >= sp["level"] - PIN_TOL
          and (sp["cap_evidence"]["total_max"] or 0) <= sp["level"] + 5e-5)
check(not on_cap or sp["pinned_days"] is not None,
      f"Total group sits on the cap ({sp['total_now']}) but pinned_days is None")

# ---- before the cap: dearer or cheaper ----------------------------------------
pre = sp.get("pre_cap")
if pre:
    word = "dearer" if pre["gap_c"] < 0 else "cheaper"
    check(f"*{word}* ones" in cmd, f"castanet/README.md should call the Total group *{word}* "
                                   f"before the cap (gap {pre['gap_c']} c)")

# ---- the rise day is claimed only when it passes its test ---------------------
rd, sig = D["weekday"]["rise_day"], D["weekday"].get("rise_day_sig")
claims = re.search(r"Rises cluster on \*\*(\w+)\*\*", cmd)
check(bool(claims) == bool(sig), f"castanet/README.md {'claims' if claims else 'omits'} a rise day, "
                                 f"rise_day_sig is {sig}")
if claims and rd:
    check(claims.group(1) == rd["name"], f"castanet/README.md names {claims.group(1)}, data {rd['name']}")

# ---- the same number in every output -----------------------------------------
gz = next(c for c in D["cards"] if c["fuel"] == "Gazole")
check(abs(city["diesel"] - gz["value"]) < 5e-4,
      f"Castanet diesel: three-city {city['diesel']}, dashboard {gz['value']}")
v = num(r"Diesel sits at \*\*([\d.]+) €/L", cmd, "castanet/README.md diesel")
check(v is None or abs(v - gz["value"]) < 5e-4, f"castanet/README.md diesel {v}, data {gz['value']}")
v = num(r"\[Castanet-Tolosan\]\(#castanet\) \| \d+ \| \*\*([\d.]+)\*\*", readme, "README.md Castanet diesel")
check(v is None or abs(v - city["diesel"]) < 5e-4, f"README.md Castanet diesel {v}, data {city['diesel']}")

dry_d = D["dry_hist"]["all"][-1]
check(city["dry_now"] == dry_d, f"Castanet dry pairs: three-city {city['dry_now']}, dashboard {dry_d}")
v = num(r"It sits at (\d+) now", cmd, "castanet/README.md dry now")
check(v is None or v == dry_d, f"castanet/README.md dry now {v}, data {dry_d}")
peak3 = max(x for x in cast["series"]["dry"] if x is not None)
v = num(r"peaked at \*\*(\d+)\*\*", cmd, "castanet/README.md dry peak")
check(v is None or v == peak3 == max(D["dry_hist"]["all"]),
      f"dry peak: castanet/README.md {v}, three-city {peak3}, dashboard {max(D['dry_hist']['all'])}")

check(cmp_["nat_n"] == meta["nat_n"], f"French station count: compare {cmp_['nat_n']}, dashboard {meta['nat_n']}")
want = round(cmp_["nat_n"], -2)
for name, text in (("README.md", readme), ("castanet/README.md", cmd)):
    v = num(r"~([\d,]+)\s+French\s+stations", text, f"{name} French count")
    check(v is None or v == want, f"{name} says ~{v:,.0f} French stations, data ~{want:,}" if v else "")

# ---- formats -----------------------------------------------------------------
for name, text in (("README.md", readme), ("castanet/README.md", cmd)):
    for m in re.finditer(r"\b\d,\d{3}\s*€", text):
        FAIL.append(f"{name}: '{m.group(0)}' — prices take a decimal point")
    for m in re.finditer(r"\b1 days\b", text):
        FAIL.append(f"{name}: '1 days'")
    caps = {f"{x:.3f}" for x in CEILING.values()}
    check(any(c in text for c in caps), f"{name} never mentions a ceiling price")

# ---- every figure link points at the PNG it was built with --------------------
for name, text, base in (("README.md", readme, "."), ("castanet/README.md", cmd, "castanet")):
    for path, h in re.findall(r"\]\(([^)?]+\.png)\?v=([0-9a-f]{8})\)", text):
        p = os.path.join(base, path)
        if not os.path.exists(p):
            FAIL.append(f"{name}: {path} does not exist")
        elif hashlib.md5(open(p, "rb").read()).hexdigest()[:8] != h:
            FAIL.append(f"{name}: {path}?v={h} is stale")

# ---- dashboard version markers agree -----------------------------------------
ver = re.search(r'<meta name="version" content="([^"]+)">', html)
upd = re.search(r'<meta name="last-updated" content="([^"]+)">', html)
pill = re.search(r'<span id="vpill">v([^ ]+) · ([\d-]+)</span>', html)
if not (ver and upd and pill):
    FAIL.append("dashboard: version meta tags or pill missing")
else:
    check(ver.group(1) == pill.group(1), f"dashboard: meta version {ver.group(1)}, pill v{pill.group(1)}")
    check(upd.group(1) == pill.group(2), f"dashboard: last-updated {upd.group(1)}, pill {pill.group(2)}")
    log = re.search(r"<!-- Changelog\s+([\d.]+) \(", html)
    check(log and log.group(1) == ver.group(1),
          f"dashboard: newest changelog entry {log and log.group(1)}, version {ver.group(1)}")
    hand = re.search(r"Castanet dashboard \(v([\d.]+)\)", open("HANDOFF.md").read())
    check(hand and hand.group(1) == ver.group(1),
          f"HANDOFF.md names dashboard v{hand and hand.group(1)}, the HTML is v{ver.group(1)}")

FAIL = [f for f in FAIL if f]
if FAIL:
    print(f"check_outputs: {len(FAIL)} failure(s)", file=sys.stderr)
    for f in FAIL:
        print("  -", f, file=sys.stderr)
    sys.exit(1)
print("check_outputs: all outputs agree with their data", file=sys.stderr)
