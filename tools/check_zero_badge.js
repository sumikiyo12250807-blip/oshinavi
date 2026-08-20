// 「カードは出るのにバッジ（買える枠）が1枚も無い」エントリの番人。
// **push前必須**・朝ルーチンで毎日回す。
//
// 2026-08-20 の発見（ユーザーが画面で気づいた）＝
//   BALLISTIK BOYZ × TOWER RECORDS CAFE(3570) は販売期間6つとも終了していて、
//   カードだけ出てバッジが1枚も無かった。全件を数えたら **同じ状態が102件**、
//   うち **公演まで31日以上あるのに買えないものが54件** あった。
//   ＝「情報だけあって買えない」＝推し活サイトとしては致命的。
//
// なぜ今まで誰も見つけられなかったか（＝この番人が要る理由）:
//   ・heal_stale_deadlines は **startDate==date の隠れ枠**しか見ない
//   ・reconcile_pia --new は **新着プール**しか見ない／--ids は指定したものだけ
//   ・check_expired は **エントリの全枠が死亡**した子しか拾わない（1枠でも未来日付なら通過）
//   → 「枠は未来日付だが startDate が無く date が過去」など、どの網にもかからない型が残る。
//   この番人は **実際に画面へ出る枠の数**を数えるので、原因の型に関係なく拾える。
//
// 🚨判定は index.html の**実物の条件式を取り出して eval する**（書き写さない）。
//   書き写すと表示ロジックの変更に追従できず「壊れているのに正常」と出る
//   （check_order.js が 2026-07-19 に踏んだのと同じ罠）。
//
//   node tools/check_zero_badge.js            … 一覧を出す
//   node tools/check_zero_badge.js --ids      … 要対応(31日より先)の id をカンマ区切りで出す
//   node tools/check_zero_badge.js 2026-08-20 … 日付を指定して検証
//
// 終了コード: 2=要対応あり(公演まで31日より先で枠0) / 1=近い公演のみ枠0 / 0=健全
const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

const args = process.argv.slice(2);
const wantIds = args.includes('--ids');
const argDate = args.find(a => /^\d{4}-\d{2}-\d{2}$/.test(a));
const base = argDate ? new Date(argDate + 'T00:00:00') : new Date();
const today = new Date(base.getFullYear(), base.getMonth(), base.getDate());
const pad = n => String(n).padStart(2, '0');
const todayStr = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`;

function parseDateStr(str) { const [y, m, d] = str.split('-').map(Number); return new Date(y, m - 1, d); }

// ---- 実物の条件式を取り出す（書き写さない）----
// ① 販売終了した枠を描かない条件
const mHide = html.match(/\/\/ 販売終了したチケットは表示しない[\s\S]*?\n\s*if \(([\s\S]*?)\) \{/);
if (!mHide) { console.error('🚨 非表示ルールが index.html から取り出せない。表示ロジックが変わった可能性がある。'); process.exit(3); }
const isHidden = new Function('t', 'ev', 'today', 'parseDateStr', `return ${mHide[1].trim()};`);

// ② soldout / saleEnded の枠を描かない条件（公演日を過ぎたら出さない安全弁）
const mSold = html.match(/if \(t\.soldout\) \{\s*\n\s*if \(([\s\S]*?)\) return "";/);
if (!mSold) { console.error('🚨 soldout ルールが index.html から取り出せない。'); process.exit(3); }
const soldHidden = new Function('t', 'ev', 'today', 'parseDateStr', `return ${mSold[1].trim()};`);

const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);

const near = [], far = [], done = [];
for (const ev of EVENTS) {
  if (ev.verified !== true) continue;
  const ts = ev.tickets || [];
  let shown = 0;
  for (const t of ts) {
    if (t.soldout) { if (!soldHidden(t, ev, today, parseDateStr)) shown++; continue; }
    if (!isHidden(t, ev, today, parseDateStr)) shown++;
  }
  if (shown > 0) continue;
  const d = ev.date || '';
  if (!d || d <= todayStr) { done.push(ev); continue; }          // 公演が終わる＝翌朝の削除ルートで消える
  const days = Math.round((parseDateStr(d) - today) / 86400000);
  (days > 30 ? far : near).push({ ev, days });
}

if (wantIds) {
  console.log(far.map(x => x.ev.id).join(','));
  process.exit(far.length ? 2 : 0);
}

const link = ev => (ev.links || {}).pia || (ev.links || {}).eplus || (ev.links || {}).official || '(リンク無し)';
console.log(`=== バッジ（買える枠）が1枚も出ないエントリ（today=${todayStr}）===`);
console.log(`  公演が今日まで … ${done.length}件（翌朝の削除ルートで消える＝正常）`);
console.log(`  公演まで30日以内 … ${near.length}件（前売り終了なら自然だが要確認）`);
console.log(`  🚨公演まで31日より先 … ${far.length}件（1か月以上先なのに買えない＝取り込み漏れを疑う）`);
console.log('');
if (far.length) {
  console.log('【🚨要対応】公演まで31日より先なのに買える枠が0');
  for (const { ev, days } of far.sort((a, b) => a.days - b.days)) {
    console.log(`  あと${String(days).padStart(3)}日 id${String(ev.id).padEnd(5)} [${(ev.genre || '').padEnd(9)}] 公演${ev.date} 枠${(ev.tickets || []).length}  ${(ev.artist || '').slice(0, 34)}`);
    console.log(`           ${link(ev)}`);
  }
  console.log('');
  console.log('→ 直し方: この id を reconcile_pia.py --ids で照合し、');
  console.log('   ぴあに買える枠があれば build_pia_entries で取り直す／無ければ削除ゲートへ回す。');
}
if (near.length) {
  console.log(`【参考】公演まで30日以内で枠0（${near.length}件）`);
  for (const { ev, days } of near.sort((a, b) => a.days - b.days).slice(0, 15)) {
    console.log(`  あと${String(days).padStart(3)}日 id${String(ev.id).padEnd(5)} 公演${ev.date}  ${(ev.artist || '').slice(0, 34)}`);
  }
  if (near.length > 15) console.log(`  … ほか${near.length - 15}件`);
}

process.exit(far.length ? 2 : (near.length ? 1 : 0));
