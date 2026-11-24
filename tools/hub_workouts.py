"""Convert the Command Center 'Workouts' tab (values JSON from the Sheets API) into the FitNotes CSV layout gym.py reads.

Usage: python3 tools/hub_workouts.py <values.json|get_values result file> <out.csv>
Hub columns: Date, Weekday, Workout #, Category, Exercise, Set #, Weight (lb), Weight (kg), Machine setting, Reps, Time (min:sec), Distance
The hub tab carries no distance unit. Miles are assumed (runs of 8 in about 75 minutes fit miles). Check this once against FitNotes.
"""
import sys, json, csv, datetime as dt

def iso(s):
    return dt.datetime.strptime(s.split(' ', 1)[1], '%b %d, %Y').date().isoformat()

def hms(t):
    if not t: return ''
    p = [int(x) for x in t.split(':')]
    if len(p) == 2: p = [0] + p
    return '%d:%02d:%02d' % tuple(p)

def load_values(path):
    raw = open(path).read()
    try: j = json.loads(raw)
    except ValueError: j = json.loads(raw[raw.index('{'):])
    if isinstance(j, dict) and 'content' in j: j = j['content']
    if isinstance(j, list) and j and isinstance(j[0], dict) and 'text' in j[0]: j = json.loads(j[0]['text'])
    return j['values'] if isinstance(j, dict) else j

def convert(src, out):
    n = 0
    w = csv.writer(open(out, 'w', newline=''))
    w.writerow(['Date', 'Exercise', 'Category', 'Weight (lbs)', 'Reps', 'Distance', 'Distance Unit', 'Time', 'Notes'])
    for r in load_values(src):
        r = list(r) + [''] * (12 - len(r))
        if not r[0] or r[0] == 'Date' or ' ' not in r[0]: continue
        try: d = iso(r[0])
        except ValueError: continue
        reps = r[9] if r[9] not in ('', '0') or not r[10] else ''
        w.writerow([d, r[4], r[3], r[6], reps, r[11], 'mi' if r[11] else '', hms(r[10]), ''])
        n += 1
    return n

if __name__ == '__main__':
    print(convert(*sys.argv[1:3]), 'sets written')
