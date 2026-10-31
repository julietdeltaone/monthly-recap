/* 2026 year-level figures shared by every page (year bars, goal, trends, index).
   Money: rebuilt Oct 30 from the full-year Origin export with tools/finance.py, which removes the
   Chase Sapphire feed that double-imported the same card Jan to Jul. Oct is through the 30th.
   Gym days and volume: FitNotes backup (Oct 30) via tools/fitnotes.py. Sermons: data/sermons-2026.js.
   Add one value per array when a month closes. null = not recorded. */
window.YEAR = {
  months:   ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  files:    ['2026-01.html', '2026-02.html', '2026-03.html', '2026-04.html', '2026-05.html', '2026-06.html', '2026-07.html', '2026-08.html', '2026-09.html', '2026-10.html', null, null],
  net:      [465.41, 640.76, 1413.45, 4194.44, 1488.27, 2422.24, 246.63, 4065.06, -588.90, 3383.35, null, null],
  income:   [3513.28, 2895.62, 3464.37, 5932.72, 4402.13, 4307.96, 2687.58, 7181.71, 2641.19, 5923.87, null, null],
  expenses: [3047.87, 2254.86, 2050.92, 1738.28, 2913.86, 1885.72, 2440.95, 3116.65, 3230.09, 2540.52, null, null],
  gymDays:  [17, 18, 20, 24, 21, 22, 23, 12, 28, 17, null, null],
  volume:   [96108, 110005, 137845, 128418, 88290, 114465, 108355, 72905, 166118, 102845, null, null],
  sermons:  [3, 3, 4, 0, 4, 3, 3, 1, 3, 3, null, null],
  ytd: { through: 'Oct 30', value: 17730.71 },
  savingsGoal: 10000,
  /* Investments: Jan 1 baseline from the 2026 plan; current values as of Oct 30 to 31.
     M1 from Plaid (Oct 30 close), Robinhood and Fidelity from their account pages (Oct 31). */
  invest: {
    asOf: 'Oct 31',
    accounts: [
      { name: 'M1 brokerage', start: 35000, now: 40668.85, note: 'SPY, XLE, JBND' },
      { name: 'M1 Roth IRA', start: 10000, now: 13401.01, note: 'VTI, RSP, VT' },
      { name: 'Fidelity 403(b)', start: 6200, now: 6681.90, note: 'Held in cash' },
      { name: 'Robinhood', start: 4000, now: 3848.02, note: 'Crypto and stocks' }
    ],
    contributed: 1650
  }
};
