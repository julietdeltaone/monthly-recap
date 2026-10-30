"""Emit data/2026-09.js and data/2026-10.js from calc.json plus narrative."""
import json, datetime as dt
S = '/tmp/claude-0/-home-claude/e2eb66b9-6aee-558a-b3a4-c4e64327d063/scratchpad/'
REPO = '/home/claude/monthly-recap/'
C = json.load(open(S + 'calc.json'))

def money(n, whole=False, plus=False):
    s = ('{:,.0f}' if whole else '{:,.2f}').format(abs(n))
    sign = '−' if n < 0 else ('+' if plus and n > 0 else '')
    return sign + '$' + s

def md(iso):
    d = dt.date.fromisoformat(iso); return d.strftime('%b %-d')

def datebox(iso):
    d = dt.date.fromisoformat(iso); return [d.strftime('%a').upper(), str(d.day), d.strftime('%b').upper()]

SRC_HUE = {'Clarkson payroll': 'emerald', 'JDM Productions': 'orange', 'Taxi': 'amber', 'Guard pay': 'green', 'Uber': 'slate', 'Interest': 'teal', 'Cashback': 'sky', 'Other': 'violet'}
CAT_HUE = {'Phone & devices': 'blue', 'Groceries': 'green', 'Dining & coffee': 'amber', 'Shopping': 'violet', 'Subscriptions': 'teal',
           'Giving': 'magenta', 'Health': 'red', 'JDM Productions': 'orange', 'Tesla': 'sky', 'Personal care': 'slate',
           'Entertainment': 'slate', 'Fees & travel': 'slate', 'Other': 'slate'}

ENTITIES = {
    'Potsdam': 'place', 'Canton': 'place', 'Fort Drum': 'place', 'Camp Smith': 'place', 'Ives Park': 'place',
    'Shindigz on the River': 'place', 'West Point': 'place', 'Russell': 'place',
    'Clarkson University': 'school', 'Clarkson': 'school', 'Lewis School': 'school', 'Reh School': 'school', 'UMGC': 'school',
    'Calvary Baptist': 'church', 'CBC': 'church',
    'HHC': 'group', '101st Cavalry': 'group', '212th': 'group', '27th IBCT': 'group',
    'JD Meyers Productions': 'org', 'JDM': 'org', 'BRL Entertainment': 'org', 'Air Force': 'org', 'B&H Photo': 'org',
}

def finance(m, brief, notes, upto=None):
    c = C[m]
    upto = upto or len(c['cum'])
    items = []
    for i in sorted(c['items'], key=lambda x: (x['date'], -abs(x['amt']))):
        items.append({'date': md(i['date']), 'label': i['label'], 'sub': i['cat'] + ' · ' + i['acct'], 'amt': i['amt'], 'kind': i['kind']})
    rate = (c['net'] / c['income'] * 100) if c['income'] else 0
    def catrows(kind):
        tot = c['bycat'] if kind == 'out' else c['bysrc']
        rows = []
        for k, v in tot.items():
            if abs(v) < 0.005: continue
            its = [i for i in c['items'] if i['kind'] == kind and i['cat'] == k]
            its.sort(key=lambda i: -abs(i['amt']))
            rows.append({'name': k, 'hue': CAT_HUE.get(k, 'green') if kind == 'out' else SRC_HUE.get(k, 'green'), 'amt': v,
                         'items': [{'date': md(i['date']), 'label': i['label'], 'sub': i['acct'], 'amt': i['amt']} for i in its]})
        return rows
    main = [
        {'hue': 'teal', 'spine': 'Briefing', 'type': 'para', 'text': brief},
        {'hue': 'teal', 'spine': 'Spending', 'blocks': [
            {'type': 'sub', 'text': 'Spending by category · tap to expand', 'right': money(c['spend']) + ' total'},
            {'type': 'cats', 'rows': catrows('out')}]},
        {'hue': 'green', 'spine': 'Income', 'blocks': [
            {'type': 'sub', 'text': 'Where the money came from · tap to expand', 'right': money(c['income']) + ' total'},
            {'type': 'cats', 'rows': catrows('in')}]},
        {'hue': 'slate', 'spine': 'Ledger', 'blocks': [
            {'type': 'sub', 'text': 'Every transaction, labeled', 'right': '%d in · %d out · %d moved' % (c['n_in'], c['n_out'], c['n_mv'])},
            {'type': 'tx', 'items': items}]},
    ]
    side = [
        {'hue': 'teal', 'spine': 'Totals', 'type': 'kv', 'items': [
            ['Income', money(c['income']), {'big': True}],
            ['Spending', money(-c['spend']), {'big': True}],
            ['Net', money(c['net'], plus=True), {'big': True}],
            ['Kept', '%.1f%% of income' % rate],
            ['Invested', money(c['invested']) + ' to M1, Robinhood'],
            ['YTD start', money(c['ytdPrev'])],
            ['YTD end', money(c['ytdEnd']), {'big': True}],
        ]},
        {'hue': 'green', 'spine': 'Weekly', 'blocks': [
            {'type': 'sub', 'text': 'In vs out by week'},
            {'type': 'cols', 'cols': c['weeks'], 'keys': ['Money in', 'Money out']}]},
        {'hue': 'red', 'spine': 'Trend', 'blocks': [
            {'type': 'sub', 'text': 'Running net, day by day', 'right': money(c['net'], whole=True, plus=True)},
            {'type': 'spark', 'values': c['cum'][:upto], 'grid': 0, 'label': 'Running net', 'axis': [md(m + '-01'), md(m + '-%02d' % upto)]}]},
        {'hue': 'teal', 'spine': '2026', 'blocks': [
            {'type': 'sub', 'text': 'Net by month', 'right': 'tap a month'},
            {'type': 'year', 'metric': 'net', 'fmt': 'money'},
            {'type': 'goal', 'value': c['ytdEnd'], 'target': 10000, 'note': '2026 savings goal of $10,000 cleared in May. YTD shown is the chained figure.'}]},
        {'hue': 'amber', 'spine': 'Notes', 'type': 'rows', 'items': notes},
    ]
    return main, side, rate

def mix(m, n=5):
    cats = list(C[m]['bycat'].items())
    top = cats[:n]; other = sum(v for k, v in cats[n:])
    segs = [[k, CAT_HUE.get(k, 'slate'), round(v)] for k, v in top]
    if other > 0: segs.append(['Other', 'slate', round(other)])
    return segs

def gym_cal(m, labelmap, events=None, fix=None):
    g = C[m]['gym']; days = {}
    order = ['Legs', 'Back', 'Chest', 'Shoulders', 'Biceps', 'Triceps', 'Abs', 'Cardio']
    hue = {'Legs': 'green', 'Back': 'blue', 'Chest': 'violet', 'Shoulders': 'teal', 'Biceps': 'amber', 'Triceps': 'amber', 'Abs': 'slate', 'Cardio': 'red'}
    for d, cats in g['dayCats'].items():
        main = [x for x in order if x in cats]
        lab = labelmap.get(d) or main[0]
        days[int(d[-2:])] = [lab, hue.get(main[0], 'slate')]
    return days

def sessions(m):
    ren = {'Hrp Emom': 'Hand-release push-up EMOM', 'Running (Outdoor)': 'Outdoor run', 'Running (Treadmill)': 'Treadmill run'}
    return {str(d): [[ren.get(e, e), v] for e, v in x] for d, x in C[m]['gym']['sessions'].items()}

def write(m, data):
    js = ('/* ' + data['meta']['label'] + ' recap data. Rendered by assets/ledger.js; edit values here, not markup. */\n'
          'window.RECAP = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    assert '—' not in js, 'raw em dash in ' + m
    open(REPO + 'data/' + m + '.js', 'w').write(js)

# =====================================================================
# SEPTEMBER
# =====================================================================
m = '2026-09'; c = C[m]; g = c['gym']
fin_main, fin_side, rate = finance(m, [
    'September closed at ' + money(c['net'], plus=True) + ' on ' + money(c['income']) + ' in and ' + money(c['spend']) + ' out. The red is one deliberate move: '
    'the ' + money(833.25) + ' Verizon payoff on Sep 9 that cleared the iPhone 17 Pro so it can go toward an Apple trade-in and the new leasing route. Without it, spending was ' + money(c['spend'] - 833.25) + ' and the month nets ' + money(c['net'] + 833.25, plus=True) + '.',
    'Income was all base pay: two Clarkson checks, a small Guard deposit, and Uber. JDM shoot money for September (Mandy Dow, Kayla Bryson) came through Venmo and only landed in the bank on Oct 6, so it counts in October.',
], [
    {'when': 'Sep 9', 'text': 'Verizon payoff, ' + money(833.25) + '. Phone cleared for trade-in toward the iPhone Duo, due Nov 6 to 13 on an Apple lease.', 'src': 'one-off'},
    {'when': 'Sep 9', 'text': 'On Black backpack, ' + money(279) + '.', 'src': 'one-off'},
    {'when': 'Sep 1', 'text': 'Apple Savings to Apple Cash move of ' + money(217.16) + ' counted as money moved, not income.', 'src': 'rule'},
    {'when': 'Note', 'text': 'The JDM Venmo account is not linked to Origin. Shoot payments count when they land in the bank.', 'src': 'gap'},
    {'when': 'Sep', 'text': 'YTD carried from the corrected August close of ' + money(17650.47) + '.', 'src': 'chain'},
])
ring_pct = round(g['days'] / 30 * 100)
SEP = {
 'meta': {'label': 'September 2026', 'short': 'Sep', 'mIdx': 8, 'year': 2026, 'daysInMonth': 30,
          'prev': ['2026-08.html', 'Aug'], 'next': ['2026-10.html', 'Oct']},
 'entities': ENTITIES,
 'header': {
   'meta': [['Period', 'Sep 1 to 30'], ['Status', 'Closed'], ['YTD', money(c['ytdEnd'], whole=True)]],
   'stats': [['Net', money(c['net'], whole=True, plus=True), c['net'] < 0], ['Income', money(c['income'], whole=True)], ['Gym days', str(g['days'])]],
   'ring': {'pct': ring_pct, 'text': str(ring_pct), 'cap': 'Trained', 'sub': '%d of 30 days' % g['days']},
   'mix': {'centre': '$%.1fk' % (c['spend'] / 1000), 'segs': mix(m)}},
 'footnote': 'Sources: Origin export (Oct 30), FitNotes export, CBC service notes, Notion Projects & Ledger, Moodle and email handoff (Oct 30).',
 'domains': []}

SEP['domains'].append({'id': 'overview', 'label': 'Overview', 'hue': 'slate', 'mainLabel': 'September at a glance', 'sideLabel': 'Key dates',
 'main': [
  {'hue': 'slate', 'spine': 'Briefing', 'type': 'para', 'text': [
    'September was the first full month of the new rhythm: Clarkson by day, three MBA courses at night, and the gym nearly every day in between. Pickup soccer and frisbee faded out in the first week, which freed the evenings for class.',
    'Money ran negative on purpose (the Verizon payoff), training hit a high of 28 days, CBC started a Fruit of the Spirit series in Galatians 5, and the OTS path settled into a wait: retest the AFOQT quant section after the 90-day window.']},
  {'hue': 'slate', 'spine': 'Domains', 'type': 'cards', 'cards': [
    {'hue': 'teal', 'spine': 'Financial', 'title': money(c['net'], plus=True) + ' net', 'text': money(c['income']) + ' in, ' + money(c['spend']) + ' out. Verizon payoff drives the red.', 'tags': ['YTD ' + money(c['ytdEnd'], whole=True)], 'foot': ['Origin export', 'Open'], 'href': '#financial'},
    {'hue': 'green', 'spine': 'Physical', 'title': '%d gym days' % g['days'], 'text': '{:,} lb moved, {} cardio sessions, {} miles. Nine-mile run on Sep 6.'.format(g['volume'], g['cardioSessions'], g['miles']), 'tags': ['28 of 30 days'], 'foot': ['FitNotes', 'Open'], 'href': '#physical'},
    {'hue': 'magenta', 'spine': 'Spiritual', 'title': '3 sermons', 'text': 'Galatians 5 series opens: liberty, love, joy.', 'tags': ['Fruit of the Spirit'], 'foot': ['CBC notes', 'Open'], 'href': '#spiritual'},
    {'hue': 'blue', 'spine': 'Intellectual', 'title': 'MBA term + OTS', 'text': 'FN 608, IS 606, OM 603 under way. Voucher route for the AFOQT retest set through the education center.', 'tags': ['Retest window opens Nov 29'], 'foot': ['Moodle, email', 'Open'], 'href': '#intellectual'},
    {'hue': 'amber', 'spine': 'Creative', 'title': '2 shoots', 'text': 'Mandy Dow and Kayla Bryson portraits. Megan Eddy films delivered.', 'tags': ['Tomford exchange closed'], 'foot': ['Notion ledger', 'Open'], 'href': '#creative'},
    {'hue': 'violet', 'spine': 'Reflections', 'title': 'The routine month', 'text': 'Nothing dramatic, and that was the point.', 'foot': ['5 notes', 'Open'], 'href': '#reflections'},
  ]}],
 'side': [
  {'hue': 'slate', 'spine': 'Timeline', 'type': 'rows', 'items': [
    {'when': 'Sep 2', 'text': 'Mandy Dow portraits at Ives Park'},
    {'when': 'Sep 6', 'text': 'Nine-mile run, 1:19:03'},
    {'when': 'Sep 9', 'text': 'Verizon payoff for the iPhone 17 Pro'},
    {'when': 'Sep 11', 'text': 'Told TSgt Powers the retest route is in motion'},
    {'when': 'Sep 13', 'text': 'Galatians 5 series begins at CBC'},
    {'when': 'Sep 19', 'text': 'Fastest 5K of the month, 23:39'},
    {'when': 'Sep 22', 'text': 'Tomford service exchange closed with a lens'},
    {'when': 'Sep 26', 'text': 'Kayla Bryson senior portraits'},
    {'when': 'Sep 27', 'text': "James's Bonfire Social Dance"},
  ]},
  {'hue': 'slate', 'spine': 'Numbers', 'type': 'kv', 'items': [
    ['Net', money(c['net'], plus=True), {'big': True}], ['YTD', money(c['ytdEnd']), {'big': True}],
    ['Gym', '%d days · %s lb' % (g['days'], '{:,}'.format(g['volume']))], ['Sermons', '3 of 4 Sundays logged'], ['Drill', 'None this month']]},
  {'hue': 'teal', 'spine': '2026', 'blocks': [{'type': 'sub', 'text': 'Net by month'}, {'type': 'year', 'metric': 'net', 'fmt': 'money'}]},
 ]})

SEP['domains'].append({'id': 'financial', 'label': 'Financial', 'hue': 'teal', 'count': money(c['net'], whole=True, plus=True), 'main': fin_main, 'side': fin_side})

SEP['domains'].append({'id': 'physical', 'label': 'Physical', 'hue': 'green', 'count': g['days'],
 'main': [
  {'hue': 'green', 'spine': 'Briefing', 'type': 'para', 'text': [
    '28 training days out of 30. Lifting ran a steady push, pull, legs rotation with cardio stacked on 19 of those days, and pickup soccer and frisbee wound down by the first week of September.',
    'Cardio is where the progress shows: zone 2 work settled at a lower heart rate, the 5K came down to 23:39 outdoors on Sep 19, and a nine-mile long run on Sep 6 went without knee pain.']},
  {'hue': 'green', 'spine': 'Calendar', 'blocks': [
    {'type': 'sub', 'text': 'Training days · tap a day for the full session', 'right': '%d of 30' % g['days']},
    {'type': 'cal', 'sessions': sessions(m), 'days': gym_cal(m, {'2026-09-06': '9 mi run', '2026-09-12': '5K', '2026-09-19': '5K', '2026-09-26': '5K'}),
     'legend': [['Legs', 'green'], ['Back', 'blue'], ['Chest', 'violet'], ['Shoulders', 'teal'], ['Arms', 'amber'], ['Run', 'red']]}]},
  {'hue': 'violet', 'spine': 'Lifts', 'blocks': [
    {'type': 'sub', 'text': 'Top working sets'},
    {'type': 'rows', 'items': [
      {'when': 'Bench', 'text': '205 x 5 (Sep 21), 175 x 13 (Sep 7)'},
      {'when': 'Deadlift', 'text': '315 x 7 (Sep 22)'},
      {'when': 'Squat', 'text': '225 x 5 (Sep 2), Smith 185 x 9 (Sep 30)'},
      {'when': 'Leg press', 'text': '315 x 15 (Sep 23)'},
      {'when': 'Press', 'text': 'Standing barbell 145 x 2, 135 x 5 (Sep 11)'},
      {'when': 'Pulldown', 'text': '162.5 x 9 (Sep 25), 160 x 10 (Sep 18)'},
      {'when': 'Incline DB', 'text': '150 x 6 total (Sep 17), 140 x 10 (Sep 24)'},
    ]}]},
  {'hue': 'red', 'spine': 'Cardio', 'blocks': [
    {'type': 'sub', 'text': 'Runs and conditioning'},
    {'type': 'rows', 'items': [
      {'when': 'Sep 6', 'text': 'Outdoor 9 mi in 1:19:03 (8:47 per mile). Two gels, one hydration stop, no knee pain.'},
      {'when': 'Sep 12', 'text': 'Outdoor 5K, 31:20, held in zone 2'},
      {'when': 'Sep 16', 'text': 'Zone 2 5K, 29:41 at speed 5, 146 average heart rate'},
      {'when': 'Sep 17', 'text': 'Treadmill 5K, 25:20'},
      {'when': 'Sep 19', 'text': 'Outdoor 5K, 23:39, best of the month (7:37 per mile)'},
      {'when': 'Sep 26', 'text': 'Outdoor 5K, 27:15 with one hill, 159 average'},
      {'when': 'Stairs', 'text': 'Five 20-minute sessions at level 7, 144 to 153 average heart rate'},
    ]}]},
 ],
 'side': [
  {'hue': 'green', 'spine': 'Totals', 'type': 'kv', 'items': [
    ['Days', '%d of 30' % g['days'], {'big': True}], ['Volume', '{:,} lb'.format(g['volume']), {'big': True}],
    ['Cardio', '%d sessions · %d min' % (g['cardioSessions'], g['cardioMin'])], ['Distance', '%.1f mi logged' % g['miles']], ['Aug ref', '10 days · 72,905 lb']]},
  {'hue': 'green', 'spine': '2026', 'blocks': [
    {'type': 'sub', 'text': 'Gym days by month', 'right': 'tap a month'},
    {'type': 'year', 'metric': 'gymDays', 'fmt': 'int', 'showAll': True},
    {'type': 'sub', 'text': 'Volume by month, lb'},
    {'type': 'year', 'metric': 'volume', 'fmt': 'k'}]},
  {'hue': 'blue', 'spine': 'Split', 'blocks': [
    {'type': 'sub', 'text': 'Days per muscle group'},
    {'type': 'meter', 'rows': [[k, v, str(v)] for k, v in g['split'].items()]}]},
  {'hue': 'red', 'spine': '5K', 'blocks': [
    {'type': 'sub', 'text': '5K times, minutes', 'right': 'lower is better'},
    {'type': 'spark', 'values': [31.33, 29.68, 25.33, 23.65, 28.33, 27.25], 'label': '5K times', 'axis': ['Sep 12', 'Sep 26']},
    {'type': 'note', 'text': 'Mix of zone 2 and effort runs; Sep 19 was the all-out effort.'}]},
  {'hue': 'slate', 'spine': 'Sports', 'type': 'para', 'text': 'Pickup soccer and frisbee tried to stretch into fall but were done by the first week of September. Evening classes took the slot.'},
 ]})

SEP['domains'].append({'id': 'spiritual', 'label': 'Spiritual', 'hue': 'magenta', 'count': 3,
 'main': [
  {'hue': 'magenta', 'spine': 'Series', 'type': 'para', 'text': [
    'Brad opened a series on the fruit of the Spirit from Galatians 5, paired with church small groups working through the same chapter. September covered the groundwork (freedom in Christ), then love, then joy.',
    'Notes were recorded for Sep 13, 20, and 27. There are no notes for Sep 6.']},
  {'hue': 'magenta', 'spine': 'Sermons', 'type': 'sermons', 'month': '2026-09'}],
 'side': [
  {'hue': 'magenta', 'spine': 'Attendance', 'type': 'kv', 'items': [
    ['Sep 6', 'No notes recorded'], ['Sep 13', 'Liberty', {'tag': 'Notes'}], ['Sep 20', 'Love', {'tag': 'Notes'}], ['Sep 27', 'Joy', {'tag': 'Notes'}]]},
  {'hue': 'violet', 'spine': 'Series', 'blocks': [
    {'type': 'sub', 'text': 'Fruit of the Spirit covered', 'right': '2 of 9'},
    {'type': 'seg', 'rows': [['Covered', 2, 9, 'Love, joy']]},
    {'type': 'note', 'text': 'Remaining: peace, patience, kindness, goodness, faithfulness, gentleness, self-control.'}]},
  {'hue': 'teal', 'spine': 'Giving', 'type': 'kv', 'items': [['Tithe', money(250) + ' to Calvary Baptist (Sep 10)', {'big': True}]]},
  {'hue': 'amber', 'spine': 'Habits', 'type': 'para', 'text': 'Keeping a daily Bible reading plan and a YouVersion Bible app streak alongside Sunday notes.'},
 ]})

SEP['domains'].append({'id': 'intellectual', 'label': 'Intellectual', 'hue': 'blue', 'count': 3,
 'main': [
  {'hue': 'blue', 'spine': 'Briefing', 'type': 'para', 'text': [
    'The fall MBA term ran three courses at once through the Reh School: FN 608 Financial Management, IS 606 Business Information Systems, and OM 603 Decision Analysis. Evening classes replaced pickup sports.',
    'On the Air Force side, the AFOQT quant score of 6 (minimum 10) set the month’s task: find the retest voucher route and wait out the 90 days. The answer came back that Guard members get vouchers through a base education center, not the recruiter.']},
  {'hue': 'blue', 'spine': 'Courses', 'type': 'cards', 'cards': [
    {'hue': 'blue', 'spine': 'FN 608', 'title': 'Financial Management', 'text': 'Feng. Weekly assignments on Coca-Cola building toward a final report.', 'tags': ['Report 60%']},
    {'hue': 'blue', 'spine': 'IS 606', 'title': 'Business Information Systems', 'text': 'Chaudhry. Week 2 and 3 quizzes at 100%, first case study 90%. The Week 4 case study was missed.', 'tags': ['Strict AI policy']},
    {'hue': 'blue', 'spine': 'OM 603', 'title': 'Decision Analysis & SC Modeling', 'text': 'Bowman. Paper 1, Production Yahtzee, scored 97.33%.', 'tags': ['Paper 1 97%']},
  ]},
  {'hue': 'red', 'spine': 'OTS', 'type': 'rows', 'items': [
    {'when': 'Aug 31', 'text': 'AFOQT at Pearson in Watertown. Verbal 61, quant 6 against a minimum of 10. Everything else passed.'},
    {'when': 'Sep 8', 'text': 'TSgt Powers (318th Recruiting Squadron) confirmed Guard and Reserve members get retest vouchers through a base education center.'},
    {'when': 'Sep 11', 'text': 'Replied to Powers that the retest route is in motion.'},
    {'when': 'Sep', 'text': 'DD-368 conditional release complete and uploaded, routed through SSG Wilson.'},
  ]},
  {'hue': 'teal', 'spine': 'Work', 'type': 'rows', 'items': [
    {'text': 'Built tools around tasks at the Lewis School: Student Hours Tracker, PT meeting minutes, inventory, and the receipt intake app.'},
    {'text': 'Took over DPT White Coat ceremony planning (Dec 11, Old Main) solo and started a CRM for it.'},
    {'text': 'Started a discovery plan for a possible Claude organizational license at the Lewis School.'},
  ]},
 ],
 'side': [
  {'hue': 'red', 'spine': 'AFOQT', 'blocks': [
    {'type': 'sub', 'text': 'Aug 31 scores', 'right': 'line = minimum'},
    {'type': 'meter', 'max': 100, 'rows': [['Verbal', 61, '61', 15], ['CSO', 41, '41'], ['Pilot', 35, '35'], ['ABM', 26, '26'], ['Academic', 26, '26'], ['Quant', 6, '6', 10]]}]},
  {'hue': 'blue', 'spine': 'Ahead', 'type': 'kv', 'items': [
    ['Retest', 'Window opens after Nov 29'], ['Board', '27OTS01R, Jan 2027'], ['Guard', 'No drill in September']]},
 ]})

SEP['domains'].append({'id': 'creative', 'label': 'Creative', 'hue': 'amber', 'count': 2,
 'main': [
  {'hue': 'amber', 'spine': 'Briefing', 'type': 'para', 'text': [
    'Two paid portrait sessions, and the last of the August wedding work closed out. Megan Eddy’s films were delivered and the family downloaded all seven videos on Sep 19; the ' + money(150) + ' refund for the camera failure was handled in August.',
    'The Julia Tomford service exchange from her 2022 wedding film finally closed on Sep 22 when she handed over a telephoto lens. Nothing is owed either way.']},
  {'hue': 'amber', 'spine': 'Shoots', 'type': 'cards', 'cards': [
    {'hue': 'amber', 'spine': 'Portraits', 'date': datebox('2026-09-02'), 'title': 'Justin & Mandy Dow', 'text': 'Portrait session at Ives Park. Photos delivered Sep 5.', 'tags': ['$150', 'Venmo'], 'foot': ['JDM-2026-16', 'Paid']},
    {'hue': 'amber', 'spine': 'Senior', 'date': datebox('2026-09-26'), 'title': 'Kayla Bryson', 'text': 'Senior portraits. Booked from a website inquiry on Sep 18; gallery delivered Oct 2.', 'tags': ['$150', 'Venmo'], 'foot': ['JDM-2026-19', 'Paid']},
    {'hue': 'orange', 'spine': 'Delivery', 'date': datebox('2026-09-19'), 'title': 'Megan Eddy films', 'text': 'All seven videos downloaded by the family. The August refund closed the incident.', 'tags': ['Delivered'], 'foot': ['JDM-2026-04', 'Closed']},
    {'hue': 'orange', 'spine': 'Exchange', 'date': datebox('2026-09-22'), 'title': 'Julia Tomford', 'text': 'Telephoto lens received; 2022 service exchange settled.', 'tags': ['Closed'], 'foot': ['JDM-2022-01', 'Settled']},
  ]},
  {'hue': 'slate', 'spine': 'Pipeline', 'type': 'rows', 'items': [
    {'when': 'Sep 8', 'text': 'Kayley Stets, family session for Oct 10. Cancelled Sep 22 for a family emergency.'},
    {'when': 'Sep 14', 'text': 'Nina Rourke, 2027 wedding in Hogansburg. Went cold after travel and deposit questions.'},
    {'when': 'Sep 16', 'text': 'Josue Bernal signed for Oct 17 proposal coverage at Cranberry Lake.'},
    {'when': 'Sep 18', 'text': 'Harper Foley, harp recital photos. Went cold; dead.'},
    {'when': 'Sep 29', 'text': 'On Black founder asked about a paid backpack content collaboration.'},
  ]},
 ],
 'side': [
  {'hue': 'amber', 'spine': 'Business', 'type': 'kv', 'items': [
    ['Shoots', '2 paid portrait sessions', {'big': True}], ['Earned', '$300 billed, paid by Venmo'], ['Delivered', 'Megan Eddy films (Sep 19)'], ['Costs', money(C[m]['bycat'].get('JDM Productions', 0)) + ' (ads, Adobe, Pixieset)']]},
  {'hue': 'orange', 'spine': 'Funnel', 'blocks': [
    {'type': 'sub', 'text': 'September inquiries'},
    {'type': 'meter', 'max': 4, 'rows': [['Inquiries', 4, '4'], ['Booked', 1, '1'], ['Cancelled', 1, '1'], ['Cold', 2, '2']]}]},
  {'hue': 'violet', 'spine': 'Projects', 'type': 'rows', 'items': [
    {'text': "RSVP dashboard for James's Bonfire Social Dance (Sep 27)."},
    {'text': "Started a tracker app for David's Hayride at the Zoovalls."},
    {'text': 'Started testing WeddingPro as a lead source.'}]},
 ]})

SEP['domains'].append({'id': 'reflections', 'label': 'Reflections', 'hue': 'violet', 'count': 5,
 'main': [
  {'hue': 'violet', 'spine': 'Pull quote', 'type': 'para', 'text': '**A quiet month that held.** No AT, no exam, no wedding. Just the routine, repeated 30 times.'},
  {'hue': 'violet', 'spine': 'a. Routine', 'type': 'para', 'text': 'August was the stress test. September was the baseline: work, class, gym, church, repeat. Twenty-eight gym days is what the routine looks like when nothing interrupts it.'},
  {'hue': 'violet', 'spine': 'b. Phone', 'type': 'para', 'text': 'The month went negative by choice. Paying off the iPhone 17 Pro breaks the yearly Verizon upgrade cycle and moves phone and watch onto Apple leases. Same cost on paper, more flexibility, and the trade-in value gets used instead of left on the table.'},
  {'hue': 'violet', 'spine': 'c. Clean up', 'type': 'para', 'text': 'Two loose ends closed: the Megan Eddy films reached the family and the Tomford exchange settled with a lens. Owning the August camera failure plainly is what made the delivery land well.'},
  {'hue': 'violet', 'spine': 'd. Waiting', 'type': 'para', 'text': 'OTS is a waiting game for now. The retest cannot happen before the 90-day window, so the useful work is the math, not the email.'},
  {'hue': 'violet', 'spine': 'e. October', 'type': 'para', 'text': 'Get the AFOQT voucher in motion, run PT Month at work, close strong in all three courses, and land the Oct 3 wedding shoot.'},
 ],
 'side': [
  {'hue': 'violet', 'spine': 'In a line', 'type': 'para', 'text': 'The routine month: consistent, a little red, nothing dropped.'},
  {'hue': 'slate', 'spine': 'Carry over', 'type': 'list', 'items': ['AFOQT voucher and retest seat', 'Final stretch of three MBA courses', 'Ken & TaShell wedding, Oct 3', 'iPhone Duo arrival, Nov 6 to 13']},
 ]})

write(m, SEP)

# =====================================================================
# OCTOBER (through Oct 30)
# =====================================================================
m = '2026-10'; c = C[m]; g = C[m]['gym']
g['miles'] = round(g['miles'] - 1.5 * 0.621371 + 1.5, 1)  # Oct 30 entry logged as km; it was the 1.5 mi agility run
jdm_in = c['bysrc'].get('JDM Productions', 0); jdm_out = c['bycat'].get('JDM Productions', 0)
fin_main, fin_side, rate = finance(m, [
    'October, through the 30th: ' + money(c['income']) + ' in, ' + money(c['spend']) + ' out, ' + money(c['net'], plus=True) + ' net. Three Clarkson checks landed in one month, and side income stacked on top.',
    'JD Meyers Productions brought in ' + money(jdm_in) + ' (the Ken & TaShell shoot through Square plus the Venmo batch for Mandy Dow and Kayla Bryson) and spent ' + money(jdm_out) + ', mostly the headshot studio kit from B&H. Taxi fares added ' + money(c['bysrc'].get('Taxi', 0)) + '. No Guard pay yet; the October drill pays in November.',
], [
    {'when': 'Oct 13', 'text': 'B&H Photo, ' + money(594.35) + ': backdrop, one light, reflector, and softbox for the new headshot studio.', 'src': 'JDM'},
    {'when': 'Oct 5', 'text': 'Square payout of ' + money(1135.92) + ' for Ken & TaShell, after Square fees on the ' + money(1175, whole=True) + ' invoice.', 'src': 'JDM'},
    {'when': 'Oct 6', 'text': 'Venmo batch of ' + money(290.85) + ' covers Mandy Dow and Kayla Bryson.', 'src': 'JDM'},
    {'when': 'Oct 12', 'text': 'Four Higgsfield refunds totaling ' + money(72.64) + ' net against subscriptions.', 'src': 'refund'},
    {'when': 'Oct 4', 'text': 'Apple Savings to Apple Cash move of ' + money(69.33) + ' counted as money moved, not income.', 'src': 'rule'},
    {'when': 'Oct', 'text': 'John Coogan’s ' + money(50) + ' deposit sits in the JDM Venmo account, which Origin cannot see. It counts when it lands in the bank.', 'src': 'gap'},
    {'when': 'Oct 31', 'text': 'Month is open through the 30th. Final day to be added at close.', 'src': 'open'},
], upto=30)
ring_pct = round(g['days'] / 30 * 100)
OCT = {
 'meta': {'label': 'October 2026', 'short': 'Oct', 'mIdx': 9, 'year': 2026, 'daysInMonth': 31,
          'prev': ['2026-09.html', 'Sep'], 'next': None},
 'entities': ENTITIES,
 'header': {
   'meta': [['Period', 'Oct 1 to 30'], ['Status', 'Open'], ['YTD', money(c['ytdEnd'], whole=True)]],
   'stats': [['Net', money(c['net'], whole=True, plus=True), c['net'] < 0], ['Income', money(c['income'], whole=True)], ['Gym days', str(g['days'])]],
   'ring': {'pct': ring_pct, 'text': str(ring_pct), 'cap': 'Trained', 'sub': '%d of 30 days' % g['days']},
   'mix': {'centre': '$%.1fk' % (c['spend'] / 1000), 'segs': mix(m)}},
 'footnote': 'Through Oct 30. Sources: Origin export (Oct 30), FitNotes export, CBC service notes, Notion Projects & Ledger, Moodle and email handoff (Oct 30).',
 'domains': []}

OCT['domains'].append({'id': 'overview', 'label': 'Overview', 'hue': 'slate', 'mainLabel': 'October at a glance', 'sideLabel': 'Key dates',
 'main': [
  {'hue': 'slate', 'spine': 'Briefing', 'type': 'para', 'text': [
    'October was the busiest month of the fall: a wedding shoot on the 3rd, PT Month at work, the headshot studio launch, a drill weekend at Camp Smith screening Soldiers for deployment, and the sheriff’s deputy agility test on the 30th. The MBA term is now in its last two weeks.',
    'Money came back strong at ' + money(c['net'], plus=True) + '. The AFOQT retest is booked for Nov 30 at Fort Drum, and the Galatians series reached patience and kindness.']},
  {'hue': 'slate', 'spine': 'Domains', 'type': 'cards', 'cards': [
    {'hue': 'teal', 'spine': 'Financial', 'title': money(c['net'], plus=True) + ' net', 'text': money(c['income']) + ' in, ' + money(c['spend']) + ' out. JDM, taxi, and three Clarkson checks.', 'tags': ['YTD ' + money(c['ytdEnd'], whole=True)], 'foot': ['Origin export', 'Open'], 'href': '#financial'},
    {'hue': 'green', 'spine': 'Physical', 'title': '%d gym days' % g['days'], 'text': 'Agility test on Oct 30: 1.5 miles in 10:35, 39 sit-ups. Zone 2 pace keeps climbing.', 'tags': ['Sheriff agility test'], 'foot': ['FitNotes', 'Open'], 'href': '#physical'},
    {'hue': 'magenta', 'spine': 'Spiritual', 'title': '3 sermons', 'text': 'Peace, patience, and kindness. Oct 25 missed for drill.', 'tags': ['Fruit of the Spirit'], 'foot': ['CBC notes', 'Open'], 'href': '#spiritual'},
    {'hue': 'blue', 'spine': 'Intellectual', 'title': 'Retest booked', 'text': 'AFOQT Nov 30 at Fort Drum. IS 606 at 92.4%, OM 603 at 97.1%.', 'tags': ['Board Jan 25, 2027'], 'foot': ['Moodle, email', 'Open'], 'href': '#intellectual'},
    {'hue': 'amber', 'spine': 'Creative', 'title': 'Studio launched', 'text': 'Ken & TaShell wedding shoot, headshot studio kit, first studio sessions.', 'tags': ['Studio from $195'], 'foot': ['Notion ledger', 'Open'], 'href': '#creative'},
    {'hue': 'violet', 'spine': 'Reflections', 'title': 'Full calendar', 'text': 'Everything at once, and it held.', 'foot': ['5 notes', 'Open'], 'href': '#reflections'},
  ]}],
 'side': [
  {'hue': 'slate', 'spine': 'Timeline', 'type': 'rows', 'items': [
    {'when': 'Oct 3', 'text': 'Ken & TaShell wedding at Shindigz on the River'},
    {'when': 'Oct 8', 'text': 'PT Month launched for the PT cohorts'},
    {'when': 'Oct 11', 'text': 'Cancelled the Bernal shoot, refunded in full'},
    {'when': 'Oct 13', 'text': 'Headshot studio kit from B&H Photo'},
    {'when': 'Oct 20', 'text': 'AFOQT retest seat confirmed for Nov 30'},
    {'when': 'Oct 23', 'text': 'Drill weekend at Camp Smith, Oct 23 to 25'},
    {'when': 'Oct 27', 'text': 'Aim High portal check: 4 of 21 tasks done'},
    {'when': 'Oct 30', 'text': 'Sheriff’s deputy agility test'},
  ]},
  {'hue': 'slate', 'spine': 'Numbers', 'type': 'kv', 'items': [
    ['Net', money(c['net'], plus=True), {'big': True}], ['YTD', money(c['ytdEnd']), {'big': True}],
    ['Gym', '%d days · %s lb' % (g['days'], '{:,}'.format(g['volume']))], ['Sermons', '3 of 4 Sundays logged'], ['Drill', 'Oct 23 to 25, Camp Smith']]},
  {'hue': 'teal', 'spine': '2026', 'blocks': [{'type': 'sub', 'text': 'Net by month'}, {'type': 'year', 'metric': 'net', 'fmt': 'money'}]},
 ]})

OCT['domains'].append({'id': 'financial', 'label': 'Financial', 'hue': 'teal', 'count': money(c['net'], whole=True, plus=True), 'main': fin_main, 'side': fin_side})

OCT['domains'].append({'id': 'physical', 'label': 'Physical', 'hue': 'green', 'count': g['days'],
 'main': [
  {'hue': 'green', 'spine': 'Briefing', 'type': 'para', 'text': [
    '%d training days through Oct 30, fewer than September because of the drill weekend, the Oct 3 wedding, and a busy back half. Lifting held its numbers while the focus shifted toward test prep: timed sit-ups, push-ups, and faster aerobic work.' % g['days'],
    'On Oct 30 came the sheriff’s deputy agility test, retaken after the first date collided with annual training at Fort Drum. The 1.5-mile run took 10:35 and sit-ups came in at 39 in under a minute, on a springy pad instead of the hard floor used in training. Push-ups and sit-ups were pass or fail.']},
  {'hue': 'green', 'spine': 'Calendar', 'blocks': [
    {'type': 'sub', 'text': 'Training days · tap a day for the full session', 'right': '%d of 30' % g['days']},
    {'type': 'cal', 'sessions': sessions(m), 'days': gym_cal(m, {'2026-10-30': 'Test', '2026-10-12': '5K'}), 'events': [23, 24, 25], 'eventLabel': 'drill',
     'legend': [['Legs', 'green'], ['Back', 'blue'], ['Chest', 'violet'], ['Shoulders', 'teal'], ['Run', 'red']]},
    {'type': 'note', 'text': 'Red outline: drill weekend at Camp Smith.'}]},
  {'hue': 'violet', 'spine': 'Lifts', 'blocks': [
    {'type': 'sub', 'text': 'Top working sets'},
    {'type': 'rows', 'items': [
      {'when': 'Bench', 'text': '195 x 5 twice (Oct 5), 185 x 11 (Oct 19), 185 x 10 (Oct 12)'},
      {'when': 'Squat', 'text': '225 x 11 (Oct 7), 195 x 10 (Oct 28)'},
      {'when': 'Trap bar', 'text': '315 x 5 (Oct 20)'},
      {'when': 'Row', 'text': 'Barbell 135 x 10 (Oct 13)'},
      {'when': 'Pulldown', 'text': '150 x 12 (Oct 27), 162.5 x 6 (Oct 16)'},
      {'when': 'Incline DB', 'text': '120 x 15 total (Oct 15)'},
    ]}]},
  {'hue': 'red', 'spine': 'Cardio', 'blocks': [
    {'type': 'sub', 'text': 'Runs and conditioning'},
    {'type': 'rows', 'items': [
      {'when': 'Oct 6', 'text': 'Zone 2 at speed 5.5, then sprint intervals. 2.5 miles in 21 minutes.'},
      {'when': 'Oct 9', 'text': 'Zone 2, 2.4 miles in 20 minutes at speed 5.8'},
      {'when': 'Oct 12', 'text': 'Treadmill 5K in 25:00 at speed 7.5'},
      {'when': 'Oct 16', 'text': 'Zone 2, 2.14 miles in 20 minutes'},
      {'when': 'Oct 26', 'text': 'Treadmill 2 miles in 16:07. Rough day, left lat cramping.'},
      {'when': 'Oct 30', 'text': 'Agility test: 1.5 miles in 10:35 (7:03 per mile)'},
    ]}]},
 ],
 'side': [
  {'hue': 'green', 'spine': 'Totals', 'type': 'kv', 'items': [
    ['Days', '%d of 30' % g['days'], {'big': True}], ['Volume', '{:,} lb'.format(g['volume']), {'big': True}],
    ['Cardio', '%d sessions · %d min' % (g['cardioSessions'], g['cardioMin'])], ['Distance', '%.1f mi logged' % g['miles']], ['Sep ref', '28 days · 166,118 lb']]},
  {'hue': 'green', 'spine': '2026', 'blocks': [
    {'type': 'sub', 'text': 'Gym days by month', 'right': 'tap a month'},
    {'type': 'year', 'metric': 'gymDays', 'fmt': 'int', 'showAll': True},
    {'type': 'sub', 'text': 'Volume by month, lb'},
    {'type': 'year', 'metric': 'volume', 'fmt': 'k'}]},
  {'hue': 'red', 'spine': 'Agility', 'type': 'kv', 'items': [
    ['1.5 mile', '10:35', {'big': True}], ['Sit-ups', '39 in 1 minute', {'big': True}], ['Push-ups', 'Pass or fail'], ['Note', 'Retake; first date fell during AT']]},
  {'hue': 'amber', 'spine': 'Sit-ups', 'blocks': [
    {'type': 'sub', 'text': 'Timed sit-ups per minute', 'right': 'Sep 4 to Oct 30'},
    {'type': 'spark', 'values': [31, 36.4, 28.4, 38.7, 41.4, 39], 'label': 'Sit-ups per minute', 'axis': ['31', '39 on test day']},
    {'type': 'note', 'text': 'Reps scaled to a 60-second pace from each logged attempt.'}]},
  {'hue': 'teal', 'spine': 'Zone 2', 'blocks': [
    {'type': 'sub', 'text': 'Zone 2 treadmill speed, mph'},
    {'type': 'meter', 'max': 6, 'rows': [['Sep 16', 5.0, '5.0'], ['Oct 6', 5.5, '5.5'], ['Oct 7', 5.7, '5.7'], ['Oct 9', 5.8, '5.8'], ['Oct 16', 5.7, '5.7']]},
    {'type': 'note', 'text': 'Same easy effort, faster pace: the cardio base is building.'}]},
 ]})

OCT['domains'].append({'id': 'spiritual', 'label': 'Spiritual', 'hue': 'magenta', 'count': 3,
 'main': [
  {'hue': 'magenta', 'spine': 'Series', 'type': 'para', 'text': [
    'The Galatians 5 series continued through peace, patience, and kindness. A thread ran through all three: cut the distractions, stay plugged into a local body, and let the fruit come from the Spirit rather than effort.',
    'Notes were recorded for Oct 4, 11, and 18. Oct 25 fell on the Camp Smith drill weekend.']},
  {'hue': 'magenta', 'spine': 'Sermons', 'type': 'sermons', 'month': '2026-10'}],
 'side': [
  {'hue': 'magenta', 'spine': 'Attendance', 'type': 'kv', 'items': [
    ['Oct 4', 'Peace', {'tag': 'Notes'}], ['Oct 11', 'Patience', {'tag': 'Notes'}], ['Oct 18', 'Kindness', {'tag': 'Notes'}], ['Oct 25', 'Drill at Camp Smith']]},
  {'hue': 'violet', 'spine': 'Series', 'blocks': [
    {'type': 'sub', 'text': 'Fruit of the Spirit covered', 'right': '5 of 9'},
    {'type': 'seg', 'rows': [['Covered', 5, 9, '5 of 9']]},
    {'type': 'note', 'text': 'Remaining: goodness, faithfulness, gentleness, self-control.'}]},
  {'hue': 'teal', 'spine': 'Giving', 'type': 'kv', 'items': [['Tithe', money(250) + ' to Calvary Baptist (Oct 9)', {'big': True}]]},
  {'hue': 'amber', 'spine': 'Habits', 'type': 'para', 'text': 'Daily Bible reading plan and YouVersion streak kept going through a crowded month.'},
 ]})

OCT['domains'].append({'id': 'intellectual', 'label': 'Intellectual', 'hue': 'blue', 'count': 3,
 'main': [
  {'hue': 'blue', 'spine': 'Briefing', 'type': 'para', 'text': [
    'All three MBA courses are in their final stretch, and everything lands in the next eleven days: FN 608 final report Nov 3, OM 603 final exam Nov 5, IS 606 final project Nov 10. The semester ending is the thing to look forward to.',
    'The OTS path moved from waiting to booked. The AFOQT retest is set for Mon Nov 30 at 9:00 AM at the UMGC National Testing Center on Fort Drum, with Dec 1 held as a backup. The voucher gets requested when Mr. Woods returns on Nov 23.']},
  {'hue': 'blue', 'spine': 'Courses', 'type': 'cards', 'cards': [
    {'hue': 'blue', 'spine': 'FN 608', 'title': 'Financial Management', 'text': 'Assignment 8 (risk factors) in Oct 26 with positive feedback. Final report on Coca-Cola due Nov 3; Self-Test 8 closes Nov 10.', 'tags': ['Report due Nov 3']},
    {'hue': 'blue', 'spine': 'IS 606', 'title': 'Business Information Systems', 'text': 'Running 92.38%. Midterm 88%, quizzes 100%. Quiz W8n9 closes Nov 3; final project due Nov 10.', 'tags': ['92.4%']},
    {'hue': 'blue', 'spine': 'OM 603', 'title': 'Decision Analysis & SC Modeling', 'text': 'Running 97.08%. Paper 2 (Travel Center) scored 100%. Only the final exam remains, Thu Nov 5 at 8 PM.', 'tags': ['97.1%']},
  ]},
  {'hue': 'red', 'spine': 'OTS', 'type': 'rows', 'items': [
    {'when': 'Oct 16', 'text': 'Mr. Woods (Test Control Officer, Joint Base MDL) sent the Pearson VUE steps for the retest voucher.'},
    {'when': 'Oct 19', 'text': 'Completed e-AFOQT voucher request form sent to Woods.'},
    {'when': 'Oct 20', 'text': 'Shari Smith at UMGC Fort Drum reserved Nov 30, 9:00 AM, with Dec 1 as the alternate. Woods will request the voucher Nov 23.'},
    {'when': 'Oct 27', 'text': 'Aim High portal: 4 of 21 tasks complete, board 27OTS01R on Jan 25, 2027, status At Risk. Retake request due Dec 13.'},
  ]},
  {'hue': 'orange', 'spine': 'Guard', 'type': 'para', 'text': 'Drill weekend Oct 23 to 25. Four of us from HHC drove a rental van down to Camp Smith to run deployment screening for the 212th and the 101st Cavalry ahead of their upcoming mobilization. This was not the usual DD 93, SGLI, records review, and ID card work; it was the information reports cannot show, like legal history questions, family care plans, and whether dependents were recorded correctly.'},
  {'hue': 'teal', 'spine': 'Work', 'type': 'rows', 'items': [
    {'text': 'Ran PT Month for the PT cohorts with Samantha: weekly activities, raffles, and a form, tracker, and dashboard.'},
    {'text': 'Built a QR check-in and check-out system, folding in the ultrasound equipment sign-out sheet.'},
    {'text': 'Worked on the OT fieldwork manuals for Ashleigh Graveline.'},
    {'text': 'Clarkson Hall wayfinding moved from 3D videos to printable PDF visitor guides.'},
  ]},
  {'hue': 'slate', 'spine': 'Civil service', 'type': 'para', 'text': 'Sheriff’s deputy civil service: agility test retaken Oct 30 after the original date fell during annual training. Result pending.'},
 ],
 'side': [
  {'hue': 'blue', 'spine': 'Grades', 'blocks': [
    {'type': 'sub', 'text': 'Running course totals'},
    {'type': 'meter', 'max': 100, 'rows': [['OM 603', 97.08, '97.1%'], ['IS 606', 92.38, '92.4%']]},
    {'type': 'note', 'text': 'FN 608 has no real running total in Moodle; assignments post as forums.'}]},
  {'hue': 'red', 'spine': 'Deadlines', 'type': 'rows', 'items': [
    {'when': 'Nov 3', 'text': 'FN 608 final report and peer feedback; IS 606 quiz'},
    {'when': 'Nov 5', 'text': 'OM 603 final exam, 8 PM'},
    {'when': 'Nov 10', 'text': 'IS 606 final project; FN 608 Self-Test 8'},
    {'when': 'Nov 23', 'text': 'Woods requests the AFOQT voucher'},
    {'when': 'Nov 30', 'text': 'AFOQT retest, Fort Drum, 9 AM'},
  ]},
  {'hue': 'orange', 'spine': 'AFOQT', 'blocks': [
    {'type': 'sub', 'text': 'Quant score vs minimum'},
    {'type': 'meter', 'max': 100, 'rows': [['Quant now', 6, '6', 10]]},
    {'type': 'note', 'text': 'Prep plan runs to Nov 30: arithmetic reasoning and math knowledge.'}]},
 ]})

OCT['domains'].append({'id': 'creative', 'label': 'Creative', 'hue': 'amber', 'count': 2,
 'main': [
  {'hue': 'amber', 'spine': 'Briefing', 'type': 'para', 'text': [
    'JD Meyers Productions opened a studio. After losing a headshot client on Oct 13 because there was no studio setup, the B&H order went in the same day: backdrop, one light, a reflector, and a softbox. Studio Headshots is now live on jdmeyersjr.com, starting at $195.',
    'The month opened with a wedding shoot on Oct 3 for BRL Entertainment at Shindigz on the River in Russell, and the first studio sessions followed within two weeks.']},
  {'hue': 'amber', 'spine': 'Jobs', 'type': 'cards', 'cards': [
    {'hue': 'amber', 'spine': 'Wedding', 'date': datebox('2026-10-03'), 'title': 'Ken & TaShell', 'text': 'Video operator for BRL Entertainment: getting ready, first look, ceremony. Two-camera coverage, RAW files handed off.', 'tags': ['$1,175', '$100 tip'], 'foot': ['JDM-2026-20', 'Paid']},
    {'hue': 'amber', 'spine': 'Studio', 'date': datebox('2026-10-21'), 'title': 'David Zufall headshots', 'text': 'First studio headshot session; gallery delivered and downloaded Oct 21.', 'tags': ['Studio'], 'foot': ['Studio session', 'Delivered']},
    {'hue': 'orange', 'spine': 'Film', 'date': datebox('2026-10-28'), 'title': 'Merrick film at Park Bros', 'text': 'Gallery delivered Oct 28.', 'tags': ['Film'], 'foot': ['Gallery', 'Delivered']},
    {'hue': 'slate', 'spine': 'Cancelled', 'date': datebox('2026-10-11'), 'title': 'Josue Bernal', 'text': 'Cancelled for a personal conflict, deposit refunded in full. He wants to reschedule later.', 'tags': ['Refunded'], 'foot': ['JDM-2026-17', 'Closed']},
  ]},
  {'hue': 'slate', 'spine': 'Pipeline', 'type': 'rows', 'items': [
    {'when': 'Oct 11', 'text': 'John Coogan booked fraternity alumni photos for Sep 4, 2027. $50 deposit in; contract still to send.'},
    {'when': 'Oct 13', 'text': 'Alexander Cohen needed a studio headshot; declined for lack of a studio. Studio kit ordered the same day.'},
    {'when': 'Oct 21', 'text': 'Max Ferran and Mwaphira James signed up for free studio headshots.'},
    {'when': 'Oct 27', 'text': 'Allen Nance, drone video of a 2,000-acre tract. Waiting on the client.'},
    {'when': 'Oct', 'text': 'Fell through: MotorHome Finders (location far south), Nico Gamarra proposal, Raddme event (out of scope).'},
  ]},
 ],
 'side': [
  {'hue': 'amber', 'spine': 'Studio', 'type': 'kv', 'items': [
    ['Essential', '$195 · 25 min · 10 images', {'big': True}], ['Signature', '$325 · 60 min · 20 images', {'big': True}],
    ['Deposit', '$50 to book'], ['Kit', money(594.35) + ' from B&H'], ['Page', 'jdmeyersjr.com/studio-headshots']]},
  {'hue': 'orange', 'spine': 'Business', 'type': 'kv', 'items': [
    ['In', money(jdm_in) + ' landed', {'big': True}], ['Out', money(jdm_out) + ' (studio, ads, software)'], ['Net', money(jdm_in - jdm_out, plus=True), {'big': True}]]},
  {'hue': 'violet', 'spine': 'Funnel', 'blocks': [
    {'type': 'sub', 'text': 'October inquiries'},
    {'type': 'meter', 'max': 8, 'rows': [['Inquiries', 8, '8'], ['Booked', 1, '1'], ['Free studio', 2, '2'], ['Open', 1, '1'], ['Lost', 4, '4']]}]},
  {'hue': 'slate', 'spine': 'Projects', 'type': 'rows', 'items': [
    {'text': 'North Country Circle contact dossier app'},
    {'text': 'Worship piano manual from the 2017 course'},
    {'text': '315signalfeed dashboard restyle'}]},
 ]})

OCT['domains'].append({'id': 'reflections', 'label': 'Reflections', 'hue': 'violet', 'count': 5,
 'main': [
  {'hue': 'violet', 'spine': 'Pull quote', 'type': 'para', 'text': '**Everything at once, and it held.** A wedding, a studio, a drill, a test, and three finals coming.'},
  {'hue': 'violet', 'spine': 'a. Gap', 'type': 'para', 'text': 'Losing a client for not having a studio and ordering one the same day is the right reflex. The gap got closed with a modest kit, not a big bet, and the page went live before the first session.'},
  {'hue': 'violet', 'spine': 'b. Camp Smith', 'type': 'para', 'text': 'The drill was a reminder of why the S1 work matters. The questions that never show on a report, like family care plans and dependents, are the ones that decide whether a Soldier is actually ready to deploy.'},
  {'hue': 'violet', 'spine': 'c. The test', 'type': 'para', 'text': 'The agility test was worth the nerves. Training on a hard floor with full range of motion and testing on a springy pad was the unknown, and it went fine. Glad it is over.'},
  {'hue': 'violet', 'spine': 'd. Money', 'type': 'para', 'text': 'September’s red was planned and October more than covered it. Side income from taxi and JDM is real money when it stacks on three paychecks.'},
  {'hue': 'violet', 'spine': 'e. November', 'type': 'para', 'text': 'Finish the semester (Nov 3, 5, 10), drill quant every day toward Nov 30, chase the voucher on Nov 23, and take delivery of the iPhone Duo.'},
 ],
 'side': [
  {'hue': 'violet', 'spine': 'In a line', 'type': 'para', 'text': 'The full-calendar month: busiest of the fall, and nothing dropped.'},
  {'hue': 'slate', 'spine': 'Carry over', 'type': 'list', 'items': ['Three finals by Nov 10', 'AFOQT voucher Nov 23, test Nov 30', 'Coogan contract to send', 'Sheriff test result', 'Nov 6 to 8 drill: height and weight']},
 ]})

write(m, OCT)
print('ok')
