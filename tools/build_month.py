"""Build data/2026-MM.js for Jan to Aug from the finance pipeline, the FitNotes rebuild, the Notion ledger,
the shared sermon file, and tools/narratives.py. Same tab layout as September and October.

Usage: python3 tools/build_month.py <fin_all.json> <fitnotes.csv> <notion_ledger.csv> 2026-01 [2026-02 ...]
"""
import sys, json, csv, datetime as dt, re
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import gym, narratives

REPO = __file__.rsplit('/', 2)[0] + '/'
CAT_HUE = {'Phone & devices': 'blue', 'Groceries': 'green', 'Dining & coffee': 'amber', 'Shopping': 'violet', 'Subscriptions': 'teal',
           'Giving': 'magenta', 'Health': 'red', 'JDM Productions': 'orange', 'Tesla': 'sky', 'Personal care': 'slate',
           'Entertainment': 'slate', 'Travel & fees': 'slate', 'Other': 'slate'}
SRC_HUE = {'Clarkson payroll': 'emerald', 'JDM Productions': 'orange', 'Taxi': 'amber', 'Guard pay': 'green', 'Uber': 'slate',
           'Interest': 'teal', 'Cashback': 'sky', 'Other': 'violet', 'Tax refund': 'blue'}
ENTITIES = {'Potsdam': 'place', 'Canton': 'place', 'Fort Drum': 'place', 'Syracuse': 'place', 'Rochester': 'place', 'Ives Park': 'place',
            'Shindigz on the River': 'place', 'Clarkson': 'school', 'Lewis School': 'school', 'SUNY Potsdam': 'school', 'Reh School': 'school',
            'Calvary Baptist': 'church', 'CBC': 'church', 'HHC': 'group', '318th RCS': 'group', '318th Recruiting Squadron': 'group',
            'JD Meyers Productions': 'org', 'JDM': 'org', 'Air Force': 'org', 'United': 'org', 'CU EMS': 'org'}
NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
SHORT = [n[:3] for n in NAMES]

def money(n, whole=False, plus=False):
    s = ('{:,.0f}' if whole else '{:,.2f}').format(abs(n))
    return ('−' if n < 0 else ('+' if plus and n > 0 else '')) + '$' + s
def first(t):
    m_ = re.match(r'(.+?[.!?])(\s|$)', t)
    return m_.group(1) if m_ else t
def md(iso): return dt.date.fromisoformat(iso).strftime('%b %-d')
def datebox(iso): d = dt.date.fromisoformat(iso); return [d.strftime('%a').upper(), str(d.day), d.strftime('%b').upper()]

def ledger(path, m):
    out = []
    for r in csv.DictReader(open(path, encoding='utf-8-sig')):
        try: d = dt.datetime.strptime(r['Service Date'].strip(), '%B %d, %Y').date()
        except ValueError: continue
        if d.isoformat()[:7] != m: continue
        amt = float(r['Amount Collected'].replace('$', '').replace(',', '') or 0)
        out.append(dict(date=d.isoformat(), client=r['Client'], type=r['Service Type'], amt=amt, status=r['Transaction Status'], loc=r['Location'].split(',')[0]))
    return sorted(out, key=lambda x: x['date'])

def finance(c, m, days, brief, notes):
    items = [{'date': md(i['date']), 'label': i['label'], 'sub': i['cat'] + ' · ' + i['acct'], 'amt': i['amt'], 'kind': i['kind']}
             for i in sorted(c['items'], key=lambda x: (x['date'], -abs(x['amt'])))]
    rate = (c['net'] / c['income'] * 100) if c['income'] else 0
    def catrows(kind):
        tot = c['bycat'] if kind == 'out' else c['bysrc']; rows = []
        for k, v in tot.items():
            if abs(v) < 0.005: continue
            its = sorted([i for i in c['items'] if i['kind'] == kind and i['cat'] == k], key=lambda i: -abs(i['amt']))
            rows.append({'name': k, 'hue': (CAT_HUE if kind == 'out' else SRC_HUE).get(k, 'slate'), 'amt': v,
                         'items': [{'date': md(i['date']), 'label': i['label'], 'sub': i['acct'], 'amt': i['amt']} for i in its]})
        return rows
    main = [
        {'hue': 'teal', 'spine': 'Briefing', 'type': 'para', 'text': brief},
        {'hue': 'teal', 'spine': 'Spending', 'blocks': [{'type': 'sub', 'text': 'Spending by category · tap to expand', 'right': money(c['spend']) + ' total'}, {'type': 'cats', 'rows': catrows('out')}]},
        {'hue': 'green', 'spine': 'Income', 'blocks': [{'type': 'sub', 'text': 'Where the money came from · tap to expand', 'right': money(c['income']) + ' total'}, {'type': 'cats', 'rows': catrows('in')}]},
        {'hue': 'slate', 'spine': 'Ledger', 'blocks': [{'type': 'sub', 'text': 'Every transaction, labeled', 'right': '%d in · %d out · %d moved' % (c['n_in'], c['n_out'], c['n_mv'])}, {'type': 'tx', 'items': items}]},
    ]
    side = [
        {'hue': 'teal', 'spine': 'Totals', 'type': 'kv', 'items': [['Income', money(c['income']), {'big': True}], ['Spending', money(-c['spend']), {'big': True}],
            ['Net', money(c['net'], plus=True), {'big': True}], ['Kept', '%.1f%% of income' % rate], ['Invested', money(c['invested']) + ' to M1, Robinhood'],
            ['YTD start', money(c['ytdPrev'])], ['YTD end', money(c['ytdEnd']), {'big': True}]]},
        {'hue': 'green', 'spine': 'Weekly', 'blocks': [{'type': 'sub', 'text': 'In vs out by week'}, {'type': 'cols', 'cols': c['weeks'], 'keys': ['Money in', 'Money out']}]},
        {'hue': 'red', 'spine': 'Trend', 'blocks': [{'type': 'sub', 'text': 'Running net, day by day', 'right': money(c['net'], whole=True, plus=True)},
            {'type': 'spark', 'values': c['cum'][:days], 'grid': 0, 'label': 'Running net', 'axis': [md(m + '-01'), md(m + '-%02d' % days)]}]},
        {'hue': 'teal', 'spine': '2026', 'blocks': [{'type': 'sub', 'text': 'Net by month', 'right': 'tap a month'}, {'type': 'year', 'metric': 'net', 'fmt': 'money'},
            {'type': 'goal', 'value': c['ytdEnd'], 'target': 10000, 'note': '2026 savings goal of $10,000.'}]},
    ]
    if notes: side.append({'hue': 'amber', 'spine': 'Notes', 'type': 'rows', 'items': notes})
    return main, side, rate

def build(m, F, G, L):
    y, mo = 2026, int(m[-2:]); i = mo - 1
    days = (dt.date(y, mo % 12 + 1, 1) - dt.timedelta(days=1)).day
    c, g, n = F[m], G[m], narratives.N[m]
    jobs = L[m]
    paid = [j for j in jobs if j['status'] not in ('Cancelled',)]
    notes = []
    if c['bysrc'].get('Taxi'): notes.append({'when': 'Rule', 'text': 'Square deposits under $400 are taxi fares; $400 and up is JD Meyers Productions.', 'src': 'rule'})
    if 'Moved' in {x['cat'] for x in c['items'] if x['label'] == 'Apple Savings to Apple Cash'}: notes.append({'when': 'Rule', 'text': 'Apple Savings to Apple Cash moves count as money moved, not income.', 'src': 'rule'})
    if mo <= 7: notes.append({'when': 'Fix', 'text': 'The Chase Sapphire feed duplicated this card in Origin; duplicates are removed.', 'src': 'data'})
    fbrief = ['%s closed at %s on %s in and %s out.' % (NAMES[i], money(c['net'], plus=True), money(c['income']), money(c['spend'])),
              'Biggest spending category: %s at %s. Income came from %s.' % (list(c['bycat'])[0], money(list(c['bycat'].values())[0]),
              ', '.join('%s (%s)' % (k, money(v, whole=True)) for k, v in list(c['bysrc'].items())[:3]))]
    fin_main, fin_side, rate = finance(c, m, days, fbrief, notes)
    ring = round(g['days'] / days * 100)
    cats = list(c['bycat'].items()); top = cats[:5]; other = sum(v for k, v in cats[5:])
    segs = [[k, CAT_HUE.get(k, 'slate'), round(v)] for k, v in top] + ([['Other', 'slate', round(other)]] if other > 0 else [])
    sermons_js = open(REPO + 'data/sermons-2026.js').read()
    S = [s for s in json.loads(sermons_js[sermons_js.index('['):sermons_js.rindex(']') + 1]) if s['date'][:7] == m]
    giving = c['bycat'].get('Giving', 0)
    # Sundays
    d = dt.date(y, mo, 1)
    while d.weekday() != 6: d += dt.timedelta(days=1)
    sundays = []
    while d.month == mo: sundays.append(d); d += dt.timedelta(days=7)
    byd = {s['date']: s for s in S}
    car = n['career']; stage = car['stage']

    D = {'meta': {'label': NAMES[i] + ' 2026', 'short': SHORT[i], 'mIdx': i, 'year': y, 'daysInMonth': days,
                  'prev': ['2026-%02d.html' % (mo - 1), SHORT[i - 1]] if mo > 1 else None, 'next': ['2026-%02d.html' % (mo + 1), SHORT[i + 1]]},
         'entities': ENTITIES,
         'header': {'meta': [['Period', SHORT[i] + ' 1 to %d' % days], ['Status', 'Closed'], ['YTD', money(c['ytdEnd'], whole=True)]],
                    'stats': [['Net', money(c['net'], whole=True, plus=True), c['net'] < 0], ['Income', money(c['income'], whole=True)], ['Gym days', str(g['days'])]],
                    'ring': {'pct': ring, 'text': str(ring), 'cap': 'Trained', 'sub': '%d of %d days' % (g['days'], days)},
                    'mix': {'centre': '$%.1fk' % (c['spend'] / 1000), 'segs': segs}},
         'domains': []}
    dom = D['domains']
    cards = [
        {'hue': 'teal', 'spine': 'Financial', 'title': money(c['net'], plus=True) + ' net', 'text': money(c['income']) + ' in, ' + money(c['spend']) + ' out.', 'tags': ['YTD ' + money(c['ytdEnd'], whole=True)], 'foot': ['Origin export', 'Open'], 'href': '#financial'},
        {'hue': 'green', 'spine': 'Physical', 'title': '%d gym days' % g['days'], 'text': '{:,} lb moved, {} cardio sessions, {} miles.'.format(g['volume'], g['cardioSessions'], g['miles']), 'foot': ['FitNotes', 'Open'], 'href': '#physical'},
        {'hue': 'magenta', 'spine': 'Spiritual', 'title': '%d sermon%s' % (len(S), '' if len(S) == 1 else 's'), 'text': (', '.join(sorted({s['series'] for s in S})) or 'No notes recorded') + '.', 'foot': ['CBC notes', 'Open'], 'href': '#spiritual'},
        {'hue': 'orange', 'spine': 'Career', 'title': narratives.OTS_STAGES[stage] if stage else car['paths'][0][1], 'text': first(car['brief']), 'foot': ['OTS stage %d of 8' % (stage + 1), 'Open'], 'href': '#career'},
        {'hue': 'blue', 'spine': 'Intellectual', 'title': ' + '.join(x[0] for x in n['intel']['courses']) or 'Between terms', 'text': first(n['intel']['brief']), 'foot': ['MBA', 'Open'], 'href': '#intellectual'},
        {'hue': 'amber', 'spine': 'Creative', 'title': ('%d paid job%s' % (len(paid), '' if len(paid) == 1 else 's')) if paid else 'No paid shoots', 'text': first(n['creative']['brief']), 'foot': ['Notion ledger', 'Open'], 'href': '#creative'},
    ]
    dom.append({'id': 'overview', 'label': 'Overview', 'hue': 'slate', 'mainLabel': NAMES[i] + ' at a glance', 'sideLabel': 'Key dates',
        'main': [{'hue': 'slate', 'spine': 'Briefing', 'type': 'para', 'text': n['brief']}, {'hue': 'slate', 'spine': 'Domains', 'type': 'cards', 'cards': cards}],
        'side': [{'hue': 'slate', 'spine': 'Timeline', 'type': 'rows', 'items': [{'when': a, 'text': b} for a, b in n['timeline']]},
                 {'hue': 'slate', 'spine': 'Numbers', 'type': 'kv', 'items': [['Net', money(c['net'], plus=True), {'big': True}], ['YTD', money(c['ytdEnd']), {'big': True}],
                     ['Gym', '%d days · %s lb' % (g['days'], '{:,}'.format(g['volume']))], ['Sermons', '%d of %d Sundays logged' % (len(S), len(sundays))]]},
                 {'hue': 'teal', 'spine': '2026', 'blocks': [{'type': 'sub', 'text': 'Net by month'}, {'type': 'year', 'metric': 'net', 'fmt': 'money'}]}]})
    dom.append({'id': 'financial', 'label': 'Financial', 'hue': 'teal', 'count': money(c['net'], whole=True, plus=True), 'main': fin_main, 'side': fin_side})

    runs = [{'when': md(r[0]), 'text': '%s, %s in %s (%s)%s' % (r[1], r[2], r[3], r[4], ('. ' + r[5]) if r[5] else '')} for r in g['runs']]
    phys_main = [{'hue': 'green', 'spine': 'Briefing', 'type': 'para', 'text': ['%d training days, {:,} lb of lifting volume, and %d cardio sessions covering %.1f miles.'.format(g['volume']) % (g['days'], g['cardioSessions'], g['miles']), n['phys']]},
                 {'hue': 'green', 'spine': 'Calendar', 'blocks': [{'type': 'sub', 'text': 'Training days · tap a day for the full session', 'right': '%d of %d' % (g['days'], days)},
                     {'type': 'cal', 'sessions': g['sessions'], 'days': {k: v for k, v in g['cal'].items()},
                      'legend': [['Legs', 'green'], ['Back', 'blue'], ['Chest', 'violet'], ['Shoulders', 'teal'], ['Arms', 'amber'], ['Cardio', 'red']]}]},
                 {'hue': 'violet', 'spine': 'Lifts', 'blocks': [{'type': 'sub', 'text': 'Top working sets', 'right': 'est. 1RM'}, {'type': 'rows', 'items': [{'when': t[0], 'text': t[1] + ' · ' + str(t[2]) + ' lb'} for t in g['tops']]}]}]
    if runs: phys_main.append({'hue': 'red', 'spine': 'Cardio', 'blocks': [{'type': 'sub', 'text': 'Runs and conditioning'}, {'type': 'rows', 'items': runs}]})
    dom.append({'id': 'physical', 'label': 'Physical', 'hue': 'green', 'count': g['days'], 'main': phys_main,
        'side': [{'hue': 'green', 'spine': 'Totals', 'type': 'kv', 'items': [['Days', '%d of %d' % (g['days'], days), {'big': True}], ['Volume', '{:,} lb'.format(g['volume']), {'big': True}],
                     ['Cardio', '%d sessions · %d min' % (g['cardioSessions'], g['cardioMin'])], ['Distance', '%.1f mi logged' % g['miles']]]},
                 {'hue': 'green', 'spine': '2026', 'blocks': [{'type': 'sub', 'text': 'Gym days by month', 'right': 'tap a month'}, {'type': 'year', 'metric': 'gymDays', 'fmt': 'int', 'showAll': True},
                     {'type': 'sub', 'text': 'Volume by month, lb'}, {'type': 'year', 'metric': 'volume', 'fmt': 'k'}]},
                 {'hue': 'blue', 'spine': 'Split', 'blocks': [{'type': 'sub', 'text': 'Days per muscle group'}, {'type': 'meter', 'rows': [[k, v, str(v)] for k, v in g['split'].items()]}]}]})

    series = sorted({s['series'] for s in S})
    dom.append({'id': 'spiritual', 'label': 'Spiritual', 'hue': 'magenta', 'count': len(S),
        'main': [{'hue': 'magenta', 'spine': 'Series', 'type': 'para', 'text': ('%d sermon%s logged at Calvary Baptist, from %s.' % (len(S), '' if len(S) == 1 else 's', ' and '.join(series))) if S else 'No sermon notes were recorded this month.'},
                 {'hue': 'magenta', 'spine': 'Sermons', 'type': 'sermons', 'month': m}],
        'side': [{'hue': 'magenta', 'spine': 'Attendance', 'type': 'kv', 'items': [[s.strftime('%b %-d'), byd[s.isoformat()]['title'] if s.isoformat() in byd else 'No notes', {'tag': 'Notes'} if s.isoformat() in byd else {}] for s in sundays]},
                 {'hue': 'teal', 'spine': 'Giving', 'type': 'kv', 'items': [['Tithe', money(giving) + ' to Calvary Baptist', {'big': True}]]}]})

    paths = [[p[0], p[1], {'tag': p[2]} if p[2] else {}] for p in car['paths']]
    side = [{'hue': 'orange', 'spine': 'OTS', 'blocks': [{'type': 'sub', 'text': 'Air Force OTS thread', 'right': 'stage %d of 8' % (stage + 1)},
                {'type': 'seg', 'rows': [[narratives.OTS_STAGES[stage], stage + 1, 8, '%d/8' % (stage + 1)]]},
                {'type': 'note', 'text': ' → '.join(narratives.OTS_STAGES)}]},
            {'hue': 'orange', 'spine': 'Paths', 'type': 'kv', 'items': paths}]
    if car.get('afoqt'):
        side.insert(1, {'hue': 'red', 'spine': 'AFOQT', 'blocks': [{'type': 'sub', 'text': 'Aug 31 scores', 'right': 'line = minimum'},
            {'type': 'meter', 'max': 100, 'rows': [['Verbal', 61, '61', 15], ['CSO', 41, '41'], ['Pilot', 35, '35'], ['ABM', 26, '26'], ['Academic', 26, '26'], ['Quant', 6, '6', 10]]}]})
    dom.append({'id': 'career', 'label': 'Career', 'hue': 'orange', 'count': narratives.OTS_STAGES[stage].split(' ')[0] if stage else None,
        'main': [{'hue': 'orange', 'spine': 'Briefing', 'type': 'para', 'text': car['brief']},
                 {'hue': 'red', 'spine': 'Events', 'type': 'rows', 'items': [{'when': a, 'text': b} for a, b in car['rows']]}],
        'side': side})

    it = n['intel']
    im = [{'hue': 'blue', 'spine': 'Briefing', 'type': 'para', 'text': it['brief']}]
    if it['courses']: im.append({'hue': 'blue', 'spine': 'Courses', 'type': 'cards', 'cards': [{'hue': 'blue', 'spine': x[0], 'title': x[1], 'text': x[2], 'tags': [x[3]]} for x in it['courses']]})
    im.append({'hue': 'violet', 'spine': 'Study', 'type': 'para', 'text': it['study']})
    dom.append({'id': 'intellectual', 'label': 'Intellectual', 'hue': 'blue', 'count': len(it['courses']) or None, 'main': im,
        'side': [{'hue': 'blue', 'spine': 'Program', 'type': 'kv', 'items': [['Degree', 'Online General MBA, Reh School'], ['Target', 'May 2027']]}]})

    cr = n['creative']
    TYPE_HUE = {'Wedding Photography': 'amber', 'Wedding Videography': 'orange', 'Photoshoot': 'violet', 'Drone': 'sky', 'Commercial': 'teal', 'Project': 'blue', 'Videography': 'orange'}
    jc = [{'hue': TYPE_HUE.get(j['type'], 'amber') if j['status'] != 'Cancelled' else 'slate', 'spine': j['type'].split(' ')[-1], 'date': datebox(j['date']), 'title': j['client'],
           'text': j['type'] + (' at ' + j['loc'] if j['loc'] else '') + '.', 'tags': [money(j['amt'], whole=True) if j['amt'] else j['status']], 'foot': [j['status'], '']} for j in jobs]
    cm = [{'hue': 'amber', 'spine': 'Briefing', 'type': 'para', 'text': cr['brief']}]
    if jc: cm.append({'hue': 'amber', 'spine': 'Jobs', 'type': 'cards', 'cards': jc})
    if cr['rows']: cm.append({'hue': 'slate', 'spine': 'Notes', 'type': 'rows', 'items': [{'when': a, 'text': b} for a, b in cr['rows']]})
    dom.append({'id': 'creative', 'label': 'Creative', 'hue': 'amber', 'count': len(paid), 'main': cm,
        'side': [{'hue': 'amber', 'spine': 'Business', 'type': 'kv', 'items': [['Jobs', '%d this month' % len(paid), {'big': True}],
                     ['Billed', money(sum(j['amt'] for j in paid), whole=True)], ['Landed', money(c['bysrc'].get('JDM Productions', 0)) + ' in the bank'],
                     ['Costs', money(c['bycat'].get('JDM Productions', 0))]]}]})

    rf = n['refl']
    dom.append({'id': 'reflections', 'label': 'Reflections', 'hue': 'violet', 'count': len(rf['items']),
        'main': [{'hue': 'violet', 'spine': 'Pull quote', 'type': 'para', 'text': '**' + rf['quote'] + '**'}] + [{'hue': 'violet', 'spine': a, 'type': 'para', 'text': b} for a, b in rf['items']],
        'side': [{'hue': 'violet', 'spine': 'In a line', 'type': 'para', 'text': rf['line']}, {'hue': 'slate', 'spine': 'Carry over', 'type': 'list', 'items': rf['carry']}]})
    # order to match Sep/Oct
    order = ['overview', 'financial', 'physical', 'spiritual', 'career', 'intellectual', 'creative', 'reflections']
    D['domains'] = sorted(dom, key=lambda x: order.index(x['id']))
    for x in D['domains']:
        if x.get('count') is None: x.pop('count', None)
    js = '/* %s recap data. Rendered by assets/ledger.js; built by tools/build_month.py. */\nwindow.RECAP = %s;\n' % (D['meta']['label'], json.dumps(D, ensure_ascii=True, indent=1))
    open(REPO + 'data/%s.js' % m, 'w').write(js)
    return D

if __name__ == '__main__':
    F = json.load(open(sys.argv[1])); rows = gym.load(sys.argv[2])
    months = sys.argv[4:]
    G = {m: gym.month(rows, m) for m in months}
    L = {m: ledger(sys.argv[3], m) for m in months}
    for m in months:
        build(m, F, G, L); print(m, 'ok', G[m]['days'], 'days', len(L[m]), 'jobs')
