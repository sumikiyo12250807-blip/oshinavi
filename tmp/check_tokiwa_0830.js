// index.html の「表示しない」条件を実物から取り出して、TOKIWA の枠が画面に出るかを評価する
const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');
const m = h.match(/const EVENTS\s*=\s*(\[[\s\S]*?\n\s*\]);/);
const EVENTS = JSON.parse(m[1]);
const today = new Date(2026, 7, 30);           // 2026-08-30
const parseDateStr = s => { const [y, mo, d] = String(s).split('-').map(Number); return new Date(y, mo - 1, d); };

// 実物の条件式を index.html から抜き出す（写経しない）
const cond1 = h.match(/if \(t\.soldout\) \{\s*\n\s*if \((.+?)\) return "";/);
const cond2 = h.match(/if \(\((!t\.startDate.+?)\) \{\s*\n\s*return "";/);
console.log('取り出した条件1(soldout):', cond1 ? cond1[1] : '取れず');
console.log('取り出した条件2(販売終了):', cond2 ? cond2[1] : '取れず');

const ev = EVENTS.find(e => (e.name || '').includes('TOKIWA'));
console.log('\n== id' + ev.id + ' ' + ev.name + ' ==');
for (const t of ev.tickets) {
  const hideSold = t.soldout && parseDateStr(ev.date) < today;
  const hideEnded = (!t.startDate || parseDateStr(t.startDate) <= today) && parseDateStr(t.date) < today;
  console.log('  ' + (hideSold || hideEnded ? '❌非表示' : '✅表示') + ' | ' + t.type);
  console.log('        startDate=' + (t.startDate || 'なし') + ' date=' + t.date);
}
