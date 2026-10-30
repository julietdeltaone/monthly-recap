/* 2026 year-level figures shared by every page (year bars, goal, trends, index).
   Money: rebuilt Oct 30 from the full-year Origin export with tools/finance.py, which removes the
   Chase Sapphire feed that double-imported the same card Jan to Jul. Oct is through the 30th.
   Gym days, volume, sermons: from each month's page until the full-year FitNotes rebuild.
   Add one value per array when a month closes. null = not recorded. */
window.YEAR = {
  months:   ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  files:    ['2026-01.html', '2026-02.html', '2026-03.html', '2026-04.html', '2026-05.html', '2026-06.html', '2026-07.html', '2026-08.html', '2026-09.html', '2026-10.html', null, null],
  net:      [465.41, 640.76, 1413.45, 4194.44, 1488.27, 2422.24, 246.63, 4065.06, -588.90, 3383.35, null, null],
  income:   [3513.28, 2895.62, 3464.37, 5932.72, 4402.13, 4307.96, 2687.58, 7181.71, 2641.19, 5923.87, null, null],
  expenses: [3047.87, 2254.86, 2050.92, 1738.28, 2913.86, 1885.72, 2440.95, 3116.65, 3230.09, 2540.52, null, null],
  gymDays:  [13, 18, 20, 24, 20, 21, 18, 10, 28, 17, null, null],
  volume:   [88392, 110005, 137105, 128418, 87390, 114025, 81365, 72905, 166118, 102845, null, null],
  sermons:  [4, 4, 5, 4, 2, 3, 3, 1, 3, 3, null, null],
  ytd: { through: 'Oct 30', value: 17730.71 },
  savingsGoal: 10000
};
