/* =====================================================================
   Glass Ledger renderer: turns window.RECAP (data/2026-MM.js) into the page.
   Every month uses this same file, so every month looks and behaves the same.
   Nothing here is month-specific; edit the data file, not this one.
   ===================================================================== */
(function () {
  'use strict';
  // Only a Council Desk launch enables the return control. No access token leaves the app.
  var councilVisit=false;
  try { if(new URLSearchParams(location.search).get('from')==='council')sessionStorage.setItem('council-recap-visit','1');councilVisit=sessionStorage.getItem('council-recap-visit')==='1'; } catch(e) {councilVisit=new URLSearchParams(location.search).get('from')==='council';}
  if(councilVisit){
    var returnBar=document.createElement('div');returnBar.className='council-return';
    var returnButton=document.createElement('button');returnButton.type='button';returnButton.textContent='← Back to Council Desk';
    var returnStatus=document.createElement('span');returnStatus.setAttribute('role','status');
    returnButton.addEventListener('click',function(){if(window.opener&&!window.opener.closed){window.opener.focus();window.close();returnStatus.textContent='Council Desk is in your original tab.';}else{returnStatus.textContent='Open Council Desk from your original tab or invitation email.';}});
    returnBar.appendChild(returnButton);returnBar.appendChild(returnStatus);document.body.appendChild(returnBar);
  }
  var R = window.RECAP;
  var root = document.documentElement;
  var ns = 'http://www.w3.org/2000/svg';
  var TX_LIMIT = 25;

  var RM = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  /* ---------- theme: dark by default, remembered per browser ---------- */
  function curTheme() { return root.dataset.theme || 'dark'; }
  try { root.dataset.theme = localStorage.getItem('gl-theme') || 'dark'; } catch (e) { root.dataset.theme = 'dark'; }

  if (!R) { document.body.textContent = 'Recap data failed to load.'; return; }

  /* ---------- helpers ---------- */
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function money(n, opt) {
    opt = opt || {};
    var s = Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: opt.whole ? 0 : 2, maximumFractionDigits: opt.whole ? 0 : 2 });
    var sign = n < 0 ? '−' : (opt.plus && n > 0 ? '+' : '');
    return sign + '$' + s;
  }
  var ICON = {
    place: '<svg viewBox="0 0 12 12"><path d="M6 10.8S2.6 7.4 2.6 4.9a3.4 3.4 0 0 1 6.8 0C9.4 7.4 6 10.8 6 10.8z"/><circle cx="6" cy="4.9" r="1.2"/></svg>',
    school: '<svg viewBox="0 0 12 12"><path d="M.9 4.6 6 2.2l5.1 2.4L6 7z"/><path d="M3.1 5.7v2.4c1.6 1.3 4.2 1.3 5.8 0V5.7"/></svg>',
    church: '<svg viewBox="0 0 12 12"><path d="M6 1v3M4.6 2.4h2.8M2.6 11V6.4L6 4.4l3.4 2V11zM5 11V8.6h2V11"/></svg>',
    group: '<svg viewBox="0 0 12 12"><circle cx="4" cy="4.2" r="1.6"/><circle cx="8.3" cy="4.6" r="1.3"/><path d="M1.4 10c.3-2 1.4-3 2.6-3s2.3 1 2.6 3M6.9 9.6c.2-1.5 1-2.3 1.9-2.3s1.6.8 1.8 2.3"/></svg>',
    org: '<svg viewBox="0 0 12 12"><rect x="1.4" y="3.9" width="9.2" height="6.3" rx="1.2"/><path d="M4.4 3.9V2.6h3.2v1.3M1.4 6.6h9.2"/></svg>'
  };
  var ENT_HUE = { place: 'sky', school: 'emerald', church: 'magenta', group: 'orange', org: 'violet' };

  /* entity pills: only names the data defines; longest first, whole words */
  var entRe = null, entMap = {};
  (function () {
    var names = Object.keys(R.entities || {});
    if (!names.length) return;
    names.sort(function (a, b) { return b.length - a.length; });
    names.forEach(function (n) { entMap[n.toLowerCase()] = R.entities[n]; });
    entRe = new RegExp('\\b(' + names.map(function (n) { return esc(n).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }).join('|') + ')\\b', 'gi');
  })();
  function rich(s, pills) {
    var out = esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    if (pills && entRe) {
      out = out.replace(entRe, function (m) {
        var t = entMap[m.toLowerCase().replace(/&amp;/g, '&')] || entMap[m.toLowerCase()];
        if (!t) return m;
        return '<span class="ent ' + ENT_HUE[t] + '">' + ICON[t] + m + '</span>';
      });
    }
    return out;
  }
  function threadHue(text) {
    var ST = window.STORY; if (!ST || !text) return '';
    for (var i = 0; i < ST.rules.length; i++) if (new RegExp(ST.rules[i][0], 'i').test(text)) return ST.threads[ST.rules[i][1]].hue;
    return '';
  }
  var SERIES_HUE = { 'Acts': 'sky', 'Standalone': 'teal', 'Trust series': 'green', 'Guest speaker': 'amber', 'Conviction': 'orange', 'Fruit of the Spirit': 'magenta' };
  function spineMin(label) { return Math.max(0, String(label).length * 8.6 + 26); }

  /* ---------- chart builders ---------- */
  function ringSVG(pct, txt, size) {
    size = size || 54; var r = size / 2 - 5, c = 2 * Math.PI * r, p = Math.max(0, Math.min(100, pct)) / 100;
    return '<svg width="' + size + '" height="' + size + '" viewBox="0 0 ' + size + ' ' + size + '" role="img" aria-label="' + esc(txt) + '">' +
      '<circle cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" fill="none" stroke="var(--track)" stroke-width="6"/>' +
      (p > 0 ? '<circle cx="' + size / 2 + '" cy="' + size / 2 + '" r="' + r + '" fill="none" stroke="var(--brand)" stroke-width="6" stroke-linecap="round" stroke-dasharray="' + (c * p).toFixed(2) + ' ' + c.toFixed(2) + '" transform="rotate(-90 ' + size / 2 + ' ' + size / 2 + ')"/>' : '') +
      '<text x="' + size / 2 + '" y="' + (size / 2 + 5) + '" text-anchor="middle" font-family="Space Grotesk,sans-serif" font-size="14" font-weight="700" fill="currentColor">' + esc(txt) + '</text></svg>';
  }
  function segRingSVG(segs, centre) {
    var r = 22, C = 2 * Math.PI * r, tot = 0, off = 0, g = '';
    segs.forEach(function (s) { tot += s[2]; });
    segs.forEach(function (s) {
      if (!s[2] || !tot) return;
      var L = s[2] / tot * C, gap = segs.length > 1 ? 2 : 0;
      g += '<circle class="' + s[1] + '" cx="27" cy="27" r="22" style="stroke:rgba(var(--c),.9)" stroke-dasharray="' + Math.max(0.5, L - gap).toFixed(2) + ' ' + (C - L + gap).toFixed(2) + '" stroke-dashoffset="' + (-off).toFixed(2) + '"/>';
      off += L;
    });
    return '<svg width="54" height="54" viewBox="0 0 54 54" role="img" aria-label="Mix"><g transform="rotate(-90 27 27)" fill="none" stroke-width="6">' + g + '</g>' +
      '<text x="27" y="31" text-anchor="middle" font-family="Space Grotesk,sans-serif" font-size="11" font-weight="700" fill="currentColor">' + esc(centre) + '</text></svg>';
  }
  function sparkSVG(b) {
    var d = b.values, W = 300, H = 64, pad = 3;
    var lo = Math.min.apply(null, d.concat(b.floor != null ? [b.floor] : [])), hi = Math.max.apply(null, d.concat(b.ceil != null ? [b.ceil] : []));
    if (b.grid != null) { lo = Math.min(lo, b.grid); hi = Math.max(hi, b.grid); }
    if (hi === lo) hi = lo + 1;
    var x = function (i) { return pad + i * (W - 2 * pad) / Math.max(1, d.length - 1); };
    var y = function (v) { return H - 6 - (v - lo) / (hi - lo) * (H - 14); };
    var pts = d.map(function (v, i) { return x(i).toFixed(1) + ',' + y(v).toFixed(1); }).join(' ');
    var base = y(b.grid != null ? b.grid : lo);
    var s = '<svg class="spark" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" role="img" aria-label="' + esc(b.label || 'trend') + '">';
    if (b.grid != null) s += '<line class="gd" x1="0" x2="' + W + '" y1="' + y(b.grid).toFixed(1) + '" y2="' + y(b.grid).toFixed(1) + '"/>';
    s += '<polygon class="ar" points="' + x(0).toFixed(1) + ',' + base.toFixed(1) + ' ' + pts + ' ' + x(d.length - 1).toFixed(1) + ',' + base.toFixed(1) + '"/>';
    s += '<polyline class="ln" points="' + pts + '"/></svg>';
    return s;
  }

  /* ---------- block renderers ---------- */
  var BLOCK = {
    sub: function (b) { return '<div class="sub"><span>' + esc(b.text) + '</span>' + (b.right ? '<span>' + esc(b.right) + '</span>' : '') + '</div>'; },
    note: function (b) { return '<p class="note">' + rich(b.text) + '</p>'; },
    para: function (b) { return [].concat(b.text).map(function (t) { return '<p class="fill para">' + rich(t, true) + '</p>'; }).join(''); },
    list: function (b) { return '<ul class="fill list">' + b.items.map(function (t) { return '<li>' + rich(t, true) + '</li>'; }).join('') + '</ul>'; },
    kv: function (b) {
      return '<div class="kv">' + b.items.map(function (it) {
        var o = it[2] || {};
        return '<div class="k">' + esc(it[0]) + '</div><div class="v fill' + (o.big ? ' big' : '') + '">' + (o.tag ? '<span class="tag">' + esc(o.tag) + '</span>' : '') + rich(it[1]) + '</div>';
      }).join('') + '</div>';
    },
    rows: function (b) {
      return '<div class="rows">' + b.items.map(function (it) {
        if (it.href) return '<a class="fill row link' + (it.hue ? ' ' + it.hue : '') + '" href="' + esc(it.href) + '">' + (it.when ? '<span class="when">' + esc(it.when) + '</span>' : '') + rich(it.text) + '</a>';
        var hue = it.hue || (b.plain ? '' : threadHue(it.text));
        return '<div class="fill row' + (hue ? ' ' + hue : '') + '">' + (it.when ? '<span class="when">' + esc(it.when) + '</span>' : '') + rich(it.text, true) + (it.src ? ' <span class="src">(' + esc(it.src) + ')</span>' : '') + '</div>';
      }).join('') + '</div>';
    },
    meter: function (b) {
      var max = b.max || Math.max.apply(null, b.rows.map(function (r) { return Math.abs(r[1]); })) || 1;
      return '<div class="meter">' + b.rows.map(function (r) {
        var w = Math.min(100, Math.abs(r[1]) / max * 100);
        var mark = r[3] != null ? '<u style="left:calc(' + Math.min(100, r[3] / max * 100).toFixed(1) + '% - 1px)"></u>' : '';
        return '<div class="k" title="' + esc(r[0]) + '">' + esc(r[0]) + '</div><div class="hbar"><i style="width:' + w.toFixed(1) + '%"></i>' + mark + '</div><b>' + esc(r[2] != null ? r[2] : r[1]) + '</b>';
      }).join('') + '</div>';
    },
    seg: function (b) {
      return '<div class="meter">' + b.rows.map(function (r) {
        var n = r[2] || 5, s = '';
        for (var i = 1; i <= n; i++) s += '<i' + (i <= r[1] ? ' class="on"' : '') + '></i>';
        return '<div class="k">' + esc(r[0]) + '</div><div class="seg" style="--n:' + n + '">' + s + '</div><b>' + esc(r[3] || (r[1] + '/' + n)) + '</b>';
      }).join('') + '</div>';
    },
    spark: function (b) {
      return sparkSVG(b) + (b.axis ? '<div class="axis">' + b.axis.map(function (a) { return '<span>' + esc(a) + '</span>'; }).join('') + '</div>' : '');
    },
    cols: function (b) {
      var max = 1;
      b.cols.forEach(function (c) { max = Math.max(max, c[1], c[2] || 0); });
      return '<div class="cols">' + b.cols.map(function (c) {
        return '<div class="c" title="' + esc(c[0] + ': ' + money(c[1]) + (c[2] != null ? ' in, ' + money(c[2]) + ' out' : '')) + '"><div class="pair"><i class="a" style="height:' + (c[1] / max * 100).toFixed(1) + '%"></i>' +
          (c[2] != null ? '<i class="b" style="height:' + (c[2] / max * 100).toFixed(1) + '%"></i>' : '') + '</div><small>' + esc(c[0]) + '</small></div>';
      }).join('') + '</div>' + (b.keys ? '<div class="key"><span><i style="background:rgba(var(--h-green),.75)"></i>' + esc(b.keys[0]) + '</span><span><i style="background:rgba(var(--h-red),.6)"></i>' + esc(b.keys[1]) + '</span></div>' : '');
    },
    cal: function (b, id) {
      var m = R.meta, first = new Date(m.year, m.mIdx, 1).getDay(), h = '';
      var ses = b.sessions || {};
      ['S', 'M', 'T', 'W', 'T', 'F', 'S'].forEach(function (d) { h += '<div class="h">' + d + '</div>'; });
      for (var i = 0; i < first; i++) h += '<div class="dy x"></div>';
      for (var d = 1; d <= m.daysInMonth; d++) {
        var e = b.days[d], ev = (b.events || []).indexOf(d) > -1;
        var tg = ses[d] ? 'button type="button" data-day="' + d + '"' : 'div';
        h += '<' + tg + ' class="dy' + (e ? ' on ' + e[1] : '') + (ev ? ' ev' : '') + '" title="' + esc(m.short + ' ' + d + (e ? ': ' + e[0] : '') + (ev && b.eventLabel ? ' (' + b.eventLabel + ')' : '')) + '"><b>' + d + '</b>' + (e ? '<span>' + esc(e[0]) + '</span>' : '') + '</' + tg.split(' ')[0] + '>';
      }
      var days = Object.keys(ses).map(Number).sort(function (a, c) { return a - c; });
      var panel = days.length ? '<div class="sess fill" id="' + id + '" data-cal="' + esc(JSON.stringify(ses)) + '" data-def="' + (b.defaultDay || days[days.length - 1]) + '"></div>' : '';
      return '<div class="cal" data-for="' + id + '">' + h + '</div>' + panel + (b.legend ? '<div class="key">' + b.legend.map(function (l) { return '<span class="' + l[1] + '"><i style="background:rgba(var(--c),.6)"></i>' + esc(l[0]) + '</span>'; }).join('') + '</div>' : '');
    },
    tx: function (b, id) {
      var kinds = [['all', 'All'], ['in', 'Money in'], ['out', 'Money out'], ['mv', 'Moved']];
      var counts = { all: b.items.length, in: 0, out: 0, mv: 0 };
      b.items.forEach(function (t) { counts[t.kind]++; });
      return '<div class="filters" data-tx="' + id + '">' + kinds.map(function (k, i) {
        return '<button type="button" class="chip sm" data-k="' + k[0] + '" aria-pressed="' + (i === 0) + '">' + k[1] + ' <span class="n">' + counts[k[0]] + '</span></button>';
      }).join('') + '<span class="sp"></span><button type="button" class="chip sm" data-sort="date" aria-pressed="true">By date</button><button type="button" class="chip sm" data-sort="amt" aria-pressed="false">By amount</button></div><div class="tx" id="' + id + '">' + b.items.map(function (t, i) {
        return '<div class="fill t" data-k="' + t.kind + '" data-i="' + i + '" data-a="' + Math.abs(t.amt) + '"><span class="d">' + esc(t.date) + '</span><span class="l">' + esc(t.label) + (t.sub ? '<small>' + esc(t.sub) + '</small>' : '') + '</span><span class="a ' + t.kind + '">' + (t.kind === 'in' ? '+' : t.kind === 'out' ? '−' : '') + money(Math.abs(t.amt)).replace('$', '$') + '</span></div>';
      }).join('') + '</div>' + (b.items.length > TX_LIMIT ? '<button type="button" class="chip sm more" data-more="' + id + '">Show all</button>' : '');
    },
    /* expandable categories (from June/July): tap a row to see its line items */
    cats: function (b) {
      var max = 0, tot = 0;
      b.rows.forEach(function (r) { max = Math.max(max, Math.abs(r.amt)); tot += r.amt; });
      return '<div class="cats">' + b.rows.map(function (r) {
        var pct = tot ? r.amt / tot * 100 : 0;
        return '<details class="cat ' + (r.hue || 'slate') + '"><summary><i class="dt"></i><span class="nm">' + esc(r.name) + '</span><span class="ct">' + r.items.length + '</span><span class="pc">' + pct.toFixed(1) + '%</span><b>' + money(r.amt) + '</b><span class="chev" aria-hidden="true"></span>' +
          '<span class="hbar"><i style="width:' + (max ? Math.abs(r.amt) / max * 100 : 0).toFixed(1) + '%"></i></span></summary><div class="tx">' +
          r.items.map(function (t) {
            return '<div class="fill t"><span class="d">' + esc(t.date) + '</span><span class="l">' + esc(t.label) + (t.sub ? '<small>' + esc(t.sub) + '</small>' : '') + '</span><span class="a ' + (t.amt > 0 ? 'in' : '') + '">' + (t.amt > 0 ? '+' : '\u2212') + money(Math.abs(t.amt)) + '</span></div>';
          }).join('') + '</div></details>';
      }).join('') + '</div>';
    },
    /* twelve-month bars from data/2026-year.js; current month highlighted, each month links to its page */
    year: function (b) {
      var Y = window.YEAR; if (!Y || !Y[b.metric]) return '';
      var v = Y[b.metric], lo = 0, hi = 0;
      v.forEach(function (x) { if (x != null) { lo = Math.min(lo, x); hi = Math.max(hi, x); } });
      if (hi === lo) hi = lo + 1;
      var span = hi - lo, zero = (hi / span * 100);
      function fmt(x) { return b.fmt === 'money' ? money(x, { whole: true }) : b.fmt === 'k' ? Math.round(x / 1000) + 'k' : String(x); }
      return '<div class="yr">' + v.map(function (x, i) {
        var cur = i === R.meta.mIdx, f = Y.files && Y.files[i], tag = f && !cur ? 'a href="' + esc(f) + '"' : 'div';
        var bar = '';
        if (x != null) {
          var hgt = Math.abs(x) / span * 100;
          bar = '<i class="' + (x < 0 ? 'neg' : '') + '" style="' + (x < 0 ? 'top:' + zero.toFixed(1) : 'bottom:' + (100 - zero).toFixed(1)) + '%;height:' + Math.max(1.5, hgt).toFixed(1) + '%"></i>';
        }
        return '<' + tag + ' class="ym' + (cur ? ' cur' : '') + (x == null ? ' na' : '') + '" title="' + esc(Y.months[i] + (x != null ? ': ' + fmt(x) : '')) + '"><small>' + (x != null && (cur || b.showAll) ? esc(fmt(x)) : '&nbsp;') + '</small><span class="yb"><u style="top:' + zero.toFixed(1) + '%"></u>' + bar + '</span><em>' + esc(Y.months[i].charAt(0)) + '</em></' + tag.split(' ')[0] + '>';
      }).join('') + '</div>';
    },
    goal: function (b) {
      var pct = Math.min(100, b.value / b.target * 100);
      return '<div class="goal"><div><b class="num">' + money(b.value) + '</b><span>' + (b.of || 'of') + ' ' + money(b.target, { whole: true }) + '</span></div><span class="pct">' + (b.value / b.target * 100).toFixed(0) + '%</span></div>' +
        '<div class="hbar tall"><i style="width:' + pct.toFixed(1) + '%"></i></div>' + (b.note ? '<p class="note">' + rich(b.note) + '</p>' : '');
    },
    /* sermons come from data/sermons-2026.js, the one shared source; b.month = 'YYYY-MM' */
    sermons: function (b) {
      var list = (window.SERMONS || []).filter(function (x) { return x.date.slice(0, 7) === b.month; });
      if (!list.length) return '<p class="fill para">No sermon notes recorded for this month.</p>';
      return '<div class="cards one">' + list.map(function (x) {
        var d = new Date(x.date + 'T12:00:00');
        var box = [d.toLocaleDateString('en-US', { weekday: 'short' }).toUpperCase(), d.getDate(), d.toLocaleDateString('en-US', { month: 'short' }).toUpperCase()];
        var spine = x.themes && x.themes[0] ? x.themes[0] : x.series;
        return '<article class="card ' + (SERIES_HUE[x.series] || 'magenta') + '" style="min-height:' + spineMin(spine) + 'px"><div class="spine"><span>' + esc(spine) + '</span></div><div class="body">' +
          '<div class="date fill"><small>' + box[0] + '</small><b>' + box[1] + '</b><small>' + box[2] + '</small></div>' +
          '<h3>' + esc(x.title) + '</h3><p>' + esc(x.passage) + ' \u00b7 ' + esc(x.series) + '</p>' +
          (x.overview ? '<p class="ov">' + rich(x.overview) + '</p>' : '<span></span>') +
          (x.points && x.points.length ? '<ul class="pts">' + x.points.map(function (p) { return '<li>' + rich(p) + '</li>'; }).join('') + '</ul>' : '') +
          (x.application ? '<p class="app fill">' + rich(x.application) + '</p>' : '') +
          (x.commentary ? '<p class="cm">' + rich(x.commentary) + '</p>' : '') +
          (x.themes ? '<div class="th">' + x.themes.map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('') + '</div>' : '') +
          '</div></article>';
      }).join('') + '</div>';
    },
    /* year swimlanes from data/2026-story.js; current month column highlighted */
    lanes: function (b) {
      var ST = window.STORY; if (!ST) return '';
      var cur = b.month != null ? b.month : R.meta.mIdx;
      var MO = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      var grid = MO.map(function (x, i) { return '<b class="ln-grid" style="left:' + (i / 12 * 100).toFixed(3) + '%"></b>'; }).join('');
      var head = '<div class="ln-row ln-head"><span class="ln-k"></span><div class="ln-track">' + MO.map(function (x, i) {
        return '<i class="' + (i === cur ? 'cur' : '') + '" style="left:' + ((i + .5) / 12 * 100).toFixed(3) + '%">' + x + '</i>'; }).join('') + '</div></div>';
      function pos(at) { return Math.max(0, Math.min(100, (at - 1) / 12 * 100)); }
      var rows = ST.lanes.map(function (ln) {
        var th = ST.threads[ln.t], bars = '', labs = [];
        ln.items.forEach(function (it) {
          var t2 = ST.threads[it.t || ln.t];
          if (it.from != null) {
            var l = pos(it.from), w = pos(it.to) - l;
            bars += '<span class="ln-span ' + t2.hue + '" style="left:' + l.toFixed(2) + '%;width:' + w.toFixed(2) + '%" title="' + esc(it.label) + '"><em>' + esc(it.label) + '</em></span>';
            labs.push({ at: l + w / 2, label: it.label, span: true });
          } else {
            bars += '<span class="ln-dot ' + t2.hue + ' ' + (it.kind || '') + '" style="left:' + pos(it.at).toFixed(2) + '%" title="' + esc(it.label) + '"></span>';
            labs.push({ at: pos(it.at), label: it.label });
          }
        });
        var marks = labs.map(function (lb) {
          var a = lb.at < 5 ? 'l' : lb.at > 95 ? 'r' : 'c';
          return '<span class="ln-lab ' + a + (lb.span ? ' alt' : '') + '" style="left:' + lb.at.toFixed(2) + '%">' + esc(lb.label) + '</span>';
        }).join('');
        return '<div class="ln-row ' + th.hue + '"><span class="ln-k">' + esc(ln.title || th.label) + '</span><div class="ln-track">' + grid +
          '<b class="ln-cur" style="left:' + (cur / 12 * 100).toFixed(3) + '%;width:' + (100 / 12).toFixed(3) + '%"></b>' + bars + '<div class="ln-labs">' + marks + '</div></div></div>';
      }).join('');
      return '<div class="lanes-wrap"><div class="lanes">' + head + rows + '</div></div>';
    },
    /* training trends from data/2026-trends.js: is it going up, and in what way */
    trends: function () {
      var T = window.TRENDS, key = R.meta.year + '-' + ('0' + (R.meta.mIdx + 1)).slice(-2), i = T ? T.months.indexOf(key) : -1;
      if (i < 0) return '';
      var MO = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      var prevName = i ? MO[i - 1] : '';
      function upto(a) { return a.slice(0, i + 1); }
      function fit(v) { /* least-squares line through the non-empty points */
        var p = []; v.forEach(function (y, x) { if (y != null) p.push([x, y]); });
        if (p.length < 2) return null;
        var n = p.length, mx = 0, my = 0; p.forEach(function (q) { mx += q[0] / n; my += q[1] / n; });
        var sxx = 0, sxy = 0; p.forEach(function (q) { sxx += (q[0] - mx) * (q[0] - mx); sxy += (q[0] - mx) * (q[1] - my); });
        var b = sxx ? sxy / sxx : 0; return { b: b, a: my - b * mx };
      }
      function line(v, o) { /* small line chart with its trend line; o.inv = lower is better */
        o = o || {}; var W = 100, Hh = 36, pts = v.map(function (y, x) { return y == null ? null : [x, y]; }).filter(Boolean);
        if (!pts.length) return '';
        var ys = pts.map(function (q) { return q[1]; }), lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
        if (o.base != null) { lo = Math.min(lo, o.base); hi = Math.max(hi, o.base); }
        var pad = (hi - lo) * 0.15 || 1; lo -= pad; hi += pad;
        var n = Math.max(2, v.length), X = function (x) { return (x / (n - 1) * W).toFixed(2); }, Y = function (y) { return (Hh - (y - lo) / (hi - lo) * Hh).toFixed(2); };
        var d = pts.map(function (q, k) { return (k ? 'L' : 'M') + X(q[0]) + ' ' + Y(q[1]); }).join(' ');
        var f = fit(v), tl = f ? '<path class="tl" d="M' + X(0) + ' ' + Y(f.a) + ' L' + X(n - 1) + ' ' + Y(f.a + f.b * (n - 1)) + '"/>' : '';
        var bl = o.base != null ? '<path class="bl" d="M0 ' + Y(o.base) + ' L' + W + ' ' + Y(o.base) + '"/>' : '';
        var last = pts[pts.length - 1];
        return '<svg class="tline" viewBox="0 0 ' + W + ' ' + Hh + '" preserveAspectRatio="none" aria-hidden="true">' + bl + tl + '<path class="ln" d="' + d + '"/></svg>' +
          '<i class="tdot" style="left:' + X(last[0]) + '%;top:' + (Y(last[1]) / Hh * 100).toFixed(1) + '%"></i>';
      }
      function sgn(x, fmt, inv) { if (x == null || isNaN(x)) return '<span class="td">no data</span>'; var good = inv ? x < 0 : x > 0, flat = Math.abs(x) < 1e-9;
        return '<span class="td ' + (flat ? '' : good ? 'gup' : 'gdn') + '">' + (flat ? '±' : x > 0 ? '+' : '−') + fmt(Math.abs(x)) + '</span>'; }
      function mmss(t) { t = Math.round(t); return Math.floor(t / 60) + ':' + ('0' + t % 60).slice(-2); }
      function lastBefore(a) { for (var k = i - 1; k >= 0; k--) if (a[k] != null) return a[k]; return null; }
      function one(x) { return (Math.round(x * 10) / 10).toString(); }

      var idx = upto(T.index), now = idx[i], pv = lastBefore(T.index), f = fit(idx);
      var ov = T.overload[i], tot = ov[0] + ov[1] + ov[2], rate = tot ? Math.round((ov[0] + ov[1]) / tot * 100) : null;
      var rates = upto(T.overload).map(function (o) { var t = o[0] + o[1] + o[2]; return t ? Math.round((o[0] + o[1]) / t * 100) : null; });
      var eq = upto(T.run.eq2), eqNow = eq[i], eqBest = Math.min.apply(null, eq.filter(function (x) { return x; }).concat([1e9]));
      var miles = upto(T.run.miles);

      /* the answer, in one line */
      var dir = f ? f.b : 0, verdict = dir > 0.5 ? 'Yes, getting stronger' : dir < -0.5 ? 'Strength is slipping' : 'Holding steady';
      var lead = '<div class="tv"><b>' + verdict + '.</b> Strength index ' + one(now) + ' (Jan = 100), trending ' + (dir >= 0 ? '+' : '−') + one(Math.abs(dir)) + ' a month' +
        (rate != null ? '. ' + rate + '% of sessions matched or beat the last one' : '') +
        (eqNow ? '. Best 2-mile equivalent ' + mmss(eqNow) + (eqNow <= eqBest ? ', the best of the year' : ' (year best ' + mmss(eqBest) + ')') : '') + '.</div>';

      function tile(lbl, val, delta, chart, hue, note) {
        return '<div class="tt ' + hue + '"><span class="lbl">' + lbl + '</span><b>' + val + '</b><div class="tdl">' + delta + (note ? ' <small>' + note + '</small>' : '') + '</div><div class="tc">' + chart + '</div></div>';
      }
      var tiles = '<div class="tts">' +
        tile('Strength index', one(now), sgn(pv != null ? now - pv : null, one) + ' <small>vs ' + prevName + '</small> ' + sgn(now - 100, one) + ' <small>vs Jan</small>', line(idx, { base: 100 }), 'violet') +
        tile('Beat last session', rate != null ? rate + '%' : 'n/a', '<span class="td">' + ov[0] + ' up · ' + ov[1] + ' same · ' + ov[2] + ' down</span>', line(rates, { base: 50 }), 'green') +
        tile('2-mile equivalent', eqNow ? mmss(eqNow) : 'no run', sgn(eqNow && lastBefore(T.run.eq2) ? eqNow - lastBefore(T.run.eq2) : null, mmss, true) + ' <small>vs last run month</small>', line(eq, { inv: true, base: 950 }), 'sky', 'goal 15:50') +
        tile('Miles run', one(miles[i]), sgn(i ? miles[i] - miles[i - 1] : null, one) + ' <small>vs ' + prevName + '</small>', line(miles), 'teal') +
        '</div>';

      /* by muscle group: one small chart each, ranked by trend */
      var cats = Object.keys(T.byCat).map(function (c) { var v = upto(T.byCat[c]), ff = fit(v); return { c: c, v: v, b: ff ? ff.b : 0, now: v[i] }; })
        .sort(function (a, b) { return b.b - a.b; });
      var grid = '<div class="tcats">' + cats.map(function (c) {
        var tag = c.b > 0.5 ? 'Rising' : c.b < -0.5 ? 'Falling' : 'Flat';
        return '<div class="tcat ' + (c.b > 0.5 ? 'rise' : c.b < -0.5 ? 'fall' : 'flat') + '"><div class="tch"><span>' + esc(c.c) + '</span><em>' + tag + '</em></div><b>' + (c.now != null ? one(c.now) : '–') + '</b>' +
          '<small>' + (c.b >= 0 ? '+' : '−') + one(Math.abs(c.b)) + '/mo</small><div class="tc">' + line(c.v, { base: 100 }) + '</div></div>';
      }).join('') + '</div>';

      /* every main lift: best set, estimated max, change, trend; tap for the detail */
      var rows = T.lifts[i].map(function (l) {
        var dv = l.prev != null ? l.e1 - l.prev : null, dj = l.e1 - l.first;
        return '<details class="tl-r"><summary><span class="tl-n">' + esc(l.ex) + (l.pr ? ' <em class="pr">PR</em>' : '') + '<small>' + esc(l.cat) + ' · best set ' + esc(l.set) + '</small></span>' +
          '<span class="tl-e"><b>' + l.e1 + '</b><small>est. max</small></span>' + sgn(dv, function (x) { return Math.round(x) + ''; }) + sgn(dj, function (x) { return Math.round(x) + ''; }) +
          '<span class="tl-c">' + line(l.hist) + '</span><i class="chev"></i></summary>' +
          '<div class="tl-d"><span><b>' + l.maxw + ' lb</b>max weight</span><span><b>' + l.maxr + '</b>max reps</span><span><b>' + l.bestvol.toLocaleString('en-US') + ' lb</b>best set volume</span>' +
          '<span><b>' + l.vol.toLocaleString('en-US') + ' lb</b>month volume, ' + l.sets + ' sets</span><span><b>' + (l.slope >= 0 ? '+' : '−') + Math.abs(l.slope) + ' lb</b>trend per month</span></div></details>';
      }).join('');
      var table = rows ? '<div class="tlh"><span>Lift</span><span>Est. max</span><span>vs ' + prevName + '</span><span>vs first</span><span>Trend</span><span></span></div><div class="tlist">' + rows + '</div>' : '';

      /* conditioning */
      function cond(lbl, arr, fmt, inv, unit) {
        var v = arr[i], p = lastBefore(arr), best = arr.slice(0, i + 1).filter(function (x) { return x != null; });
        best = best.length ? (inv ? Math.min.apply(null, best) : Math.max.apply(null, best)) : null;
        return '<div class="tk"><span>' + lbl + '</span><b>' + (v != null ? fmt(v) + (unit || '') : '–') + '</b>' + sgn(v != null && p != null ? v - p : null, fmt, inv) +
          '<small>' + (best != null ? 'year best ' + fmt(best) + (unit || '') : '') + '</small></div>';
      }
      var condBlock = '<div class="tks">' +
        cond('Best pace, 1 mi+', T.run.bestPace, mmss, true, '/mi') + cond('Longest run', T.run.longest, one, false, ' mi') +
        cond('Top sprint speed', T.run.sprintMph, one, false, ' mph') + cond('Plank', T.body.plank, mmss, false) +
        cond('Push-ups, one set', T.body.pushups, String, false) + cond('Sit-ups, one minute', T.body.situps, String, false) + cond('Chin-ups, one set', T.body.chinups, String, false) + '</div>';

      return lead + tiles +
        '<div class="sub"><span>By muscle group</span><span>index, Jan = 100 · dashed = trend</span></div>' + grid +
        '<div class="sub"><span>Main lifts this month</span><span>tap a lift for detail</span></div>' + table +
        '<div class="sub"><span>Running and conditioning</span><span>change vs the last month logged</span></div>' + condBlock +
        '<p class="note">Estimated max = weight × (1 + reps ÷ 30), so a heavy triple and a lighter set of ten land on one scale. The strength index chains each lift against its own last best; new lifts join after their first month. 2-mile equivalent converts any run of 1.5 miles or more with Riegel’s formula.</p>';
    },
    /* 2026 goals scorecard from data/2026-goals.js */
    goalsum: function (b) {
      var G = window.GOALS; if (!G) return '';
      var all = [].concat.apply([], G.groups.map(function (g) { return g.goals; }));
      var tracked = all.filter(function (x) { return x.status !== 'open'; });
      var ST = [['met', 'Met', 'green'], ['close', 'Close', 'amber'], ['behind', 'Behind', 'red'], ['open', 'Not tracked', 'slate']];
      var n = {}; all.forEach(function (x) { n[x.status] = (n[x.status] || 0) + 1; });
      var pMet = Math.round((n.met || 0) / tracked.length * 100), pNear = Math.round(((n.met || 0) + (n.close || 0)) / tracked.length * 100);
      var avg = Math.round(tracked.reduce(function (t, x) { return t + (x.pct || 0); }, 0) / tracked.length);
      var bar = ST.map(function (s) { return n[s[0]] ? '<i class="' + s[2] + '" style="flex:' + n[s[0]] + '" title="' + s[1] + ': ' + n[s[0]] + '"></i>' : ''; }).join('');
      var tiles = ST.map(function (s) { return '<div class="gs-t ' + s[2] + '"><b>' + (n[s[0]] || 0) + '</b><span>' + s[1] + '</span></div>'; }).join('');
      var pillars = G.groups.map(function (g) {
        var m = g.goals.filter(function (x) { return x.status === 'met'; }).length, t = g.goals.filter(function (x) { return x.status !== 'open'; }).length;
        return '<a class="gs-p ' + g.hue + '" href="#goals" data-g="' + g.id + '"><span>' + esc(g.label) + '</span><div class="hbar"><i style="width:' + (t ? m / t * 100 : 0).toFixed(1) + '%"></i></div><b>' + m + '/' + t + '</b></a>';
      }).join('');
      return '<div class="gs"><div class="gs-big"><b class="num">' + pMet + '%</b><span>of tracked goals met<br>' + (n.met || 0) + ' of ' + tracked.length + ', through ' + esc(G.through) + '</span></div>' +
        '<div class="gs-bar">' + bar + '</div><div class="gs-tiles">' + tiles + '</div>' +
        '<div class="gs-nums"><div><b>' + pNear + '%</b><span>met or within reach</span></div><div><b>' + avg + '%</b><span>average progress</span></div><div><b>' + (all.length - tracked.length) + '</b><span>not tracked yet</span></div></div>' +
        (b && b.verdict && G.verdict ? '<p class="gs-v">' + esc(G.verdict) + '</p>' : '') +
        '<div class="gs-pillars">' + pillars + '</div></div>';
    },
    goalset: function (b) {
      var G = window.GOALS; if (!G) return '';
      var g = G.groups.filter(function (x) { return x.id === b.group; })[0]; if (!g) return '';
      var LBL = { met: 'Met', close: 'Close', behind: 'Behind', open: 'Not tracked' };
      return '<span class="gl-anchor" id="g-' + g.id + '"></span>' + (g.take ? '<p class="gl-take">' + esc(g.take) + '</p>' : '') + '<div class="gl">' + g.goals.map(function (x) {
        var p = x.pct != null ? Math.max(3, Math.min(100, x.pct)) : 0;
        var nums = x.status === 'open' ? '<b class="gl-a">' + esc(x.actual) + '</b>' :
          '<div class="gl-nums"><b class="gl-a">' + esc(x.actual) + '</b>' + (x.delta ? '<span class="gl-d ' + (x.good ? 'gup' : 'gdn') + '">' + esc(x.delta) + '</span>' : '') + '</div>';
        return '<div class="gl-r ' + x.status + '"><span class="gl-s">' + LBL[x.status] + '</span><div class="gl-m"><div class="gl-g">' + esc(x.goal) + '</div>' +
          (x.status !== 'open' ? '<div class="gl-bar"><div class="hbar"><i style="width:' + p.toFixed(1) + '%"></i></div><small>' + (x.pct != null ? Math.round(x.pct) + '%' : '') + '</small></div>' : '') +
          '<div class="gl-n">' + (x.target ? 'Target ' + esc(x.target) + (x.note ? ' · ' : '') : '') + (x.note ? esc(x.note) : '') + '</div></div>' + nums + '</div>';
      }).join('') + '</div>';
    },
    checks: function () {
      var G = window.GOALS; if (!G) return '';
      var MO = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'], MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      var head = '<span></span>' + MN.map(function (x) { return '<i>' + x + '</i>'; }).join('');
      var rows = G.months.map(function (r) {
        return '<span class="ck-k ' + r.hue + '">' + esc(r.label) + '</span>' + r.vals.map(function (v, i) {
          var c = v == null ? 'ck-x' : v >= 1 ? 'ck-1' : v > 0 ? 'ck-h' : 'ck-0';
          var tip = MN[i] + ': ' + (r.tips && r.tips[i] ? r.tips[i] : v == null ? 'ahead' : v >= 1 ? 'met' : v > 0 ? 'partly' : 'missed');
          return '<em class="' + c + ' ' + r.hue + '" title="' + esc(tip) + '"></em>';
        }).join('');
      }).join('');
      return '<div class="ck-wrap"><div class="ck">' + head + rows + '</div></div><div class="key ck-key"><span><em class="ck-1 slate"></em>Met</span><span><em class="ck-h slate"></em>Partly</span><span><em class="ck-0 slate"></em>Missed</span><span><em class="ck-x slate"></em>Ahead</span></div>';
    },
    words: function (b) {
      var ST = window.STORY; if (!ST) return '';
      return '<div class="words">' + ST.words.filter(function (w) { return !b.only || b.only.indexOf(w[0]) > -1; }).map(function (w) {
        return '<div class="fill wd"><b>' + esc(w[0]) + '</b><p>' + rich(w[1]) + '</p></div>'; }).join('') + '</div>';
    },
    cards: function (b) {
      return '<div class="cards' + (b.one ? ' one' : '') + '">' + b.cards.map(function (c) {
        var tagName = c.href ? 'a' : 'article', hue = c.hue || 'slate';
        var date = c.date ? '<div class="date fill"><small>' + esc(c.date[0]) + '</small><b>' + esc(c.date[1]) + '</b><small>' + esc(c.date[2]) + '</small></div>' : '';
        return '<' + tagName + ' class="card ' + hue + '"' + (c.href ? ' href="' + esc(c.href) + '"' : '') + ' style="min-height:' + spineMin(c.spine) + 'px"><div class="spine"><span>' + esc(c.spine) + '</span></div><div class="body' + (c.date ? '' : ' nodate') + '">' +
          date + '<h3>' + esc(c.title) + '</h3>' + (c.text ? '<p>' + rich(c.text) + '</p>' : '') +
          (c.tags ? '<div>' + c.tags.map(function (t) { return '<span class="tag">' + esc(t) + '</span>'; }).join('') + '</div>' : '') +
          (c.pts ? '<ul class="pts">' + c.pts.map(function (p) { return '<li>' + rich(p) + '</li>'; }).join('') + '</ul>' : '') +
          (c.foot ? '<div class="foot"><span>' + esc(c.foot[0]) + '</span><b>' + esc(c.foot[1] || '') + '</b></div>' : '') +
          '</div></' + tagName + '>';
      }).join('') + '</div>';
    }
  };

  var uid = 0;
  function band(bd) {
    var blocks = bd.blocks || [bd];
    var bare = blocks.length === 1 && (blocks[0].type === 'cards' || blocks[0].type === 'sermons');
    var inner = blocks.map(function (b) { return BLOCK[b.type] ? BLOCK[b.type](b, 'tx' + (uid++)) : ''; }).join('');
    if (bd.wide) return '<div class="band wide ' + (bd.hue || 'slate') + '"><div class="body">' + inner + '</div></div>';
    return '<div class="band ' + (bd.hue || 'slate') + '" style="min-height:' + spineMin(bd.spine) + 'px"><div class="spine"><span>' + esc(bd.spine) + '</span></div><div class="body"' + (bare ? ' style="padding:0;background:none"' : '') + '>' + inner + '</div></div>';
  }
  function sheet(kind, label, bands) {
    if (!bands || !bands.length) return '';
    return '<section class="glass sheet ' + kind + '"><div class="phead">' + esc(label) + '<span class="rl"></span><span class="ct">' + bands.length + (bands.length === 1 ? ' section' : ' sections') + '</span></div>' + bands.map(band).join('') + '</section>';
  }

  /* ---------- page shell ---------- */
  var m = R.meta, H = R.header;
  document.title = m.label + (m.titleSuffix != null ? m.titleSuffix : ' · Monthly Recap · JD Meyers');

  var top = '<header class="glass top">' +
    '<div class="title"><div><div class="crumb"><a href="index.html">2026 Recaps</a><span>/</span><span>' + esc(m.short) + '</span></div><h1>' + esc(m.label) + '</h1>' +
    '<div class="meta">' + H.meta.map(function (p) { return '<span class="lbl">' + esc(p[0]) + '</span><b>' + esc(p[1]) + '</b>'; }).join('') + '</div></div></div>' +
    '<div class="stats">' + H.stats.map(function (s) { return '<div class="stat"><span class="lbl">' + esc(s[0]) + '</span><b class="' + (s[2] ? 'neg' : '') + '">' + esc(s[1]) + '</b></div>'; }).join('') + '</div>' +
    '<div class="ring-cell">' + ringSVG(H.ring.pct, H.ring.text) + '<div class="cap"><b>' + esc(H.ring.cap) + '</b><span>' + esc(H.ring.sub) + '</span></div></div>' +
    (H.mix && H.showMix ? '<div>' + segRingSVG(H.mix.segs, H.mix.centre) + '<ul class="legend">' + H.mix.segs.map(function (s) { return '<li class="' + s[1] + '"><i></i>' + esc(s[0]) + '</li>'; }).join('') + '</ul></div>' : '') +
    '';
  /* ---------- navigation: one bar on every page ----------
     Home (primary) | this page's sections (tabs) | previous month, Jump to any page, next month | theme.
     The bar sticks to the top while scrolling, so Home and Jump are always one tap away. */
  var here = (location.pathname.split('/').pop() || 'index.html');
  var Yr = window.YEAR, MN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var pages = [['index.html', 'Home: the year'], ['index.html#goals', '2026 goals'], ['cbc-sermons.html', 'Sermon notes']];
  var monthsMenu = Yr ? Yr.files.map(function (f, i) { return f ? '<a href="' + f + '"' + (f === here ? ' aria-current="page"' : '') + '><b>' + Yr.months[i] + '</b><span>' + MN[i] + '</span></a>' : '<span class="off"><b>' + Yr.months[i] + '</b><span>Ahead</span></span>'; }).join('') : '';
  var menu = '<details class="jump"><summary>Jump to<i></i></summary><div class="glass menu"><div class="mgrid">' + monthsMenu + '</div><div class="mlinks">' +
    pages.map(function (p) { return '<a href="' + p[0] + '">' + p[1] + '</a>'; }).join('') + '<button type="button" class="mtheme" data-theme-btn>Switch to light</button></div></div></details>';
  var isHome = here === 'index.html' || here === '';
  var home = '<a class="home" href="index.html#story"' + (isHome ? ' aria-current="page"' : '') + '><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 7.5 8 2.5l6 5V14H10V10H6v4H2z"/></svg>Home</a>';
  var nav = '<div class="navr">' +
    (m.prev ? '<a class="step" href="' + esc(m.prev[0]) + '" aria-label="Previous month: ' + esc(m.prev[1]) + '">&#8249; ' + esc(m.prev[1]) + '</a>' : '') +
    menu +
    (m.next ? '<a class="step" href="' + esc(m.next[0]) + '" aria-label="Next month: ' + esc(m.next[1]) + '">' + esc(m.next[1]) + ' &#8250;</a>' : '') +
    '<button class="toggle" id="theme" type="button" aria-label="Switch theme">LIGHT</button></div>';
  top += '</header>';

  var bar = '<nav class="glass bar" aria-label="Site">' + home + '<div class="tabs" role="tablist">' + R.domains.map(function (d) {
    return '<a class="chip ' + d.hue + '" href="#' + d.id + '" data-d="' + d.id + '"><span class="dot"></span>' + esc(d.label) + (d.count != null ? ' <span class="n">' + esc(d.count) + '</span>' : '') + '</a>';
  }).join('') + '</div>' + nav + '</nav>';

  /* ---------- hero: big numbers vs last month and the year, then one strip of every day ---------- */
  function thread(text) {
    var ST = window.STORY; if (!ST) return null;
    for (var i = 0; i < ST.rules.length; i++) if (new RegExp(ST.rules[i][0], 'i').test(text)) return ST.rules[i][1];
    return null;
  }
  function heroHTML() {
    var Y = window.YEAR, ST = window.STORY, mi = m.mIdx;
    if (!Y || !ST || R.noHero) return '';
    function avg(a) { var v = a.slice(0, mi).filter(function (x) { return x != null; }); return v.length ? v.reduce(function (p, q) { return p + q; }, 0) / v.length : null; }
    function tile(label, key, hue, fmt) {
      var v = Y[key][mi], pv = mi ? Y[key][mi - 1] : null, av = avg(Y[key]);
      if (v == null) return '';
      function d(x, ref) { if (ref == null) return ''; var diff = x - ref, up = diff >= 0; return '<span class="' + (up ? 'kup' : 'kdn') + '">' + (up ? '\u25B2 ' : '\u25BC ') + fmt(Math.abs(diff)) + '</span>'; }
      var spark = Y[key].map(function (x, i) { return x == null ? '' : '<i class="' + (i === mi ? 'cur' : '') + '" style="height:' + Math.max(4, Math.abs(x) / Math.max.apply(null, Y[key].filter(function (z) { return z != null; }).map(Math.abs)) * 100).toFixed(0) + '%' + (x < 0 ? ';opacity:.45' : '') + '"></i>'; }).join('');
      return '<div class="kpi ' + hue + '"><span class="lbl">' + label + '</span><b>' + fmt(v, true) + '</b><div class="dl">' + d(v, pv) + ' <small>vs ' + (mi ? Y.months[mi - 1] : '') + '</small> ' + d(v, av) + ' <small>vs avg</small></div><div class="ks">' + spark + '</div></div>';
    }
    var money_ = function (x, sign) { return (sign && x < 0 ? '\u2212' : '') + '$' + Math.round(Math.abs(x)).toLocaleString('en-US'); };
    var int_ = function (x) { return String(Math.round(x)); };
    var k_ = function (x) { return Math.round(x / 1000) + 'k'; };
    var tiles = tile('Net saved', 'net', 'teal', money_) + tile('Gym days', 'gymDays', 'violet', int_) + tile('Lifting volume, lb', 'volume', 'violet', k_) + tile('Sermons logged', 'sermons', 'magenta', int_);
    /* day strip: gym days, sermons, jobs, and every dated timeline item, each in its thread color */
    var days = {}, add = function (d, t, label) { if (!d || d > m.daysInMonth) return; (days[d] = days[d] || []).push([t, label]); };
    var ov = null, cr = null, ph = null;
    R.domains.forEach(function (x) { if (x.id === 'overview') ov = x; if (x.id === 'creative') cr = x; if (x.id === 'physical') ph = x; });
    function blocks(dm) { var out = []; (dm ? dm.main.concat(dm.side) : []).forEach(function (bd) { (bd.blocks || [bd]).forEach(function (b) { out.push(b); }); }); return out; }
    blocks(ph).forEach(function (b) { if (b.type === 'cal') Object.keys(b.days).forEach(function (d) { add(+d, 'fitness', 'Gym: ' + b.days[d][0]); }); });
    (window.SERMONS || []).forEach(function (s) { var dd = new Date(s.date + 'T12:00:00'); if (dd.getMonth() === mi && dd.getFullYear() === m.year) add(dd.getDate(), 'faith', 'Sermon: ' + s.title); });
    blocks(cr).forEach(function (b) { if (b.type === 'cards') b.cards.forEach(function (c) { if (c.date && c.date[2] === m.short.toUpperCase()) add(+c.date[1], 'jdm', c.title); }); });
    blocks(ov).forEach(function (b) { if (b.type === 'rows') b.items.forEach(function (it) {
      var mm = /^([A-Z][a-z]{2})\s+(\d{1,2})$/.exec(it.when || ''); if (!mm || mm[1] !== m.short) return;
      var t = thread(it.text); if (t && t !== 'faith' && t !== 'fitness') add(+mm[2], t, it.text);
      if (/to (\d+)/.test(it.text) && t) { var end = +/to (\d+)/.exec(it.text)[1]; for (var q = +mm[2] + 1; q <= end; q++) add(q, t, it.text); }
    }); });
    var first = new Date(m.year, mi, 1).getDay(), cells = '', used = {};
    for (var d = 1; d <= m.daysInMonth; d++) {
      var ev = days[d] || [], dow = new Date(m.year, mi, d).getDay();
      var bars = ev.map(function (e) { used[e[0]] = 1; return '<i class="' + ST.threads[e[0]].hue + '"></i>'; }).join('');
      var prev = (days[d - 1] || []).map(function (e) { return e[1]; });
      var lab = ev.filter(function (e) { return e[0] !== 'fitness' && prev.indexOf(e[1]) < 0; })[0];
      cells += '<div class="sd' + (dow === 0 || dow === 6 ? ' we' : '') + '" title="' + esc(m.short + ' ' + d + (ev.length ? ': ' + ev.map(function (e) { return e[1]; }).join(' \u00b7 ') : '')) + '"><b>' + d + '</b><span class="sb">' + bars + '</span>' + (lab ? '<em class="' + ST.threads[lab[0]].hue + '">' + esc(lab[1].replace(/^Sermon: /, '')) + '</em>' : '') + '</div>';
    }
    var legend = Object.keys(ST.threads).filter(function (k) { return used[k]; }).map(function (k) { return '<span class="' + ST.threads[k].hue + '"><i></i>' + esc(ST.threads[k].label) + '</span>'; }).join('');
    return '<section class="hero"><div class="kpis">' + tiles + '</div><div class="glass strip-wrap"><div class="sub"><span>' + esc(R.meta.label) + ', day by day</span><span>' + Object.keys(days).length + ' active days</span></div><div class="strip" style="--n:' + m.daysInMonth + '">' + cells + '</div><div class="key thr">' + legend + '</div></div>' +
      '<div class="glass strip-wrap"><div class="sub"><span>2026 so far, by thread</span><span>' + esc(m.short) + ' highlighted</span></div>' + BLOCK.lanes({}) + '</div></section>';
  }

  var wrap = document.createElement('div');
  wrap.className = 'wrap';
  wrap.innerHTML = top + bar + '<div id="hero"></div><main class="parts" id="parts"></main>' + (R.footnote ? '<p class="foot-note">' + rich(R.footnote) + '</p>' : '');
  document.body.appendChild(wrap);
  if(councilVisit)wrap.querySelector('.bar').prepend(returnBar);

  /* ---------- routing: one domain at a time, by hash ---------- */
  var parts = document.getElementById('parts');
  var sideEl = null;
  parts.addEventListener('toggle', function () { fitSide(); }, true);
  function show(id, fromClick) {
    var d = null;
    R.domains.forEach(function (x) { if (x.id === id) d = x; });
    if (!d) R.domains.forEach(function (x) { if (x.id === R.defaultDomain) d = x; });
    if (!d) d = R.domains[0];
    uid = 0;
    var mainBands = d.main;
    if (d.id === 'physical' && window.TRENDS && !R.noHero) mainBands = [{ hue: 'violet', spine: 'Trends', blocks: [{ type: 'sub', text: 'Am I making progress?', right: 'Jan to ' + m.short }, { type: 'trends' }] }].concat(d.main || []);
    parts.innerHTML = sheet('main', d.mainLabel || d.label, mainBands) + sheet('side', d.sideLabel || 'At a glance', d.side);
    var heroEl = document.getElementById('hero');
    heroEl.innerHTML = d.id === 'overview' ? heroHTML() : '';
    sideEl = parts.querySelector('.sheet.side');
    [].forEach.call(document.querySelectorAll('.bar .chip'), function (c) {
      if (c.getAttribute('data-d') === d.id) c.setAttribute('aria-current', 'page'); else c.removeAttribute('aria-current');
    });
    wireTx();
    wireCal();
    fitLanes();
    fitSide();
    if (fromClick && !RM) { [parts, heroEl].forEach(function (el) { el.classList.remove('enter'); void el.offsetWidth; el.classList.add('enter'); }); }
    var tabs = document.querySelector('.tabs'), on = tabs && tabs.querySelector('[aria-current]');
    if (on && tabs.scrollWidth > tabs.clientWidth) {
      var l = on.offsetLeft - tabs.offsetLeft, r = l + on.offsetWidth;
      if (l < tabs.scrollLeft + 8 || r > tabs.scrollLeft + tabs.clientWidth - 8) tabs.scrollTo({ left: Math.max(0, l - 24), behavior: RM ? 'auto' : 'smooth' });
    }
    if (fromClick) {
      var barEl = document.querySelector('.bar'), first = document.getElementById('hero').firstChild ? document.getElementById('hero') : parts;
      var target = window.scrollY + first.getBoundingClientRect().top - (barEl ? barEl.offsetHeight : 0) - 22;
      if (window.scrollY > target) window.scrollTo(0, Math.max(0, target));
    }
  }
  function current() { return (location.hash || '').replace('#', '') || R.defaultDomain || R.domains[0].id; }
  window.addEventListener('hashchange', function () { show(current(), true); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a && a.getAttribute('href') === location.hash) { e.preventDefault(); show(current(), true); }
  });

  /* swimlane labels: measured, so names never overlap or clip. A bar too short for its name
     shows the name underneath instead; labels stack into as many rows as they need. */
  function fitLanes() {
    [].forEach.call(document.querySelectorAll('.ln-row:not(.ln-head) .ln-track'), function (tr) {
      var tw = tr.clientWidth; if (!tw) return;
      [].forEach.call(tr.querySelectorAll('.ln-span'), function (sp, k) {
        var em = sp.querySelector('em'), alt = tr.querySelectorAll('.ln-lab.alt')[k];
        var fits = em.scrollWidth + 14 <= sp.clientWidth;
        sp.classList.toggle('short', !fits);
        if (alt) alt.style.display = fits ? 'none' : '';
      });
      var labs = [].filter.call(tr.querySelectorAll('.ln-lab'), function (l) { return l.style.display !== 'none'; });
      /* centre each label on its mark, but keep it inside the track */
      var items = labs.map(function (l) {
        if (l.dataset.at == null) l.dataset.at = parseFloat(l.style.left);
        var w = l.offsetWidth, at = l.dataset.at / 100 * tw;
        var x0 = Math.max(0, Math.min(tw - w, at - w / 2));
        l.style.left = x0 + 'px'; l.style.transform = 'none';
        return { el: l, x0: x0, x1: x0 + w };
      }).sort(function (a, b) { return a.x0 - b.x0; });
      var ends = [];
      items.forEach(function (it) {
        var r = 0; while (ends[r] != null && ends[r] > it.x0 - 8) r++;
        ends[r] = it.x1; it.el.style.top = (r * 14) + 'px';
      });
      tr.style.height = (32 + Math.max(1, ends.length) * 14 + 8) + 'px';
    });
  }

  /* side sheet sticks only when it fits in the window, so it never overlaps or clips */
  function fitSide() {
    var barEl = document.querySelector('.bar'), bh = barEl ? barEl.offsetHeight : 0;
    root.style.setProperty('--barh', bh + 'px');

  }
  var rz = false;
  window.addEventListener('resize', function () { if (!rz) { rz = true; requestAnimationFrame(function () { rz = false; fitLanes(); fitSide(); }); } }, { passive: true });

  /* training calendar: tap a day to see every exercise and set logged */
  function wireCal() {
    [].forEach.call(parts.querySelectorAll('.cal[data-for]'), function (cal) {
      var panel = document.getElementById(cal.getAttribute('data-for')); if (!panel) return;
      var ses = JSON.parse(panel.getAttribute('data-cal'));
      function pick(d) {
        [].forEach.call(cal.querySelectorAll('[data-day]'), function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-day') === String(d) ? 'true' : 'false'); });
        var date = new Date(R.meta.year, R.meta.mIdx, d);
        panel.innerHTML = '<div class="sub"><span>' + esc(date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })) + '</span><span>' + ses[d].length + ' exercises</span></div>' +
          '<div class="sx">' + ses[d].map(function (e) { return '<span class="en">' + esc(e[0]) + '</span><span class="es">' + esc(e[1]) + '</span>'; }).join('') + '</div>';
      }
      cal.addEventListener('click', function (e) { var b = e.target.closest('[data-day]'); if (b) { pick(b.getAttribute('data-day')); fitSide(); } });
      pick(panel.getAttribute('data-def'));
    });
  }

  /* long ledgers show the first TX_LIMIT rows of the active filter until "Show all" */
  function wireTx() {
    [].forEach.call(parts.querySelectorAll('.filters[data-tx]'), function (f) {
      var id = f.getAttribute('data-tx'), list = document.getElementById(id);
      var more = parts.querySelector('[data-more="' + id + '"]'), k = 'all', all = false;
      function apply() {
        var n = 0, total = 0;
        [].forEach.call(list.children, function (r) {
          var match = k === 'all' || r.getAttribute('data-k') === k;
          if (match) total++;
          var on = match && (all || n < TX_LIMIT);
          if (on) n++;
          r.style.display = on ? '' : 'none';
        });
        if (more) { more.style.display = (!all && total > TX_LIMIT) ? '' : 'none'; more.textContent = 'Show all ' + total; }
      }
      f.addEventListener('click', function (e) {
        var b = e.target.closest('button'); if (!b) return;
        if (b.hasAttribute('data-sort')) {
          var by = b.getAttribute('data-sort');
          [].forEach.call(f.querySelectorAll('[data-sort]'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
          [].slice.call(list.children).sort(function (p, q) {
            return by === 'amt' ? q.getAttribute('data-a') - p.getAttribute('data-a') : p.getAttribute('data-i') - q.getAttribute('data-i');
          }).forEach(function (r) { list.appendChild(r); });
          apply(); return;
        }
        k = b.getAttribute('data-k'); all = false;
        [].forEach.call(f.querySelectorAll('[data-k]'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        apply(); fitSide();
      });
      if (more) more.addEventListener('click', function () { all = true; apply(); fitSide(); });
      apply();
    });
  }

  /* the bar casts a soft shadow only while it is pinned over content */
  (function () {
    var barEl = document.querySelector('.bar'); if (!barEl || !('IntersectionObserver' in window)) return;
    var mark = document.createElement('div'); mark.style.cssText = 'height:1px;margin-bottom:-1px';
    barEl.parentNode.insertBefore(mark, barEl);
    new IntersectionObserver(function (en) { barEl.classList.toggle('pinned', !en[0].isIntersecting); }, { rootMargin: '-9px 0px 0px 0px' }).observe(mark);
  })();
  /* scorecard rows jump to their goal group */
  document.addEventListener('click', function (e) {
    var p = e.target.closest && e.target.closest('.gs-p[data-g]'); if (!p) return;
    e.preventDefault();
    if (current() !== 'goals') { location.hash = 'goals'; }
    setTimeout(function () {
      var el = document.getElementById('g-' + p.getAttribute('data-g')), barEl = document.querySelector('.bar');
      if (el) window.scrollTo({ top: window.scrollY + el.closest('.band').getBoundingClientRect().top - (barEl ? barEl.offsetHeight : 0) - 22, behavior: RM ? 'auto' : 'smooth' });
    }, 60);
  });
  document.addEventListener('click', function (e) {
    var j = document.querySelector('details.jump');
    if (j && j.open && (!j.contains(e.target) || e.target.closest('.menu a'))) j.open = false;
  });
  document.addEventListener('keydown', function (e) { var j = document.querySelector('details.jump'); if (e.key === 'Escape' && j) j.open = false; });

  /* ---------- theme toggle ---------- */
  var btn = document.getElementById('theme'), mbtn = document.querySelector('[data-theme-btn]');
  function label() { var d = curTheme() === 'dark'; btn.textContent = d ? 'LIGHT' : 'DARK'; if (mbtn) mbtn.textContent = d ? 'Switch to light' : 'Switch to dark'; }
  function flip() {
    root.classList.add('theming');
    root.dataset.theme = curTheme() === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('gl-theme', root.dataset.theme); } catch (e) {}
    label(); setTimeout(function () { root.classList.remove('theming'); }, 260);
  }
  btn.addEventListener('click', flip);
  if (mbtn) mbtn.addEventListener('click', flip);
  label();

  /* ---------- backdrop: blobs + contour fields, fixed behind content ---------- */
  var bg = document.createElement('div');
  bg.className = 'bg'; bg.setAttribute('aria-hidden', 'true');
  bg.innerHTML = '<div class="layer" data-depth="0.16">' +
    '<div class="blob teal" style="left:-12%;top:1%;width:50vw;height:40vw"></div>' +
    '<div class="blob amber" style="right:-14%;top:9%;width:55vw;height:40vw"></div>' +
    '<div class="blob blue" style="left:20%;top:22%;width:50vw;height:36vw"></div>' +
    '<div class="blob violet" style="right:-10%;top:40%;width:46vw;height:36vw"></div></div>' +
    '<div class="layer" data-depth="0.36" id="contours"></div>';
  document.body.insertBefore(bg, document.body.firstChild);
  var host = bg.querySelector('#contours');
  function field(x, y, size) {
    var s = document.createElementNS(ns, 'svg');
    s.setAttribute('viewBox', '-500 -500 1000 1000');
    s.style.left = x; s.style.top = y; s.style.width = size; s.style.height = size;
    for (var j = 1; j <= 16; j++) {
      var p = '', n = 120, r0 = j * 29;
      for (var i = 0; i <= n; i++) {
        var t = i / n * Math.PI * 2, r = r0 + 6 * Math.sin(4 * t + j * .35) + 4 * Math.cos(7 * t - j * .2);
        p += (i ? 'L' : 'M') + (r * Math.cos(t)).toFixed(1) + ' ' + (r * Math.sin(t)).toFixed(1);
      }
      var e = document.createElementNS(ns, 'path');
      e.setAttribute('d', p + 'Z'); if (j % 4 === 0) e.setAttribute('class', 'major');
      s.appendChild(e);
    }
    host.appendChild(s);
  }
  field('88%', '3%', '900px'); field('6%', '13%', '820px'); field('70%', '26%', '860px');
  field('15%', '40%', '900px'); field('85%', '55%', '820px'); field('30%', '72%', '880px');

  /* scroll-linked parallax: layers drift up slower than content, clamped so they never run out */
  var layers = [].slice.call(bg.querySelectorAll('.layer[data-depth]'));
  var rm = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var tick = false;
  function upd() {
    tick = false;
    var s = window.scrollY || 0, vh = window.innerHeight;
    layers.forEach(function (l) {
      if (rm.matches) { l.style.transform = ''; return; }
      var y = Math.min(s * parseFloat(l.dataset.depth), l.offsetHeight - vh);
      l.style.transform = 'translate3d(0,' + (-y).toFixed(1) + 'px,0)';
    });
  }
  window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(upd); } }, { passive: true });

  /* back to top: appears after scrolling down a screen */
  var up = document.createElement('button');
  up.type = 'button'; up.className = 'up'; up.setAttribute('aria-label', 'Back to top'); up.innerHTML = '&#8593;';
  up.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: rm.matches ? 'auto' : 'smooth' }); });
  document.body.appendChild(up);
  window.addEventListener('scroll', function () { up.classList.toggle('show', (window.scrollY || 0) > window.innerHeight); }, { passive: true });

  show(current(), false);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitLanes);
  upd();
})();

