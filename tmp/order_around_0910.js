// 指定idのカードが、画面で「どのカードに挟まれて出るか」を実物のロジックで再現する。
// 🚨並び順を書き写さない＝index.html の saleStartPending / classify / EVENTS.sort を eval する
//    （tools/check_order.js と同じ作法。写経すると「壊れているのに正常」を出す）。
//
//   node tmp/order_around_0910.js 7083 [前後の件数]
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

const targetId = Number(process.argv[2]);
const span = Number(process.argv[3] || 12);

const base = new Date();
const today = new Date(base.getFullYear(), base.getMonth(), base.getDate());
const now = new Date(today.getFullYear(), today.getMonth(), today.getDate(),
                     base.getHours(), base.getMinutes(), 0);
const pad = n => String(n).padStart(2, '0');
const todayStr = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`;
function parseDateStr(str) { const [y, m, d] = str.split('-').map(Number); return new Date(y, m - 1, d); }

const spSrc = html.match(/(function saleStartPending\(t\) \{[\s\S]*?\n  \})/)[1];
eval(spSrc);

const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);

const constSrc = html.match(/const SORT_PRESALE[^\n]*/)[0].replace('const ', 'var ');
const classifySrc = html.match(/(const classify = \(ev\) => \{[\s\S]*?\n    \};)/)[1]
  .replace('const classify =', 'var classify =');
eval(constSrc);
eval(classifySrc);

const sortSrc = html.match(/(EVENTS\.sort\(\(a, b\) => \{[\s\S]*?\n  \}\);)/)[1];
eval(sortSrc);

const i = EVENTS.findIndex(e => e.id === targetId);
if (i < 0) { console.log(`id=${targetId} は EVENTS に無い`); process.exit(1); }

console.log(`today=${todayStr} ${pad(now.getHours())}:${pad(now.getMinutes())} ／ 全${EVENTS.length}件中 ${i + 1}番目\n`);
const kindName = k => (k === 0 ? '🔵発売開始' : k === 1 ? '🟢締切　　' : `kind=${k}`);
for (let j = Math.max(0, i - span); j <= Math.min(EVENTS.length - 1, i + span); j++) {
  const e = EVENTS[j], c = classify(e);
  console.log('%s%s %s rank=%d %s  id=%-5d %s',
    j === i ? '👉' : '  ', String(j + 1).padStart(5),
    c.key, c.rank, kindName(c.kind), e.id, (e.artist || e.name || '').slice(0, 34));
}
