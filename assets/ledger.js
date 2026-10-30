/* =====================================================================
   Glass Ledger renderer: turns window.RECAP (data/2026-MM.js) into the page.
   Every month uses this same file, so every month looks and behaves the same.
   Nothing here is month-specific; edit the data file, not this one.
   ===================================================================== */
(function () {
  'use strict';
  var R = window.RECAP;
  var root = document.documentElement;
  var ns = 'http://www.w3.org/2000/svg';
  var TX_LIMIT = 25;

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
        return '<div class="fill row' + (it.hue ? ' ' + it.hue : '') + '">' + (it.when ? '<span class="when">' + esc(it.when) + '</span>' : '') + rich(it.text, true) + (it.src ? ' <span class="src">(' + esc(it.src) + ')</span>' : '') + '</div>';
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
      return '<div class="goal"><div><b class="num">' + money(b.value) + '</b><span>of ' + money(b.target, { whole: true }) + '</span></div><span class="pct">' + (b.value / b.target * 100).toFixed(0) + '%</span></div>' +
        '<div class="hbar tall"><i style="width:' + pct.toFixed(1) + '%"></i></div>' + (b.note ? '<p class="note">' + rich(b.note) + '</p>' : '');
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
    var bare = blocks.length === 1 && blocks[0].type === 'cards';
    var inner = blocks.map(function (b) { return BLOCK[b.type] ? BLOCK[b.type](b, 'tx' + (uid++)) : ''; }).join('');
    return '<div class="band ' + (bd.hue || 'slate') + '" style="min-height:' + spineMin(bd.spine) + 'px"><div class="spine"><span>' + esc(bd.spine) + '</span></div><div class="body"' + (bare ? ' style="padding:0;background:none"' : '') + '>' + inner + '</div></div>';
  }
  function sheet(kind, label, bands) {
    if (!bands || !bands.length) return '';
    return '<section class="glass sheet ' + kind + '"><div class="phead">' + esc(label) + '<span class="rl"></span><span class="ct">' + bands.length + (bands.length === 1 ? ' section' : ' sections') + '</span></div>' + bands.map(band).join('') + '</section>';
  }

  /* ---------- page shell ---------- */
  var m = R.meta, H = R.header;
  document.title = m.label + ' · Monthly Recap · JD Meyers';

  var top = '<header class="glass top">' +
    '<div class="title"><div><div class="crumb"><a href="index.html">2026 Recaps</a><span>/</span><span>' + esc(m.short) + '</span></div><h1>' + esc(m.label) + '</h1>' +
    '<div class="meta">' + H.meta.map(function (p) { return '<span class="lbl">' + esc(p[0]) + '</span><b>' + esc(p[1]) + '</b>'; }).join('') + '</div></div></div>' +
    '<div class="stats">' + H.stats.map(function (s) { return '<div class="stat"><span class="lbl">' + esc(s[0]) + '</span><b class="' + (s[2] ? 'neg' : '') + '">' + esc(s[1]) + '</b></div>'; }).join('') + '</div>' +
    '<div class="ring-cell">' + ringSVG(H.ring.pct, H.ring.text) + '<div class="cap"><b>' + esc(H.ring.cap) + '</b><span>' + esc(H.ring.sub) + '</span></div></div>' +
    '<div>' + segRingSVG(H.mix.segs, H.mix.centre) + '<ul class="legend">' + H.mix.segs.map(function (s) { return '<li class="' + s[1] + '"><i></i>' + esc(s[0]) + '</li>'; }).join('') + '</ul></div>' +
    '';
  var nav = '<div class="monthnav">' + (m.prev ? '<a href="' + esc(m.prev[0]) + '" aria-label="Previous month">&#8249; ' + esc(m.prev[1]) + '</a>' : '<span>&#8249;</span>') +
    (m.next ? '<a href="' + esc(m.next[0]) + '" aria-label="Next month">' + esc(m.next[1]) + ' &#8250;</a>' : '<span>&#8250;</span>') +
    '<button class="toggle" id="theme" type="button">LIGHT</button></div>';
  top += '</header>';

  var bar = '<nav class="glass bar" aria-label="Sections">' + R.domains.map(function (d) {
    return '<a class="chip ' + d.hue + '" href="#' + d.id + '" data-d="' + d.id + '"><span class="dot"></span>' + esc(d.label) + (d.count != null ? ' <span class="n">' + esc(d.count) + '</span>' : '') + '</a>';
  }).join('') + nav + '</nav>';

  var wrap = document.createElement('div');
  wrap.className = 'wrap';
  wrap.innerHTML = top + bar + '<main class="parts" id="parts"></main>' + (R.footnote ? '<p class="foot-note">' + rich(R.footnote) + '</p>' : '');
  document.body.appendChild(wrap);

  /* ---------- routing: one domain at a time, by hash ---------- */
  var parts = document.getElementById('parts');
  var sideEl = null;
  parts.addEventListener('toggle', function () { fitSide(); }, true);
  function show(id, fromClick) {
    var d = null;
    R.domains.forEach(function (x) { if (x.id === id) d = x; });
    if (!d) d = R.domains[0];
    uid = 0;
    parts.innerHTML = sheet('main', d.mainLabel || d.label, d.main) + sheet('side', d.sideLabel || 'At a glance', d.side);
    sideEl = parts.querySelector('.sheet.side');
    [].forEach.call(document.querySelectorAll('.bar .chip'), function (c) {
      if (c.getAttribute('data-d') === d.id) c.setAttribute('aria-current', 'page'); else c.removeAttribute('aria-current');
    });
    wireTx();
    wireCal();
    fitSide();
    if (fromClick) {
      var barEl = document.querySelector('.bar');
      if (barEl && barEl.getBoundingClientRect().top < 0) window.scrollTo(0, window.scrollY + barEl.getBoundingClientRect().top - 10);
    }
  }
  function current() { return (location.hash || '').replace('#', '') || R.domains[0].id; }
  window.addEventListener('hashchange', function () { show(current(), true); });
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (a && a.getAttribute('href') === location.hash) { e.preventDefault(); show(current(), true); }
  });

  /* side sheet sticks only when it fits in the window, so it never overlaps or clips */
  function fitSide() {
    if (!sideEl) return;
    var fits = sideEl.offsetHeight + 32 < window.innerHeight && window.innerWidth > 900;
    sideEl.classList.toggle('stick', fits);
  }
  var rz = false;
  window.addEventListener('resize', function () { if (!rz) { rz = true; requestAnimationFrame(function () { rz = false; fitSide(); }); } }, { passive: true });

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

  /* ---------- theme toggle ---------- */
  var btn = document.getElementById('theme');
  function label() { btn.textContent = curTheme() === 'dark' ? 'LIGHT' : 'DARK'; }
  btn.addEventListener('click', function () {
    root.dataset.theme = curTheme() === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('gl-theme', root.dataset.theme); } catch (e) {}
    label();
  });
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
  upd();
})();
