/* Builds the landing page from window.YEAR (data/2026-year.js) plus the month notes below.
   When a month closes: add its numbers to 2026-year.js and one entry to NOTES. */
(function () {
  'use strict';
  var Y = window.YEAR;
  var NOTES = [
    { tag: 'First month. Baselines set. Gym habit started.', chips: ['Gym started'] },
    { tag: 'Consistency over intensity.', chips: [] },
    { tag: 'Shipped the TaxiZero app, the JDM site rebuild, and an LMSW short film. Winter term closed at 3.83.', chips: ['3 projects shipped'] },
    { tag: 'Three career paths all in motion.', chips: ['Bench 195 lb', '3 paths open'] },
    { tag: 'United closed. OTS is the path. DD-368 sent. Photography delivered.', chips: ['Bench PR 215 lb', 'MBA 92.5% and 94%'] },
    { tag: 'DD-368 approved and sent to the Air Force recruiter; Jul 4 deadline met. Spring semester closed with a 4.0. Both outdoor runs came back faster.', chips: ['8 mi at 8:37', '4.000 term GPA'] },
    { tag: "Started as Administrative Coordinator at Clarkson's Lewis School. Training pivoted into frisbee, soccer, and outdoor running.", chips: ['New job Jul 20', '13.6 h cardio'] },
    { tag: 'Annual Training at Fort Drum, two weddings, and the AFOQT on Aug 31: quant 6, retest after 90 days.', chips: ['AFOQT Aug 31', '2 weddings'] },
    { tag: 'The routine month. The Verizon payoff put it in the red on purpose. Three MBA courses, a 23:39 5K, and the retest route set.', chips: ['Galatians 5 series'] },
    { tag: 'Wedding shoot, headshot studio launch, Camp Smith deployment screening, and a passed sheriff’s deputy agility test. Through Oct 30.', chips: ['Headshot studio', 'Agility test passed'] },
    { tag: 'AFOQT retest Nov 30 at Fort Drum. Semester closes Nov 10.', chips: ['Retest Nov 30'] },
    { tag: 'DPT White Coat ceremony Dec 11.', chips: ['White Coat Dec 11'] }
  ];
  var latest = -1;
  Y.net.forEach(function (v, i) { if (v != null) latest = i; });
  function money(n) { return (n < 0 ? '−' : '+') + '$' + Math.round(Math.abs(n)).toLocaleString('en-US'); }
  function sum(a) { return a.reduce(function (t, v) { return t + (v || 0); }, 0); }
  var NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

  var cards = Y.months.map(function (mo, i) {
    var done = Y.net[i] != null, n = NOTES[i] || { tag: '', chips: [] };
    var c = { spine: i === latest ? 'Latest' : done ? 'Closed' : 'Ahead', hue: i === latest ? 'red' : done ? 'teal' : 'slate',
      date: [mo.toUpperCase(), ('0' + (i + 1)).slice(-2), '2026'], title: NAMES[i], text: n.tag,
      tags: (done ? [money(Y.net[i]) + ' net', Y.gymDays[i] + ' gym days'] : []).concat(n.chips) };
    if (done) { c.href = Y.files[i]; c.foot = [Y.sermons[i] + ' sermons · ' + Math.round(Y.volume[i] / 1000) + 'k lb', 'Open']; }
    return c;
  }).reverse();

  var ytd = Y.ytd.value;
  var IV = Y.invest, ivStart = sum(IV.accounts.map(function (a) { return a.start; })), ivNow = sum(IV.accounts.map(function (a) { return a.now; }));
  function k(n) { return '$' + (n / 1000).toFixed(1) + 'k'; }
  function chg(a) { var d = a.now - a.start; return (d < 0 ? '−' : '+') + Math.abs(d / a.start * 100).toFixed(0) + '%'; }
  var ivMax = Math.max.apply(null, IV.accounts.map(function (a) { return Math.max(a.now, a.start); }));
  var investBand = { hue: 'teal', spine: 'Invested', blocks: [
    { type: 'sub', text: 'Investments vs Jan 1', right: 'tick = Jan start' },
    { type: 'goal', value: ivNow, target: ivStart, of: 'up from', note: money(ivNow - ivStart) + ' since January (' + ((ivNow / ivStart - 1) * 100).toFixed(0) + '%), about $' + IV.contributed.toLocaleString('en-US') + ' of it new money. As of ' + IV.asOf + '.' },
    { type: 'meter', max: ivMax, rows: IV.accounts.map(function (a) { return [a.name, a.now, k(a.now) + ' ' + chg(a), a.start]; }) }
  ] };
  window.RECAP = {
    meta: { label: '2026 Monthly Recap', short: 'Index', mIdx: latest, year: 2026, daysInMonth: 31, titleSuffix: ' · JD Meyers', prev: null, next: null },
    entities: { 'Clarkson': 'school', 'Lewis School': 'school', 'Air Force': 'org', 'Fort Drum': 'place' },
    header: {
      meta: [['Owner', 'JD Meyers'], ['Months', (latest + 1) + ' of 12'], ['Updated', 'Oct 31']],
      stats: [['YTD net', '$' + Math.round(ytd).toLocaleString('en-US')], ['Gym days', String(sum(Y.gymDays))], ['Sermons', String(sum(Y.sermons))]],
      ring: { pct: Math.round((latest + 1) / 12 * 100), text: String(latest + 1), cap: 'Months', sub: 'of 12 recapped' }
    },
    footnote: 'Monthly dashboards tracking financial, physical, spiritual, intellectual, and creative progress.',
    defaultDomain: 'story',
    noHero: true,
    domains: [
      { id: 'story', label: 'The year', hue: 'red', mainLabel: '2026 at a glance', sideLabel: 'Where it stands',
        main: [
          { hue: 'slate', spine: 'Threads', wide: true, blocks: [{ type: 'sub', text: 'Every thread of 2026, January to December', right: 'dot = milestone \u00b7 bar = span \u00b7 diamond = setback \u00b7 ring = next' }, { type: 'lanes', month: latest }] },
          { hue: 'violet', spine: 'In my words', blocks: [{ type: 'words' }] }
        ],
        side: [
          { hue: 'green', spine: 'Goals', blocks: [{ type: 'goalsum' }, { type: 'rows', items: [{ text: 'Open the full scorecard', href: '#goals' }] }] },
          { hue: 'red', spine: 'Now', type: 'kv', items: [['OTS', 'AFOQT retest Nov 30; board Jan 2027', { tag: 'Active' }], ['Job', 'Administrative Coordinator, Lewis School', { tag: 'Since Jul 20' }],
            ['MBA', 'Fall finals by Nov 10; May 2027 target'], ['Guard', 'ETS June 2027; last AFT 471 of 500'], ['Civil service', 'Sheriff\u2019s deputy agility test passed Oct 30'], ['Business', 'Studio launched in October; first 2027 booking in']] },
          { hue: 'teal', spine: 'Totals', type: 'kv', items: [['YTD net', '$' + Math.round(ytd).toLocaleString('en-US'), { big: true }], ['Gym days', String(sum(Y.gymDays)), { big: true }], ['Sermons', String(sum(Y.sermons))]] },
          investBand,
          { hue: 'teal', spine: 'Net', blocks: [{ type: 'sub', text: 'Net by month' }, { type: 'year', metric: 'net', fmt: 'money' }] }
        ] },
      { id: 'goals', label: '2026 goals', hue: 'green', mainLabel: 'Goals, set January 2026', sideLabel: 'Scorecard',
        main: [
          { hue: 'slate', spine: 'By month', blocks: [{ type: 'sub', text: 'The monthly goals, month by month', right: 'through ' + (window.GOALS ? window.GOALS.through : '') }, { type: 'checks' }] }
        ].concat((window.GOALS ? window.GOALS.groups : []).map(function (g) {
          var met = g.goals.filter(function (x) { return x.status === 'met'; }).length, tr = g.goals.filter(function (x) { return x.status !== 'open'; }).length;
          return { hue: g.hue, spine: g.label, blocks: [{ type: 'sub', text: g.label, right: met + ' of ' + tr + ' met' + (tr ? ' \u00b7 ' + Math.round(met / tr * 100) + '%' : '') }, { type: 'goalset', group: g.id }] };
        })),
        side: [
          { hue: 'green', spine: 'Score', blocks: [{ type: 'goalsum', verdict: true }] },
          investBand
        ] },
      { id: 'months', label: 'Months', hue: 'teal', count: latest + 1, mainLabel: '2026 by month', sideLabel: 'The year so far',
        main: [
          { hue: 'red', spine: 'Career', type: 'para', text: [
            '2026 is the year to lock in a career. United closed in May. DD-368 was approved and sent to the Air Force recruiter in June. The AFOQT on Aug 31 came back with verbal 61 and quant 6, below the minimum of 10, so the retest is set for Nov 30 at Fort Drum ahead of the January 2027 OTS board.',
            "In July, a new thread started: Administrative Coordinator at the Lewis School at Clarkson. The sheriff's deputy civil service path picked back up, and the agility test on Oct 30 was a pass."] },
          { hue: 'teal', spine: 'Months', type: 'cards', cards: cards }
        ],
        side: [
          { hue: 'teal', spine: 'Totals', type: 'kv', items: [
            ['YTD net', '$' + ytd.toLocaleString('en-US', { minimumFractionDigits: 2 }), { big: true }],
            ['Income', '$' + Math.round(sum(Y.income)).toLocaleString('en-US')], ['Spending', '$' + Math.round(sum(Y.expenses)).toLocaleString('en-US')],
            ['Gym days', String(sum(Y.gymDays))], ['Sermons', String(sum(Y.sermons))]] },
          { hue: 'teal', spine: 'Net', blocks: [{ type: 'sub', text: 'Net by month', right: 'tap a month' }, { type: 'year', metric: 'net', fmt: 'money' }] },
          { hue: 'green', spine: 'Gym', blocks: [{ type: 'sub', text: 'Gym days by month' }, { type: 'year', metric: 'gymDays', fmt: 'int', showAll: true }] },
          { hue: 'magenta', spine: 'Links', type: 'rows', items: [{ text: 'Sermon notes, all of 2026', href: 'cbc-sermons.html' }, { text: 'The year at a glance', href: '#story' }] }
        ] },
      { id: 'year', label: 'Year trends', hue: 'violet', mainLabel: '2026 trends', sideLabel: 'Savings goal',
        main: [
          { hue: 'green', spine: 'Income', blocks: [{ type: 'sub', text: 'Income by month' }, { type: 'year', metric: 'income', fmt: 'money', showAll: true }] },
          { hue: 'red', spine: 'Spending', blocks: [{ type: 'sub', text: 'Spending by month' }, { type: 'year', metric: 'expenses', fmt: 'money', showAll: true }] },
          { hue: 'teal', spine: 'Net', blocks: [{ type: 'sub', text: 'Net by month' }, { type: 'year', metric: 'net', fmt: 'money', showAll: true }] },
          { hue: 'violet', spine: 'Volume', blocks: [{ type: 'sub', text: 'Lifting volume by month, lb' }, { type: 'year', metric: 'volume', fmt: 'k', showAll: true }] },
          { hue: 'magenta', spine: 'Sermons', blocks: [{ type: 'sub', text: 'Sermons logged by month' }, { type: 'year', metric: 'sermons', fmt: 'int', showAll: true }] }
        ],
        side: [
          { hue: 'teal', spine: 'Goal', blocks: [{ type: 'goal', value: ytd, target: Y.savingsGoal, note: 'YTD rebuilt from Jan 1 with the full-year export.' }] },
          investBand,
          { hue: 'teal', spine: 'Accounts', type: 'kv', items: IV.accounts.map(function (a) { return [a.name, '$' + Math.round(a.now).toLocaleString('en-US') + ' (Jan $' + a.start.toLocaleString('en-US') + ')', { tag: a.note }]; }) }
        ] }
    ]
  };
})();
