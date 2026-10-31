/* 2026 goals, set January 2026, scored through Oct 30.
   status: met | close | behind | open (not tracked)
   pct: progress toward the target, 0 to 100 (omit when it does not apply).
   Sources: data/2026-year.js (money, gym, sermons), FitNotes backup (lifts, runs, plank, push-ups),
   Projects ledger (shoots), JD (AFT 471, agility test). */
window.GOALS = {
  through: 'Oct 30',
  groups: [
    { id: 'money', label: 'Money', hue: 'teal', goals: [
      { goal: 'Save $10,000', actual: '$17,731 saved', status: 'met', pct: 100, note: 'Passed $10k in June' },
      { goal: 'Tithe $250 every month', actual: '10 of 10 months', status: 'met', pct: 100 },
      { goal: 'Spend no more than $2,500 a month', actual: '5 of 10 months', status: 'close', pct: 50, note: 'Average $2,522; over in Jan, May, Aug, Sep, Oct' },
      { goal: 'Keep checking above $1,000', actual: '$4,197 now', status: 'met', pct: 100 },
      { goal: 'Track investment balances', actual: '$64,600, up 17%', status: 'met', pct: 100, note: 'From $55,200 on Jan 1' }
    ] },
    { id: 'fit', label: 'Fitness', hue: 'violet', goals: [
      { goal: 'AFT: 90+ points in every event', actual: '471 of 500', status: 'met', pct: 94, note: 'Event-by-event scores not recorded' },
      { goal: 'Trap bar deadlift 230 lb x3', actual: '355 lb x5', status: 'met', pct: 100, note: 'First hit Jan 31' },
      { goal: '43 hand-release push-ups', actual: '36 push-ups logged', status: 'close', pct: 84, note: 'Best logged set, Oct 13' },
      { goal: 'Plank 2:25', actual: '3:00', status: 'met', pct: 100 },
      { goal: 'Two-mile run 15:50', actual: '14:15', status: 'met', pct: 100, note: 'Sep 29' },
      { goal: '3+ training days every week', actual: '37 of 43 weeks', status: 'close', pct: 86 },
      { goal: 'Cardio every week', actual: '38 of 43 weeks', status: 'close', pct: 88 }
    ] },
    { id: 'pr', label: 'Gym PRs', hue: 'violet', goals: [
      { goal: 'Deadlift 315 x8', actual: '315 x7', status: 'close', pct: 88, note: 'One rep short, Sep 22' },
      { goal: 'Bench press 225 x4', actual: '215 x4', status: 'close', pct: 96, note: 'Mar 23' },
      { goal: 'Dumbbell curl 90 x4', actual: '90 x4', status: 'met', pct: 100, note: 'Jul 21' },
      { goal: 'Cable crunch 180 x6', actual: '180 x4', status: 'close', pct: 67, note: 'Also 170 x8' },
      { goal: 'Dumbbell shoulder press 120 x6', actual: '100 x5', status: 'behind', pct: 69 },
      { goal: 'Cable triceps 80 x8', actual: '60 x8', status: 'behind', pct: 75 }
    ] },
    { id: 'faith', label: 'Faith', hue: 'magenta', goals: [
      { goal: 'Sermon notes every Sunday attended', actual: '27 of 43 Sundays', status: 'close', pct: 63, note: 'No notes in April' },
      { goal: 'Weekly Bible reading and prayer summary', actual: 'Not tracked here', status: 'open' },
      { goal: 'Reading plan: Mark to 2 Timothy', actual: 'Not tracked here', status: 'open' }
    ] },
    { id: 'learn', label: 'Learning', hue: 'blue', goals: [
      { goal: 'A study topic every month', actual: '9 of 10 months', status: 'close', pct: 90, note: 'February missed; MBA courses and AFOQT prep took several slots' },
      { goal: 'One written summary per month', actual: 'Not tracked here', status: 'open' },
      { goal: 'MBA (added during the year)', actual: '3.83, then 4.0', status: 'met', pct: 100, note: 'Fall term finals Nov 3 to 10' }
    ] },
    { id: 'jdm', label: 'Business', hue: 'amber', goals: [
      { goal: 'Complete 3 to 4 weddings', actual: '7 wedding jobs', status: 'met', pct: 100, note: '3 photo, 4 video' },
      { goal: 'Complete 6 photo shoots', actual: '9 shoots', status: 'met', pct: 100 }
    ] },
    { id: 'career', label: 'Career', hue: 'red', goals: [
      { goal: 'Run every path at once; let the year narrow it', actual: 'Narrowed as planned', status: 'met', pct: 100, note: 'United closed, OTS retest Nov 30, agility test passed, new job in July' }
    ] }
  ],
  /* month by month: 1 met, 0.5 partial, 0 missed, null not yet */
  months: [
    { label: 'Tithe $250', hue: 'teal', vals: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, null, null] },
    { label: 'Spend under $2,500', hue: 'teal', vals: [0, 1, 1, 1, 0, 1, 1, 0, 0, 0, null, null] },
    { label: 'Saved money', hue: 'teal', vals: [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, null, null] },
    { label: '13+ gym days', hue: 'violet', vals: [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, null, null] },
    { label: 'Sermon notes', hue: 'magenta', vals: [0.5, 0.5, 0.5, 0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, null, null], tips: ['3 of 4', '3 of 4', '4 of 5', '0 of 4', '4 of 5', '3 of 4', '3 of 4', '1 of 5', '3 of 4', '3 of 4'] },
    { label: 'Study topic', hue: 'blue', vals: [1, 0, 0.5, 1, 1, 1, 0.5, 0.5, 1, 1, null, null], tips: ['Personal finance', 'Missed', 'Swapped for Army MMCS course', 'Leadership (MBA)', 'Marketing (MBA)', 'Military history', 'Swapped for strategy reading', 'Swapped for AFOQT prep', 'MBA fall term', 'MBA fall term'] }
  ]
};
