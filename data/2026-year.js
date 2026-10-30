/* 2026 year-level figures shared by every month page (year bars, goal, trends).
   Add one value per array when a month closes. null = not recorded.
   Jan to Jul net/income/expenses come from the July file; Aug from the August file;
   Sep and Oct from the Origin export dated Oct 30 (Oct is through the 30th).
   Month nets sum to slightly more than the chained YTD because of the August YTD correction (-$56.74). */
window.YEAR = {
  months:   ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  files:    ['2026-01.html', '2026-02.html', '2026-03_v2.html', '2026-04.html', '2026-05.html', '2026-06.html', '2026-07.html', '2026-08.html', '2026-09.html', '2026-10.html', null, null],
  net:      [865.41, 1094.28, 1444.32, 4233.98, 2883.12, 2464.22, 600.08, 4121.80, -588.90, 3383.35, null, null],
  income:   [3513.28, 2883.81, 3492.00, 5979.54, 5659.60, 4322.96, 2687.28, 7107.60, 2641.19, 5923.87, null, null],
  expenses: [2647.87, 1789.53, 2637.26, 1745.56, 2776.48, 1858.74, 2087.20, 2985.80, 3230.09, 2540.52, null, null],
  gymDays:  [13, 18, 20, 24, 20, 21, 18, 10, 28, 17, null, null],
  volume:   [88392, 110005, 137105, 128418, 87390, 114025, 81365, 72905, 166118, 102845, null, null],
  sermons:  [4, 4, 5, 4, 2, 3, 3, 1, 3, 3, null, null],
  ytd: { anchor: 'Aug', value: 17650.47, note: 'Corrected August close; later months chain from it.' },
  savingsGoal: 10000
};
