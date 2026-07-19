// 並び順の番人（常設・push前必須）。**実日付**で、**index.html の実物のコードを eval して**検証する。
//
// 2026-07-19 の事故＝ユーザー「順番が変わってる 初めは本日発売で 次が本日まで販売 何で変えるの？」
//  真因は並び順ロジックではなく **当日ヒールのやり忘れ**：
//  ぴあは発売時刻を過ぎてから締切を出すため、朝ヒールだけだと今日発売の枠が startDate==date のまま残り、
//  「本日発売🔵」ではなく「本日まで販売🟢」として並ぶ（翌日には date が過去になり画面から消える）。
//
// 見落としの再発防止のために2つ直した:
//  ① tmp/test_sort_0710.js は today が 2026-07-10 固定で「違反0」と出た → **実日付**で見る
//  ② 検証ロジックを別言語で書き写したらズレた（締切の 23:59 を発売時刻と誤読し、
//     壊れているのに「正常」と出た）→ **書き写さず実物を eval する**
//
//   node tools/check_order.js
//   node tools/check_order.js 2026-07-19 20:00
//
// 終了コード: 2=壊れている（pushを止める） / 1=隠れ枠あり（警告） / 0=健全
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

const argDate = process.argv[2];
const argTime = process.argv[3];
const base = argDate ? new Date(argDate + 'T00:00:00') : new Date();
const today = new Date(base.getFullYear(), base.getMonth(), base.getDate());
const [hh, mm] = (argTime || `${new Date().getHours()}:${new Date().getMinutes()}`).split(':').map(Number);
const now = new Date(today.getFullYear(), today.getMonth(), today.getDate(), hh, mm, 0);
// toISOString は UTC に変換して日付がずれるのでローカルで組む
const pad = n => String(n).padStart(2, '0');
const todayStr = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`;

function parseDateStr(str) { const [y, m, d] = str.split('-').map(Number); return new Date(y, m - 1, d); }

// ---- 実物の saleStartPending をそのまま使う（書き写さない）----
const spSrc = html.match(/(function saleStartPending\(t\) \{[\s\S]*?\n  \})/)[1];
eval(spSrc);

const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);

// ---- 優先度の定数と classify を実物から取り出す（書き写さない）----
// 手で書き写すと実物とズレて「壊れているのに正常」「正常なのに違反」を出す（2026-07-19 に両方やった）。
// const は eval のスコープ外に漏れないので var に変えてから eval する。
const constSrc = html.match(/const SORT_PRESALE[^\n]*/)[0].replace('const ', 'var ');
const classifySrc = html.match(/(const classify = \(ev\) => \{[\s\S]*?\n    \};)/)[1]
  .replace('const classify =', 'var classify =');
eval(constSrc);
eval(classifySrc);

// ---- 実物の sort ブロックをそのまま使う（EVENTS を実際に並べ替える）----
const sortSrc = html.match(/(EVENTS\.sort\(\(a, b\) => \{[\s\S]*?\n  \}\);)/)[1];
eval(sortSrc);

// --- 1) 並び順の単調性 ---
let viol = 0, same = 0, rankViol = 0;
for (let i = 1; i < EVENTS.length; i++) {
  const p = classify(EVENTS[i - 1]), c = classify(EVENTS[i]);
  if (p.rank > c.rank) { rankViol++; continue; }
  if (p.rank !== c.rank || p.rank === 2) continue;
  if (p.key > c.key) {
    viol++;
    console.log(`[日付逆転] ${EVENTS[i-1].name} ${p.key} > ${EVENTS[i].name} ${c.key}`);
  } else if (p.key === c.key && p.kind > c.kind) {
    same++;
    console.log(`[同日で締切が発売開始より上] ${EVENTS[i-1].name}(締切) > ${EVENTS[i].name}(発売開始)`);
  }
}

// --- 2) 「これから発売の枠があるのに、先頭に発売開始が出ていない」 ---
// ※「今日発売の枠があるのに本日発売が無い」では誤検知する。今日発売でも発売時刻(10:00等)を過ぎれば
//   「販売中」に切り替わるのが仕様（2026-07-14 のユーザー指示）。夜に🔵が消えるのは正常。
//   よって **まだ発売時刻前＝saleStartPending が true** の枠だけを見張る。
const pendingEvents = EVENTS.filter(ev => (ev.tickets || []).some(t => saleStartPending(t)));
const headHasPresale = EVENTS.slice(0, 50).some(ev => classify(ev).kind === 0);
const missingTodayPresale = pendingEvents.length > 0 && !headHasPresale;

// --- 3) 隠れ枠（当日ヒール漏れ）---
const stale = [];
for (const ev of EVENTS) {
  for (const t of (ev.tickets || [])) {
    if (t.startDate && t.startDate === t.date && t.date <= todayStr && !t.saleUntilSoldOut && !t.soldout) {
      stale.push([ev.name, t.type]);
    }
  }
}

// --- 表示 ---
const KIND = { 0: '🔵発売開始', 1: '🟢締切' };
console.log(`\n--- 画面の先頭15件 (today=${todayStr} ${String(hh).padStart(2,'0')}:${String(mm).padStart(2,'0')}) ---`);
for (const ev of EVENTS.slice(0, 15)) {
  const c = classify(ev);
  console.log(`  ${c.key}  ${KIND[c.kind]}  ${(ev.name || '').slice(0, 38)}`);
}

console.log(`\n=== 並び順違反: 日付逆転 ${viol} / 同日順序 ${same} / rank逆転 ${rankViol} ===`);
if (missingTodayPresale) {
  console.log(`🚨 発売前の枠が ${pendingEvents.length} 件あるのに、画面の先頭50件に「発売開始🔵」が1枚も出ていません。`);
  console.log('   ＝並び順が壊れている疑い（発売前カードが締切カードより下に沈んでいる）。');
}
console.log(`（参考）発売時刻前＝発売開始🔵として並ぶ枠を持つカード: ${pendingEvents.length} 件`);
console.log(`=== 隠れ枠(startDate==date<=today) ${stale.length} 枠 ===`);
if (stale.length) {
  console.log('  ⚠️ 当日ヒール漏れの可能性。heal_stale_deadlines を流すこと。');
  console.log('     （ヒール後も残る分＝買える枠ゼロの削除候補待ち／w.pia.jp直販で機械照合不可、は正当な残存）');
  for (const [n, ty] of stale.slice(0, 10)) console.log(`     - ${n} | ${ty}`);
}

if (viol || same || rankViol || missingTodayPresale) process.exit(2);
process.exit(stale.length ? 1 : 0);
