// 実物の renderCard を index.html から取り出して評価し、soldout枠が <a> になるか確かめる。
// 🚨 写経せず「実物の条件式」を使う（check_zero_badge.js と同じ考え方）。
const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');

// soldout の分岐だけを切り出して、必要な部品をダミーで与えて実行する
const m = h.match(/if \(t\.soldout\) \{[\s\S]*?\n      \}/);
if (!m) { console.error('soldout分岐が見つからない'); process.exit(3); }
const src = m[0];

const today = new Date('2026-08-28');
const parseDateStr = s => new Date(s);
const formatDate = s => s;
const highlightShowDate = s => s;
const shrinkPrefList = s => s;

function run(t, ev, badgeType) {
  const fn = new Function('t', 'ev', 'badgeType', 'today', 'parseDateStr', 'formatDate',
    'highlightShowDate', 'shrinkPrefList', src + '\nreturn null;');
  return fn(t, ev, badgeType, today, parseDateStr, formatDate, highlightShowDate, shrinkPrefList);
}

let ng = 0;
// ① 枠にURLがある → <a> になるか
let r = run({ soldout: true, date: '2026-09-04', url: 'https://eplus.jp/sf/detail/AAA' },
            { date: '2026-11-01', links: { pia: 'https://t.pia.jp/x' } }, '一般発売（大阪 9/7公演）');
console.log('① 枠にURLあり →', /^<a /.test(r) ? 'リンクになる ✅' : 'リンクにならない ❌');
if (!/href="https:\/\/eplus\.jp\/sf\/detail\/AAA"/.test(r)) { console.log('   🚨 枠のURLが使われていない'); ng++; }

// ② 枠にURLが無い → カード共通リンクに落ちるか
r = run({ soldout: true, date: '2026-09-19' },
        { date: '2026-11-01', links: { pia: 'https://t.pia.jp/card' } }, '一般発売（愛知 9/19公演）');
console.log('② 枠にURL無し →', /href="https:\/\/t\.pia\.jp\/card"/.test(r) ? 'カード共通リンクへ ✅' : '落ちない ❌');
if (!/href="https:\/\/t\.pia\.jp\/card"/.test(r)) ng++;

// ③ どこにもURLが無い → <div> のまま（リンクを捏造しない）
r = run({ soldout: true, date: '2026-09-19' }, { date: '2026-11-01', links: {} }, '一般発売');
console.log('③ URLがどこにも無い →', /^<div /.test(r) ? 'divのまま ✅' : '❌');
if (!/^<div /.test(r)) ng++;

// ④ 公演日を過ぎたら出さない（安全弁が壊れていないか）
r = run({ soldout: true, date: '2026-08-01' }, { date: '2026-08-01', links: { pia: 'x' } }, '一般発売');
console.log('④ 公演日を過ぎた →', r === '' ? '非表示のまま ✅' : '❌ 出てしまう');
if (r !== '') ng++;

// ⑤ バッジの文言（予定枚数終了／販売終了）が保たれているか
r = run({ soldout: true, saleEnded: true, date: '2026-09-04', url: 'u' }, { date: '2026-11-01', links: {} }, 'x');
const a = />販売終了</.test(r);
r = run({ soldout: true, date: '2026-09-04', url: 'u' }, { date: '2026-11-01', links: {} }, 'x');
const b = />予定枚数終了</.test(r);
console.log('⑤ バッジ文言 →', (a && b) ? '販売終了/予定枚数終了とも保持 ✅' : '❌');
if (!(a && b)) ng++;

console.log(ng === 0 ? '\n判定: 全部OK' : '\n判定: NG ' + ng + '件');
process.exit(ng === 0 ? 0 : 1);
