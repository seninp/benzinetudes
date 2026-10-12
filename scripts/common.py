"""Helpers shared by the aggregation scripts of both reports."""
import csv, math
from datetime import date, timedelta


def haversine_km(la1, lo1, la2, lo2):
    R = 6371.0088
    p1, p2 = math.radians(la1), math.radians(la2)
    a = (math.sin((p2 - p1) / 2) ** 2 +
         math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def read_daily(path):
    """Yield (station_id, fuel, [(day, price), ...]) from the sorted daily rows.

    Input is dump_daily.py output sorted by station, fuel, day. A malformed or
    out-of-order row raises with its line number, so a damaged file is easy to find.
    """
    cur, buf = None, []
    with open(path, newline="") as f:
        for n, row in enumerate(csv.reader(f), 1):
            try:
                sid, fuel, day, price = row
                d, p = date.fromisoformat(day), float(price)
            except ValueError as e:
                raise ValueError(f"{path}:{n}: malformed row {row!r}: {e}") from None
            if (sid, fuel) != cur:
                if buf:
                    yield cur[0], cur[1], buf
                cur, buf = (sid, fuel), []
            elif d < buf[-1][0]:
                raise ValueError(f"{path}:{n}: day {day} before {buf[-1][0]} for {sid}/{fuel}")
            buf.append((d, p))
    if buf:
        yield cur[0], cur[1], buf


def carry_forward(rows, end_day, stale_days):
    """Yield (day, price) for every day from the first post to the last post
    plus stale_days (never past end_day), carrying the last posted price."""
    d, last, i = rows[0][0], rows[0][1], 0
    stop = min(rows[-1][0] + timedelta(days=stale_days), end_day)
    while d <= stop:
        while i < len(rows) and rows[i][0] <= d:
            last = rows[i][1]
            i += 1
        yield d, last
        d += timedelta(days=1)


def dry_series(intervals, days, window, ids=None):
    """Dry station-fuel pairs on each of days.

    intervals are (id, fuel, debut, fin) rows of rupture_hist.csv, ISO dates, fin
    empty while open. A pair is dry on day d when an outage began in the window
    days up to d and had not ended by d (fin is the first day back in stock). An
    older flag means the station stopped selling that fuel. A pair counts once
    however many of its intervals overlap. ids, if given, limits the stations.
    """
    out = []
    for d in days:
        iso, floor = d.isoformat(), (d - timedelta(days=window)).isoformat()
        out.append(len({(sid, fuel) for sid, fuel, debut, fin in intervals
                        if (ids is None or sid in ids) and floor <= debut <= iso
                        and (not fin or fin > iso)}))
    return out
