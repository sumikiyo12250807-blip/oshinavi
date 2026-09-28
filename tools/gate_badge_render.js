#!/usr/bin/env node
/*
 * gate_badge_render.js — 画面に出るバッジの日付・時刻を「実際の表示コード」で確かめる番人
 *
 * 🚨Why（2026-09-28 夜 ユーザー指摘）：
 *   id24621 グレープカンパニー（ZAIKO）の枠
 *     「グレープライブシルバー（東京 10/25 12:00公演）9/28 21:00発売〜10/25 12:00」
 *   データは正しいのに、画面は「本日発売 〜10/25 21:00」と出ていた（締切の日付に発売時刻を付けた）。
 *   データのゲートは全部通っていた＝表示コードが出した文字そのものを見る番人が要る。
 *
 * やること：
 *   index.html の本体 <script>（const EVENTS を含むもの）を node の vm でそのまま実行し、
 *   ページ自身の renderCard(ev) で全エントリ（genre:new も含む）を描画して、枠ごとの
 *   .ticket-type-text / .ticket-date（.ticket-date-time 含む）/ .ticket-countdown を取り出して確かめる。
 *   document・window・localStorage・fetch などは「何を呼ばれても落ちない」Proxy で吸収する。
 *   「今日」「今の時刻」は Date を差し替えて固定する（--today・--time）。
 *
 * 見ること（1つでも破れたら exit 1）：
 *   A. 画面に「M/D HH:MM」が出ていれば、その組がその枠の type の中に隣り合って存在する（「R9年 」の有無は許す）
 *   B. 画面の日付が t.date なら「〜」が付いている（saleEndUnknown 型・startDate===date 型は除く）
 *   C. ラベル（本日発売・明日発売・発売開始まで あと N 日・販売中）と画面の日付が矛盾しない
 *   D. 描画で例外が出たカード＝判定不能として数える
 *
 * 使い方：
 *   node tools/gate_badge_render.js --html <index.htmlのコピー> [--today 2026-09-28[,2026-09-29...]]
 *          [--time 00:00,23:59] [--report tmp/gate_badge_render_report.txt] [--append] [--label 名前]
 *   index.html は読むだけ。呼び出し役 tools/gate_badge_render.py がコピーを作ってから渡す。
 */
'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');

// ── 引数 ──
const args = process.argv.slice(2);
function opt(name, def) {
  const i = args.indexOf(name);
  return i >= 0 && i + 1 < args.length ? args[i + 1] : def;
}
const HTML = opt('--html', 'index.html');
const RealDate = Date;
const pad = n => String(n).padStart(2, '0');
const localToday = (() => { const d = new RealDate(); return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; })();
const TODAYS = opt('--today', localToday).split(',').map(s => s.trim()).filter(Boolean);
const TIMES = opt('--time', '00:00,23:59').split(',').map(s => s.trim()).filter(Boolean);
const REPORT = opt('--report', path.join('tmp', 'gate_badge_render_report.txt'));
const APPEND = args.includes('--append');
const LABEL = opt('--label', '');
const MAX_SHOW = +opt('--max-show', '200');

// ── 本体 script を取り出す ──
const src = fs.readFileSync(HTML, 'utf8');
let mainJs = null;
{
  const re = /<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g;
  let m;
  while ((m = re.exec(src))) {
    if (m[1].includes('const EVENTS') && m[1].includes('function renderCard')) { mainJs = m[1]; break; }
  }
}
if (!mainJs) { console.error('本体の<script>（const EVENTS と renderCard）が見つからない'); process.exit(2); }
const mainScript = new vm.Script(mainJs, { filename: 'index.html#main' });

// ── 何を呼ばれても落ちないスタブ ──
function makeStub() {
  const fn = function () {};
  let proxy;
  const handler = {
    get(target, prop) {
      if (prop === Symbol.toPrimitive) return hint => (hint === 'number' ? 0 : '');
      if (prop === Symbol.iterator) return function* () {};
      if (prop === 'then') return undefined;           // thenable と誤認させない
      if (prop === 'length') return 0;
      if (prop === 'toString' || prop === 'valueOf') return () => '';
      return proxy;
    },
    set() { return true; },
    has() { return true; },
    deleteProperty() { return true; },
    apply() { return proxy; },
    construct() { return proxy; },
  };
  proxy = new Proxy(fn, handler);
  return proxy;
}

// ── 固定した Date ──
function makeFixedDate(y, mo, d, hh, mi) {
  const fixed = new RealDate(y, mo - 1, d, hh, mi, 0, 0).getTime();
  class FixedDate extends RealDate {
    constructor(...a) { if (a.length === 0) super(fixed); else super(...a); }
    static now() { return fixed; }
  }
  return FixedDate;
}

function buildContext(FixedDate) {
  const stub = makeStub();
  const sandbox = {
    console: { log() {}, warn() {}, error() {}, info() {}, debug() {} },
    Date: FixedDate,
    Math, JSON, Object, Array, String, Number, Boolean, RegExp, Map, Set, WeakMap, WeakSet, Symbol, Promise, Proxy, Reflect,
    Error, TypeError, RangeError, SyntaxError, ReferenceError,
    parseInt, parseFloat, isNaN, isFinite, encodeURIComponent, decodeURIComponent, encodeURI, decodeURI,
    Intl, URL, URLSearchParams,
    setTimeout: () => 0, clearTimeout: () => {}, setInterval: () => 0, clearInterval: () => {},
    requestAnimationFrame: () => 0, cancelAnimationFrame: () => {}, queueMicrotask: () => {},
    document: stub, localStorage: stub, sessionStorage: stub, fetch: stub, navigator: stub, location: stub,
    history: stub, performance: stub, matchMedia: stub, gtag: stub, dataLayer: stub,
    IntersectionObserver: stub, MutationObserver: stub, ResizeObserver: stub, Image: stub, Event: stub,
    CustomEvent: stub, HTMLElement: stub, getComputedStyle: stub, alert: stub, confirm: stub, open: stub,
    scrollTo: stub, addEventListener: stub, removeEventListener: stub, innerWidth: 1280, innerHeight: 800,
    scrollY: 0, pageYOffset: 0,
  };
  sandbox.window = sandbox;
  sandbox.self = sandbox;
  sandbox.globalThis = sandbox;
  return vm.createContext(sandbox);
}

// ── HTML から文字を取り出す ──
const stripTags = s => s.replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/\s+/g, ' ').trim();
function pickDiv(html, cls) {
  // <div class="ticket-date ..."> ... </div>（中に span はあっても div は無い）
  const re = new RegExp(`<div class="${cls}(?:\\s[^"]*)?">([\\s\\S]*?)</div>`);
  const m = html.match(re);
  return m ? stripTags(m[1]) : null;
}
function pickSpan(html, cls) {
  // ticket-type-text の中には show-date などの span が入れ子で入る＝ticket-type の div ごと取る
  const re = new RegExp(`<span class="${cls}">([\\s\\S]*?)</span>\\s*</div>`);
  const m = html.match(re);
  return m ? stripTags(m[1]) : null;
}
function splitItems(html) {
  // 1枠だけのカードで描くので、最初の ticket-item から後ろを1枠分として扱う
  const i = html.indexOf('class="ticket-item');
  return i < 0 ? [] : [html.slice(i)];
}

// ── 判定 ──
const escRe = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
function md(dateStr) { const [, m, d] = dateStr.split('-').map(Number); return `${m}/${d}`; }
function addDays(dateStr, n) {
  const [y, m, d] = dateStr.split('-').map(Number);
  const x = new RealDate(y, m - 1, d + n);
  return `${x.getFullYear()}-${pad(x.getMonth() + 1)}-${pad(x.getDate())}`;
}
function diffDays(a, b) { // b - a（日）
  const [y1, m1, d1] = a.split('-').map(Number), [y2, m2, d2] = b.split('-').map(Number);
  return Math.round((RealDate.UTC(y2, m2 - 1, d2) - RealDate.UTC(y1, m1 - 1, d1)) / 86400000);
}

let timedCount = 0;   // 画面に「M/D HH:MM」が出た枠の数（Aが空振りしていない証拠）
function checkItem(ev, t, item, todayStr) {
  const v = [];
  const typeText = pickSpan(item, 'ticket-type-text') || '';
  const dateText = pickDiv(item, 'ticket-date') || '';
  const cd = pickDiv(item, 'ticket-countdown');
  const screen = `［${typeText}］${dateText}｜${cd === null ? '(ラベルなし)' : cd}`;
  const soldout = /class="ticket-item soldout/.test(item);
  const rawType = t.type || '';

  // A. 画面の「M/D HH:MM」が type の中で隣り合っているか
  const dm = dateText.match(/(\d{1,2})\/(\d{1,2})\s*(\d{1,2}):(\d{2})/);
  if (dm) {
    timedCount++;
    const re = new RegExp(`(?<![\\d/])0?${dm[1]}/0?${dm[2]}\\s*0?${+dm[3]}:${dm[4]}(?!\\d)`);
    if (!re.test(rawType)) v.push(['A', `画面の「${dm[1]}/${dm[2]} ${dm[3]}:${dm[4]}」が type に無い`]);
  }
  if (soldout || /予定枚数に達し次第終了/.test(dateText)) return { v, screen, soldout };

  const dOnly = (dateText.match(/(\d{1,2}\/\d{1,2})/) || [])[1] || null;
  const hasTilde = dateText.startsWith('〜');
  const endUnknownForm = /〜発売中$/.test(dateText);
  const isDate = t.date && dOnly === md(t.date);
  const isStart = t.startDate && dOnly === md(t.startDate);
  const sameSD = t.startDate && t.startDate === t.date;

  // B. 画面の日付が t.date なら「〜」
  if (isDate && !isStart && !t.saleEndUnknown && !hasTilde) v.push(['B', `締切の日付 ${md(t.date)} に「〜」が無い`]);

  // C. ラベルと日付の矛盾
  const lab = cd || '';
  if (lab === '本日発売') {
    if (t.startDate !== todayStr) v.push(['C', `本日発売なのに startDate=${t.startDate || 'なし'}（今日 ${todayStr}）`]);
    if (!isDate && !isStart) v.push(['C', `本日発売なのに日付 ${dOnly} が startDate/date のどちらでもない`]);
    if (hasTilde && !isDate) v.push(['C', `本日発売で「〜」付きなのに日付が締切ではない`]);
    if (!hasTilde && isDate && !isStart && !sameSD) v.push(['C', `本日発売で締切の日付に「〜」が無い`]);
  } else if (lab === '明日発売') {
    if (t.startDate !== addDays(todayStr, 1)) v.push(['C', `明日発売なのに startDate=${t.startDate || 'なし'}`]);
    if (!isStart || hasTilde) v.push(['C', `明日発売なのに日付が発売日 ${t.startDate ? md(t.startDate) : '?'} でない／「〜」付き`]);
  } else if (/^発売開始まで あと (\d+) 日$/.test(lab)) {
    const n = +lab.match(/(\d+)/)[1];
    const real = t.startDate ? diffDays(todayStr, t.startDate) : null;
    if (real !== n) v.push(['C', `あと ${n} 日なのに startDate まで ${real} 日`]);
    if (!isStart || hasTilde) v.push(['C', `発売前なのに日付が発売日でない／「〜」付き`]);
  } else if (lab === '販売中') {
    if (endUnknownForm) {
      if (!isStart) v.push(['C', `「〜発売中」なのに日付が発売日でない`]);
      if (t.startDate && t.startDate > todayStr) v.push(['C', `発売日前なのに販売中`]);
    } else {
      if (!isDate || !hasTilde) v.push(['C', `販売中なのに日付が「〜締切」でない`]);
      if (t.startDate && t.startDate > todayStr) v.push(['C', `発売日前なのに販売中`]);
      if (t.date && t.date < todayStr) v.push(['C', `締切を過ぎているのに販売中`]);
    }
  } else {
    v.push(['C', `見慣れないラベル「${lab}」`]);
  }
  return { v, screen, soldout };
}

// ── 1回分（日付×時刻）──
function runOnce(todayStr, timeStr) {
  const [y, mo, d] = todayStr.split('-').map(Number);
  const [hh, mi] = timeStr.split(':').map(Number);
  const ctx = buildContext(makeFixedDate(y, mo, d, hh, mi));
  let loadErr = null;
  try { mainScript.runInContext(ctx, { timeout: 600000 }); } catch (e) { loadErr = e; }
  let g;
  try {
    g = vm.runInContext('({ EVENTS: EVENTS, renderCard: renderCard, todayStr: todayStr })', ctx);
  } catch (e) {
    throw new Error(`EVENTS/renderCard を取り出せない（読み込み時の例外: ${loadErr && loadErr.message}）: ${e.message}`);
  }
  if (g.todayStr !== todayStr) throw new Error(`Date の固定が効いていない（ページの今日=${g.todayStr}）`);
  const res = { todayStr, timeStr, cards: 0, items: 0, soldItems: 0, A: 0, B: 0, C: 0, D: 0, viol: [], dErr: [], loadErr: loadErr ? String(loadErr.message || loadErr) : null };
  for (const ev of g.EVENTS) {
    res.cards++;
    // D. カード丸ごとの描画
    try { g.renderCard(ev); } catch (e) { res.D++; res.dErr.push({ id: ev.id, name: ev.name, err: String(e && e.message || e) }); continue; }
    // 枠と画面の対応を取るため、1枠ずつのカードで描く（地域は「すべて」＝枠は並べ替え以外変わらない）
    for (const t of (ev.tickets || [])) {
      let html;
      try { html = g.renderCard(Object.assign({}, ev, { tickets: [t] })); }
      catch (e) { res.D++; res.dErr.push({ id: ev.id, name: ev.name, err: `枠「${t.type}」: ${e && e.message || e}` }); continue; }
      const items = splitItems(html);
      if (!items.length) continue;               // 期限切れ等で出ない枠
      res.items++;
      const r = checkItem(ev, t, items[0], todayStr);
      if (r.soldout) res.soldItems++;
      for (const [k, msg] of r.v) {
        res[k]++;
        res.viol.push({ k, id: ev.id, name: ev.name, type: t.type, date: t.date, startDate: t.startDate || '', screen: r.screen, msg });
      }
    }
  }
  return res;
}

// ── 実行 ──
const t0 = RealDate.now();
const lines = [];
const head = `=== gate_badge_render ${LABEL ? '[' + LABEL + '] ' : ''}html=${HTML} 実行=${new RealDate().toISOString()} ===`;
lines.push(head);
let bad = false;
const summaries = [];
for (const day of TODAYS) {
  for (const tm of TIMES) {
    const s = RealDate.now();
    timedCount = 0;
    const r = runOnce(day, tm);
    const sec = ((RealDate.now() - s) / 1000).toFixed(1);
    const sum = `${LABEL ? '[' + LABEL + '] ' : ''}今日=${day} ${tm}：カード${r.cards}件・枠${r.items}（売切表示${r.soldItems}・時刻付き${timedCount}）・A違反${r.A}・B${r.B}・C${r.C}・描画失敗${r.D}（${sec}秒）`;
    summaries.push(sum);
    lines.push('', '## ' + sum);
    if (r.loadErr) lines.push(`  （読み込み時の例外＝スタブで吸収しきれなかった初期化。判定には影響なし）: ${r.loadErr}`);
    const shown = r.viol.slice(0, MAX_SHOW);
    for (const x of shown) {
      lines.push(`  ${x.k} id${x.id} ${x.name}`);
      lines.push(`     type: ${x.type}`);
      lines.push(`     data: startDate=${x.startDate} date=${x.date}`);
      lines.push(`     画面: ${x.screen}`);
      lines.push(`     → ${x.msg}`);
    }
    if (r.viol.length > shown.length) lines.push(`  …ほか ${r.viol.length - shown.length} 件`);
    for (const x of r.dErr.slice(0, MAX_SHOW)) lines.push(`  D id${x.id} ${x.name}: ${x.err}`);
    if (r.A || r.B || r.C || r.D) bad = true;
  }
}
lines.push('', `所要 ${((RealDate.now() - t0) / 1000).toFixed(1)} 秒`, '');
fs.mkdirSync(path.dirname(REPORT), { recursive: true });
if (APPEND) fs.appendFileSync(REPORT, lines.join('\n') + '\n', 'utf8');
else fs.writeFileSync(REPORT, lines.join('\n') + '\n', 'utf8');
for (const s of summaries) console.log(s);
process.exit(bad ? 1 : 0);
