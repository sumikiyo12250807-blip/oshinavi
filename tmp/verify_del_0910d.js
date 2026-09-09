// 対象外に残っていた過去公演2件 (1904, 2866) の生き枠を実物の条件式で数える
const fs = require('fs');
const html = fs.readFileSync('C:/Users/user/oshinavi/index.html', 'utf8');
const today = new Date(2026, 8, 10);
function parseDateStr(s) { const [y, m, d] = String(s).split('-').map(Number); return new Date(y, m - 1, d); }
const isHidden = new Function('t', 'ev', 'today', 'parseDateStr', 'return ' + html.match(/\/\/ 販売終了したチケットは表示しない[\s\S]*?\n\s*if \(([\s\S]*?)\) \{/)[1].trim() + ';');
const soldHidden = new Function('t', 'ev', 'today', 'parseDateStr', 'return ' + html.match(/if \(t\.soldout\) \{\s*\n\s*if \(([\s\S]*?)\) return "";/)[1].trim() + ';');
const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);
const out = [1904, 2866].map(id => {
  const ev = EVENTS.find(e => e.id === id);
  const rows = (ev.tickets || []).map(t => ({
    type: t.type, date: t.date || null, startDate: t.startDate || null,
    soldout: !!t.soldout, saleEnded: !!t.saleEnded, saleUntilSoldOut: !!t.saleUntilSoldOut,
    saleEndUnknown: !!t.saleEndUnknown,
    visible: t.soldout ? !soldHidden(t, ev, today, parseDateStr) : !isHidden(t, ev, today, parseDateStr)
  }));
  return { id, artist: ev.artist, date: ev.date, dateLabel: ev.dateLabel, links: ev.links, visibleCount: rows.filter(r => r.visible).length, tickets: rows };
});
fs.writeFileSync('C:/Users/user/oshinavi/tmp/verify_del_0910d.json', JSON.stringify(out, null, 1), 'utf8');
console.log('ok');
