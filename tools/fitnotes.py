"""Convert a FitNotes iOS backup (.fitnotesdb, SQLite) into the same CSV columns as the FitNotes CSV export.

Usage: python3 tools/fitnotes.py <backup.fitnotesdb> <out.csv> [start YYYY-MM-DD] [end YYYY-MM-DD]
Weights and distances are stored x100; dates are seconds since 2001-01-01.
"""
import sqlite3, csv, sys, datetime as dt

BASE = dt.datetime(2001, 1, 1)
UNITS = {1: 'mi', 2: 'm', 3: 'km', 7: 'in'}

def fmt_time(s):
    s = int(round(s or 0))
    return '' if not s else '%d:%02d:%02d' % (s // 3600, s % 3600 // 60, s % 60)

def num(x):
    return ('%g' % x) if x else ''

def convert(db, out, start='2026-01-01', end='2026-12-31'):
    c = sqlite3.connect(db)
    names = dict(c.execute('select Z_PK, ZNAME from ZEXERCISE'))
    cats = dict(c.execute('select e.Z_PK, c.ZNAME from ZEXERCISE e left join ZEXERCISECATEGORY c on e.ZCATEGORY = c.Z_PK'))
    lo = (dt.datetime.fromisoformat(start) - BASE).total_seconds()
    hi = (dt.datetime.fromisoformat(end) + dt.timedelta(days=1) - BASE).total_seconds()
    rows = c.execute('''select s.ZDATE, s.ZEXERCISE, s.ZWEIGHTLBS, s.ZREPS, s.ZTIME, s.ZDISTANCEAMOUNT, s.ZDISTANCEUNITINT, s.ZNOTES,
                               coalesce(we.ZINDEX, 0), s.ZINDEX
                        from ZWORKOUTSET s left join ZWORKOUTEXERCISE we on s.ZWORKOUTEXERCISE = we.Z_PK
                        where s.ZDATE >= ? and s.ZDATE < ? order by s.ZDATE, 9, 10''', (lo, hi)).fetchall()
    w = csv.writer(open(out, 'w', newline=''))
    w.writerow(['Date', 'Exercise', 'Category', 'Weight (lbs)', 'Reps', 'Distance', 'Distance Unit', 'Time', 'Notes'])
    for d, ex, lbs, reps, t, dist, unit, notes, _a, _b in rows:
        date = (BASE + dt.timedelta(seconds=d)).date().isoformat()
        w.writerow([date, names.get(ex, '?'), cats.get(ex) or '', num((lbs or 0) / 100), reps or '', num((dist or 0) / 100), UNITS.get(unit, '') if dist else '',
                    fmt_time(t), (notes or '').strip()])
    return len(rows)

if __name__ == '__main__':
    print(convert(*sys.argv[1:]), 'sets written')
