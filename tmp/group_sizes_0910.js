// 画面の頭から「日付のかたまり」が何件ずつ続くかを、実物のロジックで数える。
// 🚨並び順は書き写さない＝index.html の実物を eval する（tools/check_order.js と同じ作法）。
//   node tmp/group_sizes_0910.js [先頭いくつのかたまりを見るか]
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

const base = new Date();
const today = new Date(base.getFullYear(), base.getMonth(), base.getDate());
const now = new Date(today.getFullYear(), today.getMonth(), today.getDate(),
                     base.getHours(), base.getMinutes(), 0);
const pad = n => String(n).padStart(2, '0');
const todayStr = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`;
function parseDateStr(str) { const [y, m, d] = str.split('-').map(Number); return new Date(y, m - 1, d); }

eval(html.match(/(function saleStartPending\(t\) \{[\s\S]*?\n  \})/)[1]);
const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);
eval(html.match(/const SORT_PRESALE[^\n]*/)[0].replace('const ', 'var '));
eval(html.match(/(const classify = \(ev\) => \{[\s\S]*?\n    \};)/)[1].replace('const classify =', 'var classify ='));
eval(html.match(/(EVENTS\.sort\(\(a, b\) => \{[\s\S]*?\n  \}\);)/)[1]);

const limit = Number(process.argv[2] || 12);
const groups = [];
for (const e of EVENTS) {
  const c = classify(e);
  const label = c.rank === 2 ? '（買える枠なし）' : `${c.key} ${c.kind === 0 ? '🔵発売開始' : '🟢締切'}`;
  if (!groups.length || groups[groups.length - 1].label !== label) groups.push({ label, n: 0, boxes: 0 });
  groups[groups.length - 1].n++;
  groups[groups.length - 1].boxes += (e.tickets || []).length;
}

console.log(`today=${todayStr} ／ 全${EVENTS.length}件\n`);
let acc = 0;
for (const g of groups.slice(0, limit)) {
  acc += g.n;
  // 🚨Node の console.log は %4d のような桁指定を解釈しない（literal で残って引数がずれる）。
  //    自分で padStart する。
  console.log(g.label.padEnd(22) + '  カード' + String(g.n).padStart(4) + '枚'
    + '  枠' + String(g.boxes).padStart(5) + '個'
    + '  （先頭からの累計 ' + acc + '枚）');
}
