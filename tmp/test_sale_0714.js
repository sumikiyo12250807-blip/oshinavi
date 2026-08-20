// index.html から saleStartPending を実物のまま切り出して検証（写経しない）
const fs = require('fs');
const src = fs.readFileSync('index.html', 'utf8');
const m = src.match(/function saleStartPending\(t\) \{[\s\S]*?\n  \}/);
if (!m) { console.log('NG: saleStartPending が見つからない'); process.exit(1); }

const today = new Date(2026, 6, 14);            // 2026-07-14
const now = new Date(2026, 6, 14, 15, 0, 0);    // 当日15:00 の想定
function parseDateStr(s) { const [y, mo, d] = s.split('-').map(Number); return new Date(y, mo - 1, d); }
function daysFrom(s) { return Math.round((parseDateStr(s) - today) / 86400000); }
eval(m[0]);

const cases = [
  { name: '未ヒールの隠れ枠(発売時刻後)', t: { startDate: '2026-07-14', date: '2026-07-14', type: '一般発売（熊本 9/5公演）7/14 10:00発売' }, pending: false },
  { name: 'ヒール後(締切23:59を発売時刻と誤読しないこと)', t: { startDate: '2026-07-14', date: '2026-09-04', type: '一般発売（熊本 9/5公演）〜9/4 23:59' }, pending: false },
  { name: '今日発売だがまだ時刻前(19:00発売)', t: { startDate: '2026-07-14', date: '2026-07-14', type: '一般発売（東京 8/30公演）7/14 19:00発売' }, pending: true },
  { name: '明日発売', t: { startDate: '2026-07-15', date: '2026-07-15', type: '一般発売（東京 9/15公演）7/15 10:00発売' }, pending: true },
  { name: '昨日発売開始・締切は先', t: { startDate: '2026-07-13', date: '2026-09-04', type: '一般発売（東京 9/5公演）〜9/4 23:59' }, pending: false },
  { name: 'startDateなし(受付中)', t: { date: '2026-09-04', type: '一般発売（東京 9/5公演）〜9/4 23:59' }, pending: false },
];

// renderCard のラベル決定（実装と同じ条件式）
function labelOf(t) {
  if (saleStartPending(t)) {
    const sdiff = daysFrom(t.startDate);
    return sdiff === 0 ? '本日発売(発売前)' : sdiff === 1 ? '明日発売' : `発売開始まで あと ${sdiff} 日`;
  }
  if (t.startDate && parseDateStr(t.date) >= today) {
    if (t.startDate === t.date) return '本日発売(締切不明)';
    if (daysFrom(t.startDate) === 0) return `本日発売 〜${t.date}`;
    return `販売中 〜${t.date}`;
  }
  if (!t.startDate && parseDateStr(t.date) >= today) return `販売中 〜${t.date}`;
  return '終了';
}

let ng = 0;
for (const c of cases) {
  const p = saleStartPending(c.t);
  const ok = p === c.pending;
  if (!ok) ng++;
  console.log(`${ok ? 'OK ' : 'NG '} ${c.name}\n     pending=${p} (期待 ${c.pending}) → 表示「${labelOf(c.t)}」`);
}
console.log(ng ? `\n${ng}件 失敗` : '\n全ケース OK');
