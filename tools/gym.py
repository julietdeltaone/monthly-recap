"""Training summary per month from a FitNotes CSV (export, or tools/fitnotes.py output)."""
import csv, collections

MAIN_ORDER = ['Legs', 'Back', 'Chest', 'Shoulders', 'Biceps', 'Triceps', 'Abs', 'Cardio']
HUE = {'Legs': 'green', 'Back': 'blue', 'Chest': 'violet', 'Shoulders': 'teal', 'Biceps': 'amber', 'Triceps': 'amber', 'Abs': 'slate', 'Cardio': 'red'}
RENAME = {'Hrp Emom': 'Hand-release push-up EMOM', 'Running (Outdoor)': 'Outdoor run', 'Running (Treadmill)': 'Treadmill run'}
KEY_LIFTS = [('Bench', ['Flat Barbell Bench Press']), ('Squat', ['Barbell Squat', 'Smith Machine Sqaut', 'Smith Machine Squat']),
             ('Deadlift', ['Deadlift', 'Trap Bar Deadlift', 'Trap Bar DL']), ('Press', ['Standing Barbell Press', 'Overhead Press']),
             ('Pulldown', ['Lat Pulldown Potsdam', 'Lat Pulldown', 'Close Grip Lat Pull Potsdam']), ('Incline DB', ['Incline Dumbbell Bench Press']),
             ('Row', ['Barbell Row', 'Seated Cable Row']), ('Leg press', ['Leg Press'])]

def num(x): return '%g' % float(x)
def tm(t):
    h, m, s = [int(v) for v in t.split(':')]
    return ('%d:%02d:%02d' % (h, m, s)) if h else ('%d:%02d' % (m, s))
def secs(t):
    if not t: return 0
    h, m, s = [int(v) for v in t.split(':')]; return h * 3600 + m * 60 + s

def load(path):
    return list(csv.DictReader(open(path)))

def month(rows, m):
    mr = [r for r in rows if r['Date'].startswith(m)]
    days = sorted({r['Date'] for r in mr})
    vol = 0; cats = collections.defaultdict(set); sess = {}
    for r in mr:
        if r['Category'] != 'Cardio' and r['Weight (lbs)'] and r['Reps']:
            vol += float(r['Weight (lbs)']) * int(r['Reps'])
        cats[r['Date']].add(r['Category'] or 'Other')
    cardio = [r for r in mr if r['Category'] == 'Cardio']
    miles = 0
    runs = []
    for r in cardio:
        if r['Distance']:
            d = float(r['Distance']); u = r['Distance Unit']
            mi = d if u == 'mi' else d * 0.621371 if u == 'km' else d / 1609.34 if u == 'm' else 0
            miles += mi
            if mi >= 1 and r['Time']:
                pace = secs(r['Time']) / mi
                runs.append([r['Date'], RENAME.get(r['Exercise'], r['Exercise']), num(d) + ' ' + u, tm(r['Time']), '%d:%02d per mile' % (pace // 60, pace % 60), (r['Notes'] or '').split('\n')[0][:80]])
    for d in days:
        ex = collections.OrderedDict()
        for r in [x for x in mr if x['Date'] == d]:
            w, rp, dist, t, name = r['Weight (lbs)'], r['Reps'], r['Distance'], r['Time'], r['Exercise']
            if r['Category'] == 'Cardio':
                bits = []
                if dist: bits.append(num(dist) + ' ' + r['Distance Unit'])
                if t: bits.append(tm(t))
                extra = ''
                if w:
                    if 'Sprint' in name: extra = 'speed ' + num(w)
                    elif name == 'Stairs (Weighted)': extra = num(w) + ' lb vest'
                    elif name.startswith('Stairs'): extra = 'level ' + num(w)
                s_ = (' @ '.join(bits) if len(bits) > 1 else ' '.join(bits)) + ((' ' + extra) if extra else '')
            elif w and rp: s_ = num(w) + 'x' + rp
            elif rp and t: s_ = rp + ' in ' + tm(t)
            elif rp: s_ = rp + ' reps'
            elif t: s_ = tm(t)
            else: s_ = ''
            nm = RENAME.get(name, name).replace(' Potsdam', '').replace('Sqaut', 'Squat').replace('Cabel', 'Cable')
            ex.setdefault(nm, []).append(s_.strip())
        sess[str(int(d[-2:]))] = [[k, ', '.join(v)] for k, v in ex.items()]
    split = collections.Counter()
    for d in days:
        for c in cats[d]:
            if c not in ('Cardio', 'Abs', 'Other'): split[c] += 1
    cal = {}
    for d in days:
        main = [x for x in MAIN_ORDER if x in cats[d]] or ['Cardio']
        cal[str(int(d[-2:]))] = [main[0], HUE.get(main[0], 'slate')]
    best = {}
    for r in mr:
        if r['Weight (lbs)'] and r['Reps'] and r['Category'] != 'Cardio':
            w, rp = float(r['Weight (lbs)']), int(r['Reps'])
            if rp > 20: continue
            e1 = w * (1 + rp / 30)
            if r['Exercise'] not in best or e1 > best[r['Exercise']][2]: best[r['Exercise']] = (w, rp, e1, r['Date'])
    tops = []
    for label, names in KEY_LIFTS:
        cands = [(best[n], n) for n in names if n in best]
        if cands:
            (w, rp, e1, d), n = max(cands, key=lambda x: x[0][2])
            tops.append([label, '%s x %d (%s)%s' % (num(w), rp, md(d), '' if n == names[0] else ', ' + RENAME.get(n, n).replace(' Potsdam', '').replace('Sqaut', 'Squat')), round(e1)])
    situps = [[r['Date'], int(r['Reps']), secs(r['Time'])] for r in mr if r['Exercise'] == 'Timed Sit Up' and r['Reps'] and r['Time']]
    return dict(days=len(days), volume=round(vol), cardioSessions=len({r['Date'] for r in cardio}), cardioMin=round(sum(secs(r['Time']) for r in cardio) / 60),
                miles=round(miles, 1), split=dict(split.most_common()), cal=cal, sessions=sess, tops=tops, runs=runs, situps=situps)

def md(iso):
    import datetime as dt
    return dt.date.fromisoformat(iso).strftime('%b %-d')
