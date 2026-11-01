"""Training trends for every month, from the FitNotes CSV (tools/fitnotes.py output).

Usage: python3 tools/trends.py <fitnotes.csv> data/2026-trends.js

Strength
  e1RM      Epley estimate, weight x (1 + reps/30). Puts a heavy triple and a light set of ten on one scale,
            so "more weight, fewer reps" and "less weight, more reps" both count as progress when they are.
  Index     Chained like a price index: each month, every lift that was also done before is compared with
            its last known best e1RM; the median change moves the index (each lift capped at +/-20% a month,
            lifts done fewer than 4 times all year left out). January = 100.
            New exercises join the index the month after they first appear, so adding a lift never
            fakes progress.
  Overload  Session by session: did this exercise beat the last session of the same exercise
            (best e1RM, or reps for bodyweight work)? Share of sessions that beat or matched it.
Running
  2-mile equivalent  Every run of 1.5 mi or more converted to a 2-mile time with Riegel's formula
            (T2 = T x (2 / d)^1.06), so a 5K and a 6-miler are comparable. Best per month.
"""
import csv, json, math, sys, collections, datetime as dt

SKIP = ('Mobility', 'Isometric', 'L Hold', 'Hip Plank', 'One Leg Bosu')
BODY = {'Plank': 'time', 'Pushup': 'reps', 'Timed Sit Up': 'reps', 'Chin Up': 'reps', 'Hrp Emom': 'reps', 'Elevated Push Up': 'reps', 'Hanging Leg Raise': 'reps'}
RUNS = ('Running (Outdoor)', 'Running (Treadmill)')  # Zone 2 logs incline in the distance field, so it counts as time only
TO_MI = {'mi': 1.0, 'km': 0.621371, 'm': 0.000621371}


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def secs(t):
    if not t:
        return 0
    s = 0
    for p in t.split(':'):
        s = s * 60 + int(p)
    return s


def e1rm(w, r):
    return w * (1 + r / 30.0) if w > 0 and r > 0 else 0


def slope(pts):
    pts = [(x, y) for x, y in pts if y]
    if len(pts) < 2:
        return 0
    n = len(pts); mx = sum(p[0] for p in pts) / n; my = sum(p[1] for p in pts) / n
    d = sum((p[0] - mx) ** 2 for p in pts)
    return sum((p[0] - mx) * (p[1] - my) for p in pts) / d if d else 0


def mmss(s):
    s = int(round(s)); return '%d:%02d' % (s // 60, s % 60)


def main(src, out):
    rows = list(csv.DictReader(open(src)))
    months = sorted({r['Date'][:7] for r in rows})
    M = len(months)
    mi = {m: i for i, m in enumerate(months)}

    # ---------- strength: best set per exercise per session and per month ----------
    sess = collections.defaultdict(dict)       # (ex) -> date -> best e1rm / reps
    cat_of = {}
    mon = collections.defaultdict(lambda: collections.defaultdict(lambda: {'e1': 0, 'set': None, 'maxw': 0, 'maxr': 0, 'bestvol': 0, 'vol': 0, 'sets': 0, 'days': set()}))
    for r in rows:
        ex, c = r['Exercise'], r['Category']
        if c == 'Cardio' or any(k in ex for k in SKIP) or ex in BODY:
            continue
        w, n = f(r['Weight (lbs)']), int(f(r['Reps']))
        if w <= 0 or n <= 0:
            continue
        cat_of[ex] = c
        e = e1rm(w, n); m = r['Date'][:7]; d = mon[ex][m]
        if e > d['e1']:
            d['e1'], d['set'] = e, (w, n)
        d['maxw'] = max(d['maxw'], w); d['maxr'] = max(d['maxr'], n); d['bestvol'] = max(d['bestvol'], w * n)
        d['vol'] += w * n; d['sets'] += 1; d['days'].add(r['Date'])
        sess[ex][r['Date']] = max(sess[ex].get(r['Date'], 0), e)

    # chained index, overall and by category
    def chain(exs):
        idx, last, out = 100.0, {}, []
        for m in months:
            logs = sorted(max(-0.2, min(0.2, math.log(mon[e][m]['e1'] / last[e]))) for e in exs if m in mon[e] and e in last and last[e] > 0)
            if logs:  # median change, each lift capped at +/-20% a month so one odd session cannot swing the index
                k = len(logs); idx *= math.exp(logs[k // 2] if k % 2 else (logs[k // 2 - 1] + logs[k // 2]) / 2)
            out.append(round(idx, 1) if any(m in mon[e] for e in exs) or out else None)
            for e in exs:
                if m in mon[e]:
                    last[e] = max(mon[e][m]['e1'], 0) or last.get(e, 0)
        return out
    allex = [e for e in mon if sum(len(mon[e][m]['days']) for m in mon[e]) >= 4]
    cats = sorted({cat_of[e] for e in allex})
    index = chain(allex)
    bycat = {c: chain([e for e in allex if cat_of[e] == c]) for c in cats}

    # overload: each session vs the previous session of the same exercise
    over = [[0, 0, 0] for _ in months]           # up, same, down
    for ex, ds in sess.items():
        prev = None
        for d in sorted(ds):
            v = ds[d]
            if prev is not None:
                k = 0 if v > prev * 1.005 else 1 if v >= prev * 0.995 else 2
                over[mi[d[:7]]][k] += 1
            prev = v

    # per-month lift table: lifts done that month in at least two sessions over the year
    freq = collections.Counter({e: sum(len(mon[e][m]['days']) for m in mon[e]) for e in allex})
    lifts = []
    for i, m in enumerate(months):
        tab = []
        for e in allex:
            if m not in mon[e] or freq[e] < 4:
                continue
            d = mon[e][m]
            prior = [mon[e][p]['e1'] for p in months[:i] if p in mon[e]]
            last = prior[-1] if prior else None
            first = prior[0] if prior else d['e1']
            hist = [(j, mon[e][p]['e1']) for j, p in enumerate(months[:i + 1]) if p in mon[e]]
            tab.append({'ex': e.replace(' Potsdam', '').replace('Cabel', 'Cable'), 'cat': cat_of[e], 'set': '%g x %d' % d['set'], 'e1': round(d['e1']),
                        'prev': round(last) if last else None, 'first': round(first),
                        'pr': bool(prior) and d['e1'] > max(prior) * 1.001,
                        'maxw': d['maxw'], 'maxr': d['maxr'], 'bestvol': round(d['bestvol']), 'vol': round(d['vol']),
                        'sets': d['sets'], 'slope': round(slope(hist), 1), 'n': freq[e],
                        'hist': [round(mon[e][p]['e1']) if p in mon[e] else None for p in months[:i + 1]]})
        tab.sort(key=lambda t: (-t['n'], t['ex']))
        lifts.append(tab[:14])

    # ---------- bodyweight and core ----------
    body = {k: [None] * M for k in ('plank', 'pushups', 'situps', 'chinups')}
    for r in rows:
        i = mi[r['Date'][:7]]; ex = r['Exercise']
        if ex == 'Plank':
            body['plank'][i] = max(body['plank'][i] or 0, secs(r['Time']))
        elif ex in ('Pushup', 'Elevated Push Up'):
            body['pushups'][i] = max(body['pushups'][i] or 0, int(f(r['Reps'])))
        elif ex == 'Timed Sit Up':
            body['situps'][i] = max(body['situps'][i] or 0, int(f(r['Reps'])))
        elif ex == 'Chin Up':
            body['chinups'][i] = max(body['chinups'][i] or 0, int(f(r['Reps'])))

    # ---------- running and cardio ----------
    run = {k: [None] * M for k in ('miles', 'minutes', 'runs', 'bestPace', 'longest', 'eq2', 'sprintMph')}
    for k in ('miles', 'minutes', 'runs'):
        run[k] = [0] * M
    for r in rows:
        i = mi[r['Date'][:7]]; ex = r['Exercise']; t = secs(r['Time'])
        if ex == 'Treadmill Sprint':
            sp = f(r['Weight (lbs)'])
            if sp:
                run['sprintMph'][i] = max(run['sprintMph'][i] or 0, sp)
            run['minutes'][i] += t / 60
            continue
        if ex == 'Sprint' and f(r['Distance']) and t:
            mph = f(r['Distance']) * TO_MI.get(r['Distance Unit'], 0) / (t / 3600)
            run['sprintMph'][i] = max(run['sprintMph'][i] or 0, round(mph, 1))
            continue
        if ex not in RUNS:
            if r['Category'] == 'Cardio':
                run['minutes'][i] += t / 60
            continue
        d = f(r['Distance']) * TO_MI.get(r['Distance Unit'], 0)
        if not d or not t:
            continue
        run['miles'][i] += d; run['minutes'][i] += t / 60; run['runs'][i] += 1
        pace = t / d
        run['longest'][i] = max(run['longest'][i] or 0, round(d, 2))
        if d >= 1:
            run['bestPace'][i] = min(run['bestPace'][i] or 1e9, pace)
        if d >= 1.5:
            eq = t * (2 / d) ** 1.06
            run['eq2'][i] = min(run['eq2'][i] or 1e9, eq)
    for k in ('miles', 'minutes'):
        run[k] = [round(v, 1) for v in run[k]]
    for k in ('bestPace', 'eq2'):
        run[k] = [round(v) if v else None for v in run[k]]

    data = {'months': months, 'index': index, 'byCat': bycat, 'overload': over, 'lifts': lifts, 'body': body, 'run': run,
            'method': 'e1RM = weight x (1 + reps / 30). Strength index: median month-over-month change of each lift against its last best, chained, Jan = 100. 2-mile equivalent uses Riegel: T x (2 / miles)^1.06.'}
    js = ('/* Generated by tools/trends.py from the FitNotes export. Do not edit by hand; rerun the script.\n'
          '   ' + data['method'] + ' */\nwindow.TRENDS = ' + json.dumps(data, separators=(',', ':')) + ';\n')
    open(out, 'w').write(js)
    print('months', months)
    print('index', index)
    for c in cats:
        print(c, bycat[c])
    print('overload', over)
    print('eq2', [mmss(v) if v else None for v in run['eq2']])
    print('bestPace', [mmss(v) if v else None for v in run['bestPace']])
    print('sprint', run['sprintMph'], 'miles', run['miles'])
    print('body', body)


if __name__ == '__main__':
    main(*sys.argv[1:])
