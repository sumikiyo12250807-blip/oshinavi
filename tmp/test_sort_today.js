// index.html の EVENTS.sort ブロックを「実物のまま」切り出して実行し、並び順を検証する。
// 写経ではなくソースを eval するので、実ページと同じ挙動をテストできる。
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

// today / now を固定
const today = new Date(2026, 6, 19); today.setHours(0, 0, 0, 0);
const now = new Date(2026, 6, 19, 20, 0, 0);
function parseDateStr(str) { const [y, m, d] = str.split('-').map(Number); return new Date(y, m - 1, d); }
function saleStartPending(t) {
  if (!t.startDate) return false;
  const sd = parseDateStr(t.startDate);
  if (sd > today) return true;
  if (sd < today) return false;
  const m = (t.type || '').match(/(\d{1,2}):(\d{2})/);
  if (!m) return false;
  const start = new Date(sd); start.setHours(+m[1], +m[2], 0, 0);
  return now < start;
}

const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);

// 実物の sort ブロックを抜き出す
const src = html.match(/(const SORT_PRESALE[\s\S]*?EVENTS\.sort\(\(a, b\) => \{[\s\S]*?\n  \}\);)/)[1];
if (!src) { console.error('sort block not found'); process.exit(1); }
eval(src);

// --- 検証 ---
function classifyRef(ev) {
  const cands = [];
  for (const t of (ev.tickets || [])) {
    if (t.soldout) continue;
    if (t.saleUntilSoldOut) { if (parseDateStr(t.date) >= today) cands.push([t.date, 1]); continue; }
    if (saleStartPending(t)) { cands.push([t.startDate, 0]); continue; }
    if (parseDateStr(t.date) >= today) cands.push([t.date, 1]);
  }
  if (!cands.length) return { rank: 2, key: ev.date, kind: 1 };
  cands.sort((x, y) => (x[0] !== y[0] ? (x[0] < y[0] ? -1 : 1) : x[1] - y[1]));
  return { rank: 0, key: cands[0][0], kind: cands[0][1] };
}

let viol = 0, rankViol = 0, sameDayViol = 0;
for (let i = 1; i < EVENTS.length; i++) {
  const p = classifyRef(EVENTS[i - 1]), c = classifyRef(EVENTS[i]);
  if (p.rank > c.rank) { rankViol++; continue; }
  if (p.rank !== c.rank) continue;
  if (p.rank === 2) continue;
  if (p.key > c.key) { viol++; console.log('日付逆転', EVENTS[i-1].artist, p.key, '>', EVENTS[i].artist, c.key); }
  else if (p.key === c.key && p.kind > c.kind) {
    sameDayViol++;
    console.log('同日で締切が発売開始より上', EVENTS[i-1].artist, '(締切)', '>', EVENTS[i].artist, '(発売開始)');
  }
}
console.log(`\n=== 違反: 日付逆転 ${viol} / 同日順序 ${sameDayViol} / rank逆転 ${rankViol} ===`);

const KIND = { 0: '🔵発売開始', 1: '🟢締切' };
console.log('\n--- 先頭25件 ---');
for (const ev of EVENTS.slice(0, 25)) {
  const c = classifyRef(ev);
  console.log(`${c.key}  ${KIND[c.kind]}  ${(ev.artist || '').slice(0, 30)}`);
}
const last = EVENTS.slice(-3).map(e => `${e.artist} (rank${classifyRef(e).rank})`);
console.log('\n--- 末尾3件 ---\n' + last.join('\n'));
