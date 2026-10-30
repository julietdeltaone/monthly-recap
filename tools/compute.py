"""Finance + gym computation for Sep/Oct 2026 recaps. Prints summaries, writes calc.json."""
import csv, json, re, collections, datetime as dt

A = '/mnt/user-data/attachments/e2eb66b9-6aee-558a-b3a4-c4e64327d063/'
TX = A + 'a40c5dd5-2026-10-30_21_49_17-transactions.csv'
FN = A + 'ea62dfbc-FitNotes_2026-09-01_to_2026-10-30.csv'
YTD_AUG = 17650.47

def acct(a):
    if 'Productions (8718)' in a: return 'NCSB JDM checking'
    if 'John David Meyers (6005)' in a: return 'NCSB checking'
    if 'Apple Card' in a: return 'Apple Card'
    if 'Apple Cash' in a: return 'Apple Cash'
    if 'Apple - Savings' in a: return 'Apple Savings'
    if 'J. MEYERS JR (1950)' in a: return 'Chase business card'
    if 'Chase' in a: return 'Chase card'
    if 'Venmo' in a: return 'Venmo personal'
    if 'Corning' in a: return 'Corning CU savings'
    return a

APPLE_MOVES = {('2026-09-01', 217.16), ('2026-10-04', 69.33)}

def classify(r):
    d, desc, amt, a, typ = r['Date'], r['Description'], float(r['Amount']), r['Account'], r['Type']
    u = (desc + ' | ' + r['Statement description']).upper()
    # ---- money moved (not income, not spending)
    if (d, abs(amt)) in APPLE_MOVES and ('Apple' in a):
        return ('mv', 'Apple Savings to Apple Cash', 'Moved')
    if typ == 'Transfer':
        if 'M1' in u: return ('mv', 'M1 Finance investment', 'Invested')
        if 'ROBINHOOD' in u: return ('mv', 'Robinhood investment', 'Invested')
        if 'Invest' in desc: return ('mv', 'Transfer to JDM account for investing', 'Moved')
        if 'CHASE CREDIT' in u or 'PAYMENT' in u or 'APPLECARD' in u or 'Bill Payment' in desc: return ('mv', 'Credit card payment', 'Card payment')
        if 'METAPAY' in u: return ('mv', 'Meta Pay verification', 'Moved')
        if 'VENMO' in u: return ('mv', 'Venmo top-up', 'Moved')
        if 'P2P' in u or 'John Meyers' in desc: return ('mv', 'Transfer to Corning CU savings', 'Moved')
        if 'x8718' in desc or 'x6005' in desc: return ('mv', 'JDM account to personal checking', 'Moved')
        return ('mv', desc.title(), 'Moved')
    # ---- income
    if typ == 'Income':
        if 'CLARKSON' in u: return ('in', 'Clarkson University payroll', 'Clarkson payroll')
        if 'DEFENSE FINANCE' in u: return ('in', 'NY Army National Guard pay (DFAS)', 'Guard pay')
        if u.startswith('RAISER'): return ('in', 'Uber driver earnings', 'Uber')
        if u.startswith('SQUARE'):
            if 'Productions' in a or amt >= 400: return ('in', 'JD Meyers Productions (Square)', 'JDM Productions')
            return ('in', 'Taxi fares (Square)', 'Taxi')
        if desc == 'Venmo' and amt > 0: return ('in', 'JD Meyers Productions (Venmo payout)', 'JDM Productions')
        if 'Zufall' in desc: return ('in', 'David Zufall, gift cards (Venmo)', 'Other')
        if desc == 'Interest': return ('in', 'Apple Savings interest', 'Interest')
        if 'DIVIDEND' in u: return ('in', 'Corning CU dividend', 'Interest')
        if desc == 'Deposit' and 'Apple Cash' in a: return ('in', 'Apple Daily Cash', 'Cashback')
        if 'KNOWN TRAVELER' in u: return ('out', 'TSA PreCheck credit (Chase)', 'Fees & travel')
        if 'HIGGSFIELD' in u: return ('out', 'Higgsfield refund', 'Subscriptions')
        raise ValueError(repr(r))
    # ---- spending
    rules = [
        (r'VERIZON|VZWRLSS', 'Verizon, iPhone 17 Pro payoff', 'Phone & devices'),
        (r'KLARNA', 'Apple Watch lease (Klarna)', 'Phone & devices'),
        (r'APPLE STORE', 'Apple Store', 'Phone & devices'),
        (r'ESRTECH', 'ESR phone accessories', 'Phone & devices'),
        (r'B&H', 'B&H Photo, headshot studio kit', 'JDM Productions'),
        (r'GOOGLE \*ADS|GOOGLE\*ADS', 'Google Ads', 'JDM Productions'),
        (r'ADOBE', 'Adobe', 'JDM Productions'),
        (r'PIXIESET', 'Pixieset galleries', 'JDM Productions'),
        (r'ANTHROPIC', 'Claude subscription', 'Subscriptions'),
        (r'CALVARY', 'Calvary Baptist tithe', 'Giving'),
        (r'WALMART|PRICE CHOPPER|APPLEWOOD|WILD OAT', None, 'Groceries'),
        (r'TESLA SUBSCRIPTION', 'Tesla connectivity', 'Tesla'),
        (r'TESLA SUPERCHARGER', 'Tesla Supercharger', 'Tesla'),
        (r'TRICARE', 'TRICARE Reserve Select', 'Health'),
        (r'HIMS', 'Hims & Hers', 'Health'),
        (r'SWANSON', 'Swanson vitamins', 'Health'),
        (r'SIAN MILLER', 'Haircut (Sian Miller)', 'Personal care'),
        (r'GRAMMARLY', 'Grammarly', 'Subscriptions'),
        (r'ORIGIN', 'Origin finance app (annual)', 'Subscriptions'),
        (r'CHATGPT', 'ChatGPT', 'Subscriptions'),
        (r'YOUTUBE', 'YouTube Premium', 'Subscriptions'),
        (r'HIGGSFIELD', 'Higgsfield', 'Subscriptions'),
        (r'ELEVENLABS', 'ElevenLabs', 'Subscriptions'),
        (r'WISPR', 'Wispr Flow', 'Subscriptions'),
        (r'PENTESTER', 'Pentester.com', 'Subscriptions'),
        (r'DOORDASH', 'DoorDash DashPass', 'Subscriptions'),
        (r'GOOGLE', 'Google One / storage', 'Subscriptions'),
        (r'^APPLE \| APPLE$', 'Apple subscriptions', 'Subscriptions'),
        (r'ONBLACK', 'On Black backpack', 'Shopping'),
        (r'AMAZON', 'Amazon', 'Shopping'),
        (r'IZOD', 'Izod', 'Shopping'),
        (r'USMA', 'West Point PX', 'Shopping'),
        (r'JERICHO|APPLEGREEN', None, 'Shopping'),
        (r'ROXY', 'Roxy Theater', 'Entertainment'),
        (r'IDEMIA|TSA', 'TSA PreCheck renewal', 'Fees & travel'),
        (r'CLERK|MUNICIPAY', 'St. Lawrence County Clerk', 'Fees & travel'),
        (r'OGDENSBURG BRIDGE', 'Ogdensburg bridge toll', 'Fees & travel'),
        (r'MULTIACQTEST', 'Unlabeled card charge', 'Other'),
    ]
    for pat, lab, cat in rules:
        if re.search(pat, u) or re.search(pat, desc.upper().strip()):
            return ('out', lab or desc.replace('Supermarkets', '').strip(), cat)
    return ('out', desc.replace('Ryan Blount "Dinner"', 'Dinner with Ryan Blount (Venmo)'), 'Dining & coffee')

rows = [{k: (v or '').replace('\xa0', ' ') for k, v in r.items()} for r in csv.DictReader(open(TX))]
assert len(rows) == 315, len(rows)
out = {}
for m in ('2026-09', '2026-10'):
    mr = [r for r in rows if r['Date'].startswith(m)]
    items = []
    for r in mr:
        kind, lab, cat = classify(r)
        amt = float(r['Amount'])
        items.append(dict(date=r['Date'], kind=kind, label=lab, cat=cat, amt=round(amt, 2), acct=acct(r['Account'])))
    inc = [i for i in items if i['kind'] == 'in']
    exp = [i for i in items if i['kind'] == 'out']
    income = round(sum(i['amt'] for i in inc), 2)
    spend = round(-sum(i['amt'] for i in exp), 2)
    net = round(income - spend, 2)
    invested = round(-sum(i['amt'] for i in items if i['cat'] == 'Invested' and i['acct'] in ('NCSB JDM checking', 'Corning CU savings') or (i['label'] == 'Robinhood investment')), 2)
    bysrc = collections.Counter(); bycat = collections.Counter()
    for i in inc: bysrc[i['cat']] += i['amt']
    for i in exp: bycat[i['cat']] += -i['amt']
    # weekly buckets (Mon-start weeks clipped to month)
    days = int(m[-2:] == '09') and 30 or 31
    wk = collections.OrderedDict()
    for d in range(1, days + 1):
        date = dt.date(2026, int(m[-2:]), d)
        start = date - dt.timedelta(days=date.weekday())
        key = max(start, dt.date(2026, int(m[-2:]), 1)).strftime('%b %-d')
        wk.setdefault(key, [0, 0])
    for i in inc + exp:
        date = dt.date.fromisoformat(i['date']); start = date - dt.timedelta(days=date.weekday())
        key = max(start, dt.date(2026, int(m[-2:]), 1)).strftime('%b %-d')
        if i['kind'] == 'in': wk[key][0] += i['amt']
        else: wk[key][1] += -i['amt']
    cum = []; c = 0
    for d in range(1, days + 1):
        ds = '%s-%02d' % (m, d)
        c += sum(i['amt'] for i in inc + exp if i['date'] == ds)
        cum.append(round(c, 2))
    assert abs(cum[-1] - net) < 0.01
    out[m] = dict(items=items, income=income, spend=spend, net=net, invested=invested,
                  bysrc={k: round(v, 2) for k, v in bysrc.most_common()},
                  bycat={k: round(v, 2) for k, v in bycat.most_common()},
                  weeks=[[k, round(v[0], 2), round(v[1], 2)] for k, v in wk.items()], cum=cum,
                  n_in=len(inc), n_out=len(exp), n_mv=len(items) - len(inc) - len(exp))
    print(m, 'income', income, 'spend', spend, 'net', net, 'invested', invested)
    print('  src', out[m]['bysrc']); print('  cat', out[m]['bycat'])
    print('  weeks', out[m]['weeks'])

# hard assertions on known figures
assert out['2026-09']['bysrc']['Clarkson payroll'] == 2069.85
assert out['2026-10']['bysrc']['Clarkson payroll'] == 3380.78
assert out['2026-10']['bysrc']['JDM Productions'] == round(1135.92 + 290.85, 2)
assert out['2026-10']['bysrc']['Taxi'] == round(311.07 + 289.80 + 347.82, 2)
ytd_sep = round(YTD_AUG + out['2026-09']['net'], 2)
ytd_oct = round(ytd_sep + out['2026-10']['net'], 2)
out['2026-09']['ytdPrev'] = YTD_AUG; out['2026-09']['ytdEnd'] = ytd_sep
out['2026-10']['ytdPrev'] = ytd_sep; out['2026-10']['ytdEnd'] = ytd_oct
print('YTD', YTD_AUG, '->', ytd_sep, '->', ytd_oct)

# ------------------------------------------------ gym
raw = open(FN).read()
assert raw.count('"') % 2 == 0, 'unterminated quote in FitNotes CSV'
fr = list(csv.DictReader(open(FN)))
assert len(fr) == 388, len(fr)
def secs(t):
    if not t: return 0
    h, mi, s = [int(x) for x in t.split(':')]; return h * 3600 + mi * 60 + s
for m in ('2026-09', '2026-10'):
    mr = [r for r in fr if r['Date'].startswith(m)]
    days = sorted({r['Date'] for r in mr})
    vol = 0
    cats = collections.defaultdict(set)
    for r in mr:
        if r['Category'] != 'Cardio' and r['Weight (lbs)'] and r['Reps']:
            vol += float(r['Weight (lbs)']) * int(r['Reps'])
        cats[r['Date']].add(r['Category'])
    cardio = [r for r in mr if r['Category'] == 'Cardio']
    cmin = sum(secs(r['Time']) for r in cardio) / 60
    miles = 0
    for r in cardio:
        if r['Distance']:
            dd = float(r['Distance']); miles += dd if r['Distance Unit'] == 'mi' else dd * 0.621371
    split = collections.Counter()
    for d in days:
        main = [c for c in cats[d] if c not in ('Cardio', 'Abs')]
        for c in main: split[c] += 1
    out[m]['gym'] = dict(days=len(days), dayList=days, volume=round(vol), cardioSessions=len({r['Date'] for r in cardio}),
                         cardioMin=round(cmin), miles=round(miles, 1), split=dict(split.most_common()),
                         dayCats={d: sorted(cats[d]) for d in days})
    sess = {}
    def num(x): return ('%g' % float(x))
    def tm(t):
        h, mi, se = [int(v) for v in t.split(':')]
        return ('%d:%02d:%02d' % (h, mi, se)) if h else ('%d:%02d' % (mi, se))
    for d in days:
        ex = collections.OrderedDict()
        for r in [x for x in mr if x['Date'] == d]:
            w, rp, dist, t, name = r['Weight (lbs)'], r['Reps'], r['Distance'], r['Time'], r['Exercise']
            if r['Category'] == 'Cardio':
                unit = r['Distance Unit']
                if d == '2026-10-30' and unit == 'km': unit = 'mi'  # agility test run was 1.5 mi
                bits = []
                if dist: bits.append(num(dist) + ' ' + unit)
                if t: bits.append(tm(t))
                if w:
                    if 'Sprint' in name: bits.append('speed ' + num(w))
                    elif name == 'Stairs (Weighted)': bits.append(num(w) + ' lb vest')
                    elif name == 'Stairs': bits.append('level ' + num(w))
                s_ = ' @ '.join(bits[:2]) + ((' (' + bits[2] + ')') if len(bits) > 2 else '') if len(bits) > 1 and dist else ' '.join(bits)
            elif w and rp: s_ = num(w) + 'x' + rp
            elif rp and t: s_ = rp + ' in ' + tm(t)
            elif rp: s_ = rp + ' reps'
            elif t: s_ = tm(t)
            else: s_ = ''
            ex.setdefault(name.replace(' Potsdam', '').replace('Sqaut', 'Squat').replace('Cabel', 'Cable'), []).append(s_)
        sess[int(d[-2:])] = [[k, ', '.join(v)] for k, v in ex.items()]
    out[m]['gym']['sessions'] = sess
    print(m, 'gym days', len(days), 'volume', round(vol), 'cardio days', out[m]['gym']['cardioSessions'], 'cardio min', round(cmin), 'miles', round(miles, 1))
    print('  split', dict(split.most_common()))
    # top sets
    best = {}
    for r in mr:
        if r['Weight (lbs)'] and r['Reps'] and r['Category'] != 'Cardio':
            w, rp = float(r['Weight (lbs)']), int(r['Reps'])
            e1 = w * (1 + rp / 30)
            k = r['Exercise']
            if k not in best or e1 > best[k][2]: best[k] = (w, rp, e1, r['Date'])
    for k in ['Flat Barbell Bench Press', 'Barbell Squat', 'Deadlift', 'Trap Bar Deadlift', 'Standing Barbell Press', 'Lat Pulldown Potsdam', 'Incline Dumbbell Bench Press', 'Leg Press', 'Smith Machine Sqaut', 'Barbell Row']:
        if k in best: print('   top', k, best[k][:2], best[k][3], 'e1RM', round(best[k][2]))
json.dump(out, open('/tmp/claude-0/-home-claude/e2eb66b9-6aee-558a-b3a4-c4e64327d063/scratchpad/calc.json', 'w'), indent=1)
