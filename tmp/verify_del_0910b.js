// 対象19件について ① dateLabel/券種名に date より後の日付が無いか ② 配信枠が無いか
// ③ 同名アーティストの別エントリ（ツアーの続き）が残っているか を機械で調べる。
const fs = require('fs');
const html = fs.readFileSync('C:/Users/user/oshinavi/index.html', 'utf8');
const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);
const IDS = [809, 1052, 1812, 2084, 2728, 3154, 3765, 4203, 4324, 4941, 4978, 5014, 5577, 5643, 5731, 6187, 6195, 7434, 7466];
const TODAY = '2026-09-10';

// 文字列から日付候補を拾う（YYYY年M月D日 / M/D）。年が無ければ2026年扱い。
function pickDates(s, baseYear) {
  const res = [];
  let m;
  const re1 = /(\d{4})年(\d{1,2})月(\d{1,2})日/g;
  while ((m = re1.exec(s))) res.push(`${m[1]}-${String(m[2]).padStart(2, '0')}-${String(m[3]).padStart(2, '0')}`);
  const re2 = /(?<!\d)(\d{1,2})\/(\d{1,2})(?!\d)/g;
  while ((m = re2.exec(s))) {
    const mo = Number(m[1]), da = Number(m[2]);
    if (mo >= 1 && mo <= 12 && da >= 1 && da <= 31) res.push(`${baseYear}-${String(mo).padStart(2, '0')}-${String(da).padStart(2, '0')}`);
  }
  return res;
}

const HAISHIN = /(配信|視聴|アーカイブ|ライブビューイング|ライビュ|LIVE VIEWING|オンライン)/i;

const lines = [];
for (const id of IDS) {
  const ev = EVENTS.find(e => e.id === id);
  const y = Number((ev.date || '2026-01-01').slice(0, 4));
  const found = new Set();
  for (const d of pickDates(ev.dateLabel || '', y)) if (d > ev.date) found.add('dateLabel:' + d);
  for (const t of (ev.tickets || [])) {
    for (const d of pickDates(t.type || '', y)) if (d > ev.date) found.add('券種名:' + d + ' <= ' + t.type);
  }
  const haishin = (ev.tickets || []).filter(t => HAISHIN.test(t.type || '')).map(t => t.type);
  if (HAISHIN.test(ev.artist || '') || HAISHIN.test(ev.venue || '')) haishin.push('(名称に配信語)');
  // 同名系の別エントリ
  const key = (ev.artist || '').replace(/[\s　]/g, '').slice(0, 8);
  const sibs = EVENTS.filter(e => e.id !== id && key.length >= 4 && (e.artist || '').replace(/[\s　]/g, '').includes(key))
    .map(e => `id${e.id} 公演${e.date} ${e.artist}`);
  lines.push({
    id, artist: ev.artist, date: ev.date, dateLabel: ev.dateLabel,
    laterDates: [...found], haishinSlots: haishin, siblings: sibs
  });
}
fs.writeFileSync('C:/Users/user/oshinavi/tmp/verify_del_0910b.json', JSON.stringify(lines, null, 1), 'utf8');

// おまけ: RAY YUZUKA を全文検索
const ray = EVENTS.filter(e => /YUZUKA|ゆづか|Salon de RAY/i.test((e.artist || '') + (e.venue || '') + (e.dateLabel || '')))
  .map(e => `id${e.id} 公演${e.date} ${e.artist} / ${e.venue} / ${e.dateLabel}`);
fs.writeFileSync('C:/Users/user/oshinavi/tmp/verify_del_0910_ray.txt', ray.join('\n') || '(none)', 'utf8');
console.log('ok', lines.length, 'ray=', ray.length);
