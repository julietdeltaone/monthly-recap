"""Finance pipeline for every 2026 month, from one Origin export.

Usage: python3 tools/finance.py <origin_export.csv> <out.json>

Rules (stated by JD, Oct 2026):
  - Every income line gets a plain label, never the raw bank string.
  - Square deposits of about $250 to $300 (anything under $400) are taxi fares; $400 and up is JD Meyers Productions.
  - Venmo payouts into checking are JD Meyers Productions.
  - Apple Savings to Apple Cash moves are money moved, not income.
Data fixes:
  - The Chase Sapphire Reserve (7999) feed duplicates Chase CREDIT CARD (6358) from January to July.
    A 7999 row with an exact date and amount match in 6358 is dropped.
  - Card credits and refunds (travel, dining, hotel, StubHub, Amex perks) net against spending.
"""
import csv, json, re, sys, collections, datetime as dt

def load(path):
    rows = [{k: (v or '').replace('\xa0', ' ') for k, v in r.items()} for r in csv.DictReader(open(path))]
    pool = collections.Counter((r['Date'], r['Amount']) for r in rows if '(6358)' in r['Account'])
    keep, dropped = [], 0
    for r in rows:
        if '(7999)' in r['Account']:
            k = (r['Date'], r['Amount'])
            if pool[k] > 0:
                pool[k] -= 1; dropped += 1; continue
        keep.append(r)
    return keep, dropped

def acct(a):
    for pat, name in [('Productions (8718)', 'NCSB JDM checking'), ('John David Meyers (6005)', 'NCSB checking'), ('Apple Card', 'Apple Card'),
                      ('Apple Cash', 'Apple Cash'), ('Apple - Savings', 'Apple Savings'), ('J. MEYERS JR (1950)', 'Chase business card'),
                      ('Sapphire Reserve', 'Chase Sapphire'), ('Freedom', 'Chase Freedom'), ('IHG', 'Chase IHG card'), ('Chase', 'Chase card'),
                      ('Venmo', 'Venmo personal'), ('Corning', 'Corning CU savings'), ('Platinum', 'Amex Platinum'), ('Gold', 'Amex Gold'),
                      ('Hilton', 'Amex Hilton')]:
        if pat in a: return name
    return a

def apple_moves(rows):
    """Apple Cash deposits that mirror an Apple Savings withdrawal within 7 days."""
    w = [(dt.date.fromisoformat(r['Date']), round(-float(r['Amount']), 2)) for r in rows if r['Account'] == 'Apple - Savings' and r['Description'] == 'Withdrawal']
    out = set()
    for r in rows:
        if r['Account'] == 'Apple - Apple Cash' and r['Description'] == 'Deposit':
            d, a = dt.date.fromisoformat(r['Date']), round(float(r['Amount']), 2)
            if any(abs((d - wd).days) <= 7 and a == wa for wd, wa in w): out.add((r['Date'], a))
    return out

SPEND = [
    (r'VERIZON|VZWRLSS', 'Verizon', 'Phone & devices'), (r'KLARNA', 'Apple Watch lease (Klarna)', 'Phone & devices'),
    (r'APPLE STORE', 'Apple Store', 'Phone & devices'), (r'ESRTECH', 'ESR phone accessories', 'Phone & devices'),
    (r'B&H', 'B&H Photo', 'JDM Productions'), (r'GOOGLE \*ADS|GOOGLE\*ADS', 'Google Ads', 'JDM Productions'), (r'ADOBE', 'Adobe', 'JDM Productions'),
    (r'PIXIESET', 'Pixieset galleries', 'JDM Productions'), (r'SQUARESPACE', 'Squarespace', 'JDM Productions'),
    (r'CALVARY', 'Calvary Baptist tithe', 'Giving'),
    (r'WALMART|PRICE CHOPPER|APPLEWOOD|WILD OAT|ALDI|HANNAFORD|TARGET|COSTCO|SAM\'S', None, 'Groceries'),
    (r'TESLA SUBSCRIPTION', 'Tesla connectivity', 'Tesla'), (r'TESLA', 'Tesla Supercharger', 'Tesla'),
    (r'TRICARE', 'TRICARE Reserve Select', 'Health'), (r'HIMS', 'Hims & Hers', 'Health'), (r'SWANSON', 'Swanson vitamins', 'Health'),
    (r'SIAN MILLER', 'Haircut (Sian Miller)', 'Personal care'),
    (r'ANTHROPIC', 'Claude subscription', 'Subscriptions'), (r'GRAMMARLY', 'Grammarly', 'Subscriptions'), (r'ORIGIN', 'Origin finance app', 'Subscriptions'),
    (r'CHATGPT|OPENAI', 'ChatGPT', 'Subscriptions'), (r'YOUTUBE', 'YouTube Premium', 'Subscriptions'), (r'HIGGSFIELD', 'Higgsfield', 'Subscriptions'),
    (r'ELEVENLABS', 'ElevenLabs', 'Subscriptions'), (r'WISPR', 'Wispr Flow', 'Subscriptions'), (r'PENTESTER', 'Pentester.com', 'Subscriptions'),
    (r'DOORDASH', 'DoorDash', 'Subscriptions'), (r'GOOGLE', 'Google subscription', 'Subscriptions'), (r'^APPLE \| APPLE', 'Apple subscriptions', 'Subscriptions'),
    (r'NETFLIX|HULU|DISNEY|PARAMOUNT|HBO|MAX\b|SPOTIFY', None, 'Subscriptions'),
    (r'ONBLACK', 'On Black backpack', 'Shopping'), (r'AMAZON', 'Amazon', 'Shopping'), (r'INMOTION', 'InMotion V9 EUC', 'Shopping'),
    (r'USMA', 'West Point PX', 'Shopping'),
    (r'ROXY|STUBHUB', None, 'Entertainment'),
    (r'IDEMIA|TSA|KNOWN TRAVELER|CLEAR', None, 'Travel & fees'), (r'CLERK|MUNICIPAY', 'St. Lawrence County Clerk', 'Travel & fees'),
    (r'BRIDGE|TOLL|HAMPTON|HILTON|FAIRMONT|HOTEL|CHASE TRAVEL|AIRLINE|UNITED|DELTA|AMEX HOTEL|EDIT YEAR|TRAVEL CREDIT|ONCENTER', None, 'Travel & fees'),
    (r'MULTIACQTEST', 'Unlabeled card charge', 'Other'),
]
CAT_FALLBACK = {'Groceries': 'Groceries', 'Drinks & dining': 'Dining & coffee', 'Shopping': 'Shopping', 'Subscriptions': 'Subscriptions',
                'Travel & vacation': 'Travel & fees', 'Entertainment': 'Entertainment', 'Healthcare': 'Health', 'Personal care': 'Personal care',
                'Business': 'JDM Productions', 'Tithe': 'Giving', 'Auto & transport': 'Tesla', 'Apple Products': 'Phone & devices',
                'Education': 'Subscriptions', 'Financial': 'Travel & fees', 'Donations': 'Giving'}

def classify(r, moves):
    d, desc, amt, a, typ = r['Date'], r['Description'], float(r['Amount']), r['Account'], r['Type']
    u = (desc + ' | ' + r['Statement description']).upper()
    if (d, round(abs(amt), 2)) in moves and 'Apple Cash' in a and amt > 0:
        return 'mv', 'Apple Savings to Apple Cash', 'Moved'
    if typ == 'Transfer':
        if 'M1' in u: return 'mv', 'M1 Finance investment', 'Invested'
        if 'ROBINHOOD' in u: return 'mv', 'Robinhood investment', 'Invested'
        if a == 'Apple - Savings': return 'mv', 'Apple Savings ' + ('deposit' if amt > 0 else 'withdrawal'), 'Savings'
        if 'INVEST' in u: return 'mv', 'Transfer to JDM account for investing', 'Moved'
        if any(k in u for k in ('CHASE CREDIT', 'PAYMENT', 'APPLECARD', 'BILL PAYMENT', 'AUTOPAY', 'AMEX EPAYMENT')): return 'mv', 'Credit card payment', 'Card payment'
        if 'VENMO' in u: return 'mv', 'Venmo transfer', 'Moved'
        if 'P2P' in u or 'JOHN MEYERS' in u: return 'mv', 'Transfer to Corning CU savings', 'Moved'
        return 'mv', desc.title()[:40], 'Moved'
    if u.startswith('SQUARE') and amt > 0:
        return ('in', 'JD Meyers Productions (Square)', 'JDM Productions') if amt >= 400 else ('in', 'Taxi fares (Square)', 'Taxi')
    if typ == 'Income':
        if 'CLARKSON' in u: return 'in', 'Clarkson University payroll', 'Clarkson payroll'
        if 'DEFENSE FINANCE' in u: return 'in', 'NY Army National Guard pay (DFAS)', 'Guard pay'
        if u.startswith('RAISER') or 'UBER' in u: return 'in', 'Uber driver earnings', 'Uber'
        if 'TAXI' in u: return 'in', 'Taxi fares', 'Taxi'
        if desc == 'Venmo' and 'Venmo' not in a: return 'in', 'JD Meyers Productions (Venmo payout)', 'JDM Productions'
        if 'TOMFORD' in u: return 'in', 'JuliaKia Photography subcontract (Venmo)', 'JDM Productions'
        if 'INTERNAL REVENUE' in u: return 'in', 'Federal tax refund', 'Tax refund'
        if 'NYSTTAXRFD' in u or 'NY STATE' in u: return 'in', 'NY State tax refund', 'Tax refund'
        if desc == 'Interest': return 'in', 'Apple Savings interest', 'Interest'
        if 'DIVIDEND' in u: return 'in', 'Corning CU dividend', 'Interest'
        if desc == 'Deposit' and 'Apple Cash' in a: return 'in', 'Apple Daily Cash', 'Cashback'
        if 'KNOWN TRAVELER' in u or 'TRAVEL CREDIT' in u: return 'out', 'Card travel credit', 'Travel & fees'
        if 'HIGGSFIELD' in u: return 'out', 'Higgsfield refund', 'Subscriptions'
        if 'Venmo' in a:
            who = re.sub(r'\s*".*', '', desc).strip()
            return 'in', 'Venmo from ' + who, 'Other'
        if desc == 'Deposit': return 'in', 'Deposit, unlabeled', 'Other'
        return 'in', desc.title()[:40], 'Other'
    if r['Category'] == 'Reimbursement' or 'SUNY POTSDAM' in u:
        if amt > 0 and 'SUNY' in u: return 'in', 'SUNY Potsdam reimbursement', 'Other'
    for pat, lab, cat in SPEND:
        if re.search(pat, u):
            return 'out', lab or desc.strip(), cat
    label = desc.strip()
    if 'Venmo' in a and '"' in desc:
        who, what = desc.split('"', 1)[0].strip(), desc.split('"')[1]
        label = what.capitalize() + ' (' + who + ', Venmo)'
    return 'out', label, CAT_FALLBACK.get(r['Category'], 'Dining & coffee' if 'SUNOCO' in u or "STEWART" in u else 'Other')

def month_block(items, m, days):
    inc = [i for i in items if i['kind'] == 'in']; exp = [i for i in items if i['kind'] == 'out']
    income = round(sum(i['amt'] for i in inc), 2); spend = round(-sum(i['amt'] for i in exp), 2)
    bysrc, bycat = collections.Counter(), collections.Counter()
    for i in inc: bysrc[i['cat']] += i['amt']
    for i in exp: bycat[i['cat']] += -i['amt']
    y, mo = 2026, int(m[-2:])
    wk = collections.OrderedDict()
    def wkey(date):
        start = date - dt.timedelta(days=date.weekday())
        return max(start, dt.date(y, mo, 1)).strftime('%b %-d')
    for d in range(1, days + 1): wk.setdefault(wkey(dt.date(y, mo, d)), [0, 0])
    for i in inc + exp:
        k = wkey(dt.date.fromisoformat(i['date']))
        if i['kind'] == 'in': wk[k][0] += i['amt']
        else: wk[k][1] += -i['amt']
    cum, c = [], 0
    for d in range(1, days + 1):
        ds = '%s-%02d' % (m, d); c += sum(i['amt'] for i in inc + exp if i['date'] == ds); cum.append(round(c, 2))
    invested = round(-sum(i['amt'] for i in items if i['cat'] == 'Invested' and i['amt'] < 0 and i['acct'] in ('NCSB JDM checking', 'Corning CU savings', 'NCSB checking') and i['label'] != 'Transfer to JDM account for investing'), 2)
    return dict(items=items, income=income, spend=spend, net=round(income - spend, 2), invested=invested,
                bysrc={k: round(v, 2) for k, v in bysrc.most_common()}, bycat={k: round(v, 2) for k, v in bycat.most_common()},
                weeks=[[k, round(v[0], 2), round(v[1], 2)] for k, v in wk.items()], cum=cum,
                n_in=len(inc), n_out=len(exp), n_mv=len(items) - len(inc) - len(exp))

def main(src, dst):
    rows, dropped = load(src)
    moves = apple_moves(rows)
    out = {'_dropped_duplicates': dropped}
    ytd = 0
    for mo in range(1, 13):
        m = '2026-%02d' % mo
        mr = [r for r in rows if r['Date'].startswith(m)]
        if not mr: continue
        items = []
        for r in mr:
            kind, lab, cat = classify(r, moves)
            items.append(dict(date=r['Date'], kind=kind, label=lab, cat=cat, amt=round(float(r['Amount']), 2), acct=acct(r['Account'])))
        days = (dt.date(2026, mo % 12 + 1, 1) - dt.timedelta(days=1)).day if mo < 12 else 31
        b = month_block(items, m, days)
        b['ytdPrev'] = round(ytd, 2); ytd += b['net']; b['ytdEnd'] = round(ytd, 2)
        assert abs(b['cum'][-1] - b['net']) < 0.01
        out[m] = b
    json.dump(out, open(dst, 'w'), indent=1)
    return out

if __name__ == '__main__':
    o = main(sys.argv[1], sys.argv[2])
    print('dropped duplicate rows:', o['_dropped_duplicates'])
    for m in sorted(k for k in o if k.startswith('2026')):
        b = o[m]
        print(m, 'in %9.2f  out %9.2f  net %9.2f  ytd %9.2f' % (b['income'], b['spend'], b['net'], b['ytdEnd']))
