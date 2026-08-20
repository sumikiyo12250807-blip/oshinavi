// 実物のロジックをそのままevalして、育成した4件が地方フィルタでどこに出るか確かめる
// （写経で検証しない＝feedback_display_order）
const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');

function grab(re, label) {
  const m = h.match(re);
  if (!m) throw new Error('見つからない: ' + label);
  return m[0];
}

const EVENTS = JSON.parse(h.match(/ {2}const EVENTS = (\[[\s\S]*?\]);/)[1]);
const src = [
  grab(/const PREFECTURE_TO_REGION\s*=\s*\{[\s\S]*?\n {2}\};/, 'PREFECTURE_TO_REGION'),
  grab(/const PREF_LIST\s*=\s*Object\.keys\(PREFECTURE_TO_REGION\);/, 'PREF_LIST'),
  grab(/function parseDateStr\([\s\S]*?\n {2}\}/, 'parseDateStr'),
  grab(/function isTicketActive\([\s\S]*?\n {2}\}/, 'isTicketActive'),
  grab(/function eventRegions\([\s\S]*?\n {2}\}/, 'eventRegions'),
].join('\n');

const today = new Date(2026, 7, 3);
const fn = new Function('EVENTS', 'today', src + '\nreturn {eventRegions, PREF_LIST};');
const { eventRegions } = fn(EVENTS, today);

for (const id of [3631, 3635, 3636, 3662, 3640]) {
  const ev = EVENTS.find(e => e.id === id);
  if (!ev) { console.log(id, 'なし'); continue; }
  const r = [...eventRegions(ev)];
  console.log(id, '| pref=' + ev.prefecture, '| 地方フィルタ=' + JSON.stringify(r),
    '| 全国タブに出る=' + (ev.prefecture === '全国'));
}
