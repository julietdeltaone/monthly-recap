"""Build data/sermons-2026.js: the single source for every CBC sermon note (Jan to Oct 2026)."""
import json, html, datetime as dt, re
S = '/tmp/claude-0/-home-claude/e2eb66b9-6aee-558a-b3a4-c4e64327d063/scratchpad/'
REPO = '/home/claude/monthly-recap/'
old = json.load(open(S + 'sermons_old.json'))

def clean(x):
    if isinstance(x, list): return [clean(i) for i in x]
    return html.unescape(x).strip() if isinstance(x, str) else x

def iso(d):
    d = d.replace('June', 'Jun').replace('July', 'Jul')
    return dt.datetime.strptime(d, '%b %d, %Y').date().isoformat()

SERIES = {'acts': 'Acts', 'epistle': 'Teaching series', 'guest': 'Guest speaker'}
out = []
for s in old:
    s = clean(s)
    out.append({'id': s['id'], 'date': iso(s['date']), 'series': SERIES[s['section']], 'title': s['title'], 'passage': s['book'],
                'themes': s['themes'], 'overview': s['overview'], 'points': s['points'], 'application': s['application'],
                'commentary': s.get('commentary', '')})

# August: from the August recap page
out.append({'id': 'S2608a', 'date': '2026-08-02', 'series': 'Conviction', 'title': 'Repentance & Confession', 'passage': 'James 5:16',
  'themes': ['conviction', 'confession', 'community'],
  'overview': 'A season of conviction: the Holy Spirit surfacing things He has not convicted of before, things that used to be easy to excuse.',
  'points': ['Conviction answered promptly draws you toward God; left sitting, it curdles into condemnation, which pulls you away from His presence.',
             "Brad's illustration was his own mother: decades of unaddressed jealousy turned into church-hopping and burned bridges, even with her sons.",
             'Confession is individual and corporate: let the body of Christ close enough to speak into your life.'],
  'application': 'Respond to conviction right away, and let others in close enough to call it out.', 'commentary': ''})

FRUIT = 'Fruit of the Spirit'
out += [
 {'id': 'S2609a', 'date': '2026-09-13', 'series': FRUIT, 'title': 'Stand fast in freedom', 'passage': 'Galatians 5:1 to 15',
  'themes': ['liberty', 'law', 'love'],
  'overview': 'Brad opened the Galatians 5 series alongside church small groups. Paul is confronting a church that slid back into rule-keeping after he left.',
  'points': ['"Stand fast" is a military term: brace yourself for what is coming.',
             'Freedom in Christ is not a license for the flesh. The point of liberty is to serve one another in love.',
             'The whole law is fulfilled in one command: love your neighbor as yourself. Biting and devouring each other consumes the body.'],
  'application': 'Use freedom to serve the people in your local body, not to excuse the flesh.', 'commentary': ''},
 {'id': 'S2609b', 'date': '2026-09-20', 'series': FRUIT, 'title': 'Walk by the Spirit', 'passage': 'Galatians 5:16 to 26, 1 John 4',
  'themes': ['love', 'flesh and Spirit'],
  'overview': 'The prerequisite for any fruit is walking in the Spirit, and the first fruit is love.',
  'points': ['Walking in the Spirit means how you live: talk, posture, presence. Without it, you are already feeding the flesh.',
             'The struggle never fully ends on this side of heaven; flesh and Spirit stay at war, as Paul admits in Romans 7.',
             'Love is the root of the rest. Perfected love is what sustains the church through hard times.'],
  'application': 'Love each other the way the Bible commands, starting with the people in this room.', 'commentary': ''},
 {'id': 'S2609c', 'date': '2026-09-27', 'series': FRUIT, 'title': 'Joy starts at salvation', 'passage': 'Psalm 95:1, John 15, Nehemiah 9',
  'themes': ['joy', 'salvation', 'testimony'],
  'overview': 'Real joy comes after bending the knee to Christ, and it does not depend on feelings.',
  'points': ["Bob's plain, non-emotional testimony led two people to faith that week.",
             "Joy and peace are the two things with no counterfeit. Persecuted believers keep joy because God's presence is more real than their circumstances.",
             'Brad shared his own season of despair as a pastor and how joy carried him through it.'],
  'application': 'Nobody can hand you joy. It comes from your own relationship with Jesus.', 'commentary': ''},
 {'id': 'S2610a', 'date': '2026-10-04', 'series': FRUIT, 'title': 'Where peace starts', 'passage': 'Romans 10:9, Philippians 2:12',
  'themes': ['peace', 'accountability', 'discipline'],
  'overview': 'Peace rests on three things: salvation, relationship, and discipline.',
  'points': ['Salvation: believe and confess Jesus with your whole life, including how you spend money and raise children.',
             'Relationship: be plugged into a local body for accountability and perspective. No one, including a pastor, should lead without it.',
             'Discipline: cut the distractions, social media first, and help children build their own prayer lives.'],
  'application': 'Cut one distraction and replace it with prayer.', 'commentary': ''},
 {'id': 'S2610b', 'date': '2026-10-11', 'series': FRUIT, 'title': 'Long-suffering', 'passage': 'Galatians 5:22, 2 Peter 3:9, Hebrews 6:11 to 12',
  'themes': ['patience', 'promises', 'repentance'],
  'overview': "Patience is rooted in trusting God's promises.",
  'points': ['It starts with "I will never leave you nor forsake you."',
             'God is not slow; His patience is giving people time to repent. Repentance is a lifestyle, not a one-time event.',
             'Slow down. Superficial connections, online and in church, keep people from the depth that patience builds.'],
  'application': 'Exercise patience where it is hardest, and keep repenting as a habit.', 'commentary': ''},
 {'id': 'S2610c', 'date': '2026-10-18', 'series': FRUIT, 'title': 'Kindness rooted in truth', 'passage': 'Galatians 5:22, Colossians 3:12, Ephesians 2:4',
  'themes': ['kindness', 'truth', 'forgiveness'],
  'overview': "Genuine kindness flows from God's love for us; without love in the heart it stays superficial.",
  'points': ['Real kindness is grounded in truth and sometimes does not feel kind.',
             "Jerry's \"work it out, don't let the sun go down on your anger\" was kindness.",
             'Clothe yourselves with compassion, kindness, humility, gentleness, and patience. Love binds them together.'],
  'application': 'Keep running back to the Father, again and again.', 'commentary': ''},
]
out.sort(key=lambda s: s['date'])
assert len(out) == 25 + 1 + 6, len(out)
js = ('/* Every CBC sermon note for 2026. The sermon page and each month\'s Spiritual tab read from here.\n'
      '   Add a sermon: append one object (date as YYYY-MM-DD). Brad = pastor, first name only. */\n'
      'window.SERMONS = ' + json.dumps(out, ensure_ascii=True, indent=1) + ';\n')
open(REPO + 'data/sermons-2026.js', 'w').write(js)
print(len(out), 'sermons')
