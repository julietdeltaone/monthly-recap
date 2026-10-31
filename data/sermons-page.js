/* Builds the sermon page from window.SERMONS (data/sermons-2026.js).
   Nothing to edit here when a sermon is added; months, counts and Sundays update on their own.
   Links like cbc-sermons.html#aug still open that month. */
(function () {
  'use strict';
  var S = (window.SERMONS || []).slice().sort(function (a, b) { return a.date < b.date ? -1 : 1; });
  var MON = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
  var NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var SERIES_HUE = { 'Acts': 'sky', 'Standalone': 'teal', 'Trust series': 'green', 'Guest speaker': 'amber', 'Conviction': 'orange', 'Fruit of the Spirit': 'magenta' };
  var NOTES = { '2026-10-25': 'Drill weekend at Camp Smith' };
  var year = 2026, last = S.length ? S[S.length - 1].date : year + '-01-01';
  var lastDate = new Date(last + 'T12:00:00');

  function sundays(mi) {
    var out = [], d = new Date(year, mi, 1);
    while (d.getDay() !== 0) d.setDate(d.getDate() + 1);
    for (; d.getMonth() === mi; d.setDate(d.getDate() + 7)) out.push(new Date(d));
    return out;
  }
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function short(d) { return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); }

  var byDate = {}, series = {}, months = [];
  S.forEach(function (s) { byDate[s.date] = s; series[s.series] = (series[s.series] || 0) + 1; });
  var totalSundays = 0;
  for (var mi = 0; mi <= lastDate.getMonth(); mi++) {
    var key = year + '-' + ('0' + (mi + 1)).slice(-2);
    var list = S.filter(function (s) { return s.date.slice(0, 7) === key; });
    var suns = sundays(mi).filter(function (d) { return d <= lastDate || d.getMonth() === lastDate.getMonth(); });
    totalSundays += suns.length;
    var ser = {};
    list.forEach(function (s) { ser[s.series] = 1; });
    var serNames = Object.keys(ser);
    months.push({
      id: MON[mi], label: NAMES[mi].slice(0, 3), hue: 'magenta', count: list.length,
      mainLabel: NAMES[mi] + ' sermons', sideLabel: NAMES[mi] + ' Sundays',
      main: [
        { hue: 'magenta', spine: 'Summary', type: 'para', text: list.length
          ? list.length + (list.length === 1 ? ' sermon' : ' sermons') + ' logged in ' + NAMES[mi] + (serNames.length ? ', from ' + serNames.join(' and ') + '.' : '.')
          : 'No sermon notes were recorded in ' + NAMES[mi] + '.' },
        { hue: 'magenta', spine: 'Sermons', type: 'sermons', month: key }
      ],
      side: [
        { hue: 'violet', spine: 'Sundays', type: 'kv', items: suns.map(function (d) {
          var s = byDate[iso(d)];
          return [short(d), s ? s.title : (NOTES[iso(d)] || 'No notes'), s ? { tag: s.series === 'Fruit of the Spirit' ? 'Fruit' : s.series === 'Guest speaker' ? 'Guest' : s.series.split(' ')[0] } : {}];
        }) }
      ]
    });
  }
  var segs = Object.keys(series).map(function (k) { return [k, SERIES_HUE[k] || 'slate', series[k]]; });
  var pct = totalSundays ? Math.round(S.length / totalSundays * 100) : 0;

  window.RECAP = {
    meta: { label: 'CBC Sermons ' + year, short: 'Sermons', mIdx: lastDate.getMonth(), year: year, daysInMonth: 31, titleSuffix: ' · JD Meyers', prev: null, next: null },
    defaultDomain: MON[lastDate.getMonth()],
    entities: { 'Calvary Baptist': 'church', 'CBC': 'church' },
    header: {
      meta: [['Church', 'Calvary Baptist'], ['Pastor', 'Brad'], ['Through', short(lastDate)]],
      stats: [['Sermons', String(S.length)], ['Series', String(segs.length)], ['Months', String(months.filter(function (m) { return m.count; }).length)]],
      ring: { pct: pct, text: String(pct), cap: 'Logged', sub: S.length + ' of ' + totalSundays + ' Sundays' },
      mix: { centre: String(S.length), segs: segs }
    },
    domains: months
  };
})();
