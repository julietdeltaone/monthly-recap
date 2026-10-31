/* 2026 goals, set January 2026, scored through Oct 30.
   status: met | close | behind | open (not tracked)
   pct:   progress toward the target, 0 to 100 (omit when it does not apply)
   delta: distance from the target, signed; good: true when the delta is on the right side of the target
   Sources: data/2026-year.js (money, gym, sermons), FitNotes backup (lifts, runs, plank), May recap (HRPU 42),
   Projects ledger in Notion (shoots, 2027 booking), JD (AFT 471, agility test), M1 / Fidelity / Robinhood (Oct 31). */
window.GOALS = {
  through: 'Oct 30',
  verdict: 'Ten months in, the plan held where it counted. Savings, tithe, the business, and the career search all hit or beat their targets, and every AFT event standard but push-ups has been reached in training, where push-ups sit one rep short. The misses are concentrated in two places: monthly spending ran right at the $2,500 cap instead of under it, and the upper-body accessory PRs stalled after spring. Faith and study habits were kept up but never tracked well enough to score.',
  groups: [
    { id: 'money', label: 'Money', hue: 'teal',
      take: 'The savings goal was cleared by June and finished 77% over target. Spending is the soft spot: half the months went over, mostly from one-off buys (Apple lease swap, Verizon payoff, B&H studio gear), and the average landed $22 above the cap.',
      goals: [
      { goal: 'Save $10,000', target: '$10,000', actual: '$17,731', delta: '+$7,731', good: true, status: 'met', pct: 100, note: 'Passed $10k in June' },
      { goal: 'Tithe $250 every month', target: '10 months', actual: '10 of 10', delta: '+$300 extra in Aug', good: true, status: 'met', pct: 100 },
      { goal: 'Spend no more than $2,500 a month', target: '$2,500 avg', actual: '$2,522 avg', delta: '+$22 over', good: false, status: 'close', pct: 50, note: 'Under the cap in 5 of 10 months; over in Jan, May, Aug, Sep, Oct' },
      { goal: 'Keep checking above $1,000', target: '$1,000', actual: '$4,197', delta: '+$3,197', good: true, status: 'met', pct: 100 },
      { goal: 'Grow investment balances', target: '$55,200 start', actual: '$64,600', delta: '+$9,400 (+17%)', good: true, status: 'met', pct: 100, note: 'About $1,650 of it new contributions; the rest market gains' }
    ] },
    { id: 'fit', label: 'Fitness', hue: 'violet',
      take: 'Four of five AFT event standards have been beaten in training, and the last official score was 471 of 500. The two-mile came in 1:35 under the goal and the plank 35 seconds over. Push-ups are the one event still at the edge: 42 hand-release in May against a 43 target.',
      goals: [
      { goal: 'AFT: 90+ points in every event', target: '450 of 500', actual: '471 of 500', delta: '+21 points', good: true, status: 'met', pct: 100, note: 'Average of 94 per event; event-by-event scores not recorded' },
      { goal: 'Trap bar deadlift 230 lb x3', target: '230 x3', actual: '355 x5', delta: '+125 lb', good: true, status: 'met', pct: 100, note: 'First hit Jan 31' },
      { goal: '43 hand-release push-ups', target: '43', actual: '42', delta: '−1 rep', good: false, status: 'close', pct: 98, note: 'May test' },
      { goal: 'Plank 2:25', target: '2:25', actual: '3:00', delta: '+0:35', good: true, status: 'met', pct: 100 },
      { goal: 'Two-mile run 15:50', target: '15:50', actual: '14:15', delta: '−1:35 faster', good: true, status: 'met', pct: 100, note: 'Sep 29' },
      { goal: '3+ training days every week', target: '43 weeks', actual: '37 weeks', delta: '−6 weeks', good: false, status: 'close', pct: 86, note: 'Three of the six short weeks were Annual Training in August' },
      { goal: 'Cardio every week', target: '43 weeks', actual: '38 weeks', delta: '−5 weeks', good: false, status: 'close', pct: 88 }
    ] },
    { id: 'pr', label: 'Gym PRs', hue: 'violet',
      take: 'One of six PR goals is done (the curl) and three are within a rep or ten pounds. Shoulder press and triceps have not moved since spring; training shifted toward running and test prep after June.',
      goals: [
      { goal: 'Deadlift 315 x8', target: '315 x8', actual: '315 x7', delta: '−1 rep', good: false, status: 'close', pct: 88, note: 'Sep 22' },
      { goal: 'Bench press 225 x4', target: '225 x4', actual: '215 x4', delta: '−10 lb', good: false, status: 'close', pct: 96, note: 'Mar 23' },
      { goal: 'Dumbbell curl 90 x4', target: '90 x4', actual: '90 x4', delta: 'On target', good: true, status: 'met', pct: 100, note: 'Jul 21' },
      { goal: 'Cable crunch 180 x6', target: '180 x6', actual: '180 x4', delta: '−2 reps', good: false, status: 'close', pct: 67, note: 'Also 170 x8' },
      { goal: 'Dumbbell shoulder press 120 x6', target: '120 x6', actual: '100 x5', delta: '−20 lb', good: false, status: 'behind', pct: 69, note: 'Apr 2' },
      { goal: 'Cable triceps 80 x8', target: '80 x8', actual: '60 x8', delta: '−20 lb', good: false, status: 'behind', pct: 75, note: 'Mar 23' }
    ] },
    { id: 'faith', label: 'Faith', hue: 'magenta',
      take: 'Notes exist for 27 Sundays across six series. April has none and August only one (Annual Training). Daily reading and prayer are the stated focus for the rest of the year, but they are not logged anywhere this site can see.',
      goals: [
      { goal: 'Sermon notes every Sunday attended', target: '43 Sundays', actual: '27 Sundays', delta: '−16', good: false, status: 'close', pct: 63, note: 'Sundays away or not attended are not separated out' },
      { goal: 'Weekly Bible reading and prayer summary', actual: 'Not tracked here', status: 'open' },
      { goal: 'Reading plan: Mark to 2 Timothy', actual: 'Not tracked here', status: 'open' }
    ] },
    { id: 'learn', label: 'Learning', hue: 'blue',
      take: 'The monthly topic plan bent to real life: the MBA, an Army course, and AFOQT prep took several slots, and only February was a true miss. The MBA itself is the standout, at 3.83 and then 4.0, with fall courses running 92 to 97%.',
      goals: [
      { goal: 'A study topic every month', target: '10 months', actual: '9 months', delta: '−1 (Feb)', good: false, status: 'close', pct: 90, note: '4 of the 9 were swapped for MBA, Army, or AFOQT work' },
      { goal: 'One written summary per month', actual: 'Not tracked here', status: 'open' },
      { goal: 'MBA (added during the year)', target: 'Pass every course', actual: '3.92 cumulative', delta: 'All A range', good: true, status: 'met', pct: 100, note: 'Fall finals Nov 3 to 10' }
    ] },
    { id: 'jdm', label: 'Business', hue: 'amber',
      take: 'A strong year for the business: both targets beaten by October, about $7,400 in card payments through Square, a headshot studio launched, and the first 2027 booking already holds a deposit.',
      goals: [
      { goal: 'Complete 3 to 4 weddings', target: '4', actual: '7', delta: '+3', good: true, status: 'met', pct: 100, note: '3 photo, 4 video' },
      { goal: 'Complete 6 photo shoots', target: '6', actual: '9', delta: '+3', good: true, status: 'met', pct: 100, note: 'Plus a Sep 2027 event booked' }
    ] },
    { id: 'career', label: 'Career', hue: 'red',
      take: 'The plan was to keep every door open and let the year choose. It did: United closed in May, the Lewis School job arrived in July, the sheriff’s deputy agility test was passed Oct 30, and OTS comes down to the Nov 30 retest and a January board.',
      goals: [
      { goal: 'Run every path at once; let the year narrow it', target: 'One path', actual: '2 live paths', delta: 'United closed', good: true, status: 'met', pct: 100, note: 'OTS retest Nov 30; civil service agility passed' }
    ] }
  ],
  /* month by month: 1 met, 0.5 partial, 0 missed, null ahead */
  months: [
    { label: 'Tithe $250', hue: 'teal', vals: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, null, null] },
    { label: 'Spend under $2,500', hue: 'teal', vals: [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, null, null], tips: ['$3,048', '$2,255', '$2,051', '$1,738', '$2,914', '$1,886', '$2,441', '$3,117', '$3,230', '$2,541'] },
    { label: 'Saved money', hue: 'teal', vals: [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, null, null], tips: ['+$465', '+$641', '+$1,413', '+$4,194', '+$1,488', '+$2,422', '+$247', '+$4,065', '−$589', '+$3,383'] },
    { label: '13+ gym days', hue: 'violet', vals: [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, null, null], tips: ['17', '18', '20', '24', '21', '22', '23', '12', '28', '17'] },
    { label: 'Sermon notes', hue: 'magenta', vals: [0.5, 0.5, 0.5, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, null, null], tips: ['3 of 4', '3 of 4', '4 of 5', '0 of 4', '4 of 5', '3 of 4', '3 of 4', '1 of 5', '3 of 4', '3 of 4'] },
    { label: 'Study topic', hue: 'blue', vals: [1, 0, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, null, null], tips: ['Personal finance', 'Missed', 'Swapped for Army MMCS course', 'Leadership (MBA)', 'Marketing (MBA)', 'Military history', 'Swapped for strategy reading', 'Swapped for AFOQT prep', 'MBA fall term', 'MBA fall term'] }
  ]
};
