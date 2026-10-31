"""Build data/sermons-2026.js: the single source for every CBC sermon note (Jan to Oct 2026)."""
import json, html, datetime as dt, re
S = '/tmp/claude-0/-home-claude/e2eb66b9-6aee-558a-b3a4-c4e64327d063/scratchpad/'
REPO = '/home/claude/monthly-recap/'
old = json.load(open(S + 'sermons_old.json'))

def clean(x):
    if isinstance(x, list): return [clean(i) for i in x]
    if isinstance(x, dict): return {k: clean(v) for k, v in x.items()}
    return html.unescape(html.unescape(x)).strip() if isinstance(x, str) else x

def iso(d):
    d = d.replace('June', 'Jun').replace('July', 'Jul')
    day = dt.datetime.strptime(d, '%b %d, %Y').date()
    if day.weekday() == 0: day -= dt.timedelta(days=1)  # Jan, Feb, Apr notes were dated the Monday after; services are Sundays
    return day.isoformat()

SERIES = {'acts': 'Acts', 'epistle': 'Teaching series', 'guest': 'Guest speaker'}
out = []
# Jan to Apr in the old sermon page did not match the voice notes (dates and passages were a guessed Acts sequence).
# Those months are rewritten below from the raw notes; May onward matches the notes and is kept.
old = [x for x in old if x['month'] not in ('jan', 'feb', 'mar', 'apr')]
for s in old:
    s = clean(s)
    out.append({'id': s['id'], 'date': iso(s['date']), 'series': SERIES[s['section']], 'title': s['title'], 'passage': s['book'],
                'themes': s['themes'], 'overview': s['overview'], 'points': s['points'], 'application': s['application'],
                'commentary': s.get('commentary', '')})

ACTS = 'Acts'
def S_(id, date, title, passage, themes, overview, points, application, series=ACTS):
    return {'id': id, 'date': date, 'series': series, 'title': title, 'passage': passage, 'themes': themes,
            'overview': overview, 'points': points, 'application': application, 'commentary': ''}
out += [
 S_('S2601a', '2026-01-04', 'Waiting on God', 'Acts 1', ['waiting', 'trust'],
    'Waiting on God is not like waiting on a pizza. The disciples were told to wait in Jerusalem for the promise, and waiting was part of the obedience.',
    ['Just because you cannot feel, taste, or touch what God is doing does not mean He is not moving.',
     'Waiting is active: stay where God put you instead of lining up people to take your side.',
     'Name the specific thing you have been waiting on and keep bringing it to Him.'],
    'Treat the waiting season as obedience, not lost time.'),
 S_('S2601b', '2026-01-11', 'The Day of Pentecost', 'Acts 2, Galatians 5:22 to 23', ['Holy Spirit', 'unity'],
    'The Spirit came on believers gathered in one accord and one place, fulfilling the promise of Acts 1. Notes were taken longhand.',
    ['They were all there for one purpose, and all of them were filled, not just the leaders.',
     'Spirit-filling shows up as fruit: changed character, not just an emotional moment.',
     'We do not have to try harder to be filled. God wants us free from the guilt of sin.'],
    'Yield instead of strive; the filling is offered to everyone.'),
 S_('S2601c', '2026-01-25', 'Peter, restored', 'Luke 5, Luke 22:47, Acts 2', ['restoration', 'Peter'],
    'Peter went from a half-hearted net cast and a denial in the garden to standing up and preaching. The difference was the Holy Spirit, not willpower.',
    ['Peter was always the first to put his foot in his mouth; Jesus used him anyway.',
     'Most believers ride a roller coaster of commitment, which is why church can look inconsistent.',
     'The Holy Spirit leads into all truth; real change comes from Him, not from another rededication.'],
    'Stop restarting on your own strength and let the Spirit lead.'),
 S_('S2602a', '2026-02-01', 'Peter and John before the council', 'Acts 3 to 4', ['boldness', 'faith', 'testimony'],
    'Peter and John healed in Jesus\u2019 name and were hauled in for it. Brad tied it to righteous judgment and to drawing attention to what God has done.',
    ['God is not going to move on our behalf without faith.',
     'We can judge, but we have to do it righteously.',
     'Point people to what God has done in your life; that was the apostles\u2019 whole defense.'],
    'Tell someone this week what God has actually done for you.'),
 S_('S2602b', '2026-02-08', 'Silver and gold I have none', 'Acts 3', ['healing', 'witness'],
    'A short set of notes on Acts 3: after the chaos of Pentecost, Peter and John meet the lame man at the temple gate.',
    ['Peter had no money to give, but he had the name of Jesus.',
     'The healing opened the door for Peter to preach to a crowd that was already watching.'],
    'Give what you actually have.'),
 S_('S2602c', '2026-02-15', 'What God is really looking for', 'Malachi 3, Matthew 11 to 12, Acts 4', ['giving', 'the heart', 'trust'],
    'Brad separated Old Testament tithes and sacrifices from what God asks of the church now: trust and a changed heart, not rule-keeping out of fear.',
    ['Much of American church giving is driven by fear from Malachi 3, which was written to Israel under the law.',
     'The early church gave because they trusted each other and trusted God.',
     'Wanting to look holy without wanting to be holy is the trap.'],
    'Give out of trust, not fear.'),
 S_('S2603a', '2026-03-01', 'The seven deacons', 'Acts 6, Philippians 4:6 to 7', ['service', 'peace'],
    'Bob shared about peace after his heart attack. Brad then walked through Acts 6, where the first deacons are set apart, Stephen among them.',
    ['Think of church offices as functions, not titles.',
     'Deacons were boots on the ground so the apostles could keep the word central.',
     'Stephen was accused of blasphemy for simply doing what God asked.'],
    'Find the function God gave you in the body and do it.'),
 S_('S2603b', '2026-03-08', 'Persecution and the spread', 'Acts 7 to 8', ['persecution', 'love God first'],
    'Picking up from Stephen, the first martyr, Brad warned that real persecution is coming for the American church and that only the Spirit prepares you for it.',
    ['Stephen was the first to die proclaiming the gospel after Jesus.',
     'We have to love God first; everything else falls in line after that.',
     'Persecution scattered the church, and the message spread with it.'],
    'If God is dealing with you on something, today is the day.'),
 S_('S2603c', '2026-03-22', 'Saul on the road to Damascus', 'Acts 9', ['conversion', 'grace'],
    'One of the most dramatic conversions in Scripture: the man who held coats at Stephen\u2019s death meets Jesus.',
    ['God wants to reveal Himself to people, even the ones fighting Him.',
     'Nobody is right all the time; Saul was sincere and still wrong.',
     'As Easter approaches, the question is whether you have moved past just hearing about Jesus.'],
    'Let God interrupt the road you are on.'),
 S_('S2603d', '2026-03-29', 'The message of the cross', '1 Corinthians 1:18, Matthew 27, Luke 22:41 to 42, Isaiah 53', ['the cross', 'Palm Sunday'],
    'Palm Sunday. The crowd cheering Jesus into Jerusalem was screaming for His death days later. Brad preached the cross itself.',
    ['To the lost, trusting a bleeding, crucified man for salvation looks foolish.',
     'God does not want forms and ritual; the cross brings us to say yes and amen to who Jesus is.',
     'This is why the church loves each other and why the world is not fond of it.'],
    'Settle what you believe about the cross before Easter.'),
 S_('S2605c', '2026-05-24', 'Trusting God when prayers go unanswered', 'Judges 4 to 5', ['trust', 'disappointment'],
    'Start of a trust series built from questions people had been asking Brad for six months.',
    ['Everyone trusts God when it is easy; the question is the hard times.',
     'Deborah drew her trust from God and spent her time accordingly.',
     'Put the energy you spend worrying into trusting instead.'],
    'Trust God even when the answer is not yet.', 'Trust series'),
 S_('S2605d', '2026-05-31', 'Trusting God when you have suffered long', 'Mark 5, Luke 8, Isaiah', ['trust', 'suffering'],
    'Second week of the trust series: how to trust God after a long season of suffering.',
    ['Line up with Scripture; at some point every believer has to learn to feed themselves.',
     'The woman who bled for twelve years still reached for Jesus.',
     'Share what you are going through; struggling alone is where trust erodes.'],
    'Keep reaching, and do not suffer in silence.', 'Trust series'),
]

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
for s_ in out:
    if s_['date'] in ('2026-06-07', '2026-06-28'): s_['series'] = 'Trust series'
    elif s_['date'] == '2026-07-26': s_['series'] = 'Conviction'
    elif s_['series'] == 'Teaching series': s_['series'] = 'Standalone'
out.sort(key=lambda s: s['date'])
assert len(out) == 27, len(out)
js = ('/* Every CBC sermon note for 2026. The sermon page and each month\'s Spiritual tab read from here.\n'
      '   Add a sermon: append one object (date as YYYY-MM-DD). Brad = pastor, first name only. */\n'
      'window.SERMONS = ' + json.dumps(out, ensure_ascii=True, indent=1) + ';\n')
open(REPO + 'data/sermons-2026.js', 'w').write(js)
print(len(out), 'sermons')
