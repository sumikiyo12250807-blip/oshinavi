// 削除候補19件の検証用ダンプ。index.html の実物の表示条件式を取り出して visible を判定する。
const fs = require('fs');
const html = fs.readFileSync('C:/Users/user/oshinavi/index.html', 'utf8');

const TODAY_STR = '2026-09-10';
const today = new Date(2026, 8, 10);
function parseDateStr(str) { const [y, m, d] = String(str).split('-').map(Number); return new Date(y, m - 1, d); }

const mHide = html.match(/\/\/ 販売終了したチケットは表示しない[\s\S]*?\n\s*if \(([\s\S]*?)\) \{/);
if (!mHide) { console.error('NG: hide rule not found'); process.exit(3); }
const isHidden = new Function('t', 'ev', 'today', 'parseDateStr', `return ${mHide[1].trim()};`);

const mSold = html.match(/if \(t\.soldout\) \{\s*\n\s*if \(([\s\S]*?)\) return "";/);
if (!mSold) { console.error('NG: soldout rule not found'); process.exit(3); }
const soldHidden = new Function('t', 'ev', 'today', 'parseDateStr', `return ${mSold[1].trim()};`);

const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);

const IDS = [809, 1052, 1812, 2084, 2728, 3154, 3765, 4203, 4324, 4941, 4978, 5014, 5577, 5643, 5731, 6187, 6195, 7434, 7466];

const out = [];
for (const id of IDS) {
  const ev = EVENTS.find(e => e.id === id);
  if (!ev) { out.push({ id, MISSING: true }); continue; }
  const ts = ev.tickets || [];
  const rows = ts.map(t => {
    let vis;
    if (t.soldout) vis = !soldHidden(t, ev, today, parseDateStr);
    else vis = !isHidden(t, ev, today, parseDateStr);
    return {
      type: t.type || '', date: t.date || null, startDate: t.startDate || null,
      soldout: !!t.soldout, saleEnded: !!t.saleEnded,
      saleUntilSoldOut: !!t.saleUntilSoldOut, saleEndUnknown: !!t.saleEndUnknown,
      url: t.url || '', visible: vis
    };
  });
  out.push({
    id, verified: ev.verified === true, artist: ev.artist || '', title: ev.title || '',
    genre: ev.genre || '', venue: ev.venue || '', area: ev.area || '',
    date: ev.date || '', dateLabel: ev.dateLabel || '',
    datePast: (ev.date || '') < TODAY_STR,
    links: ev.links || {},
    visibleCount: rows.filter(r => r.visible).length,
    ticketCount: rows.length,
    tickets: rows
  });
}
fs.writeFileSync('C:/Users/user/oshinavi/tmp/verify_del_0910.json', JSON.stringify(out, null, 1), 'utf8');
console.log('written', out.length);
