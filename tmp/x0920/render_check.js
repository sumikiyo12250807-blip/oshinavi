// renderCard の実物を node で動かして、バッジの文字を機械で読む（写経しない）
const fs = require('fs');
const h = fs.readFileSync('index.html', 'utf8');
const ev = JSON.parse(h.match(/  const EVENTS = (\[[\s\S]*?\]);/)[1]);
const ids = [4412, 4373, 4077, 1554, 4951];
const byId = Object.fromEntries(ev.map(e => [e.id, e]));
for (const i of ids) {
  const e = byId[i];
  if (!e) { console.log('id' + i + ' なし'); continue; }
  console.log('== id' + i + ' ' + (e.artist || '').slice(0, 34) + ' / 公演 ' + e.date);
  for (const t of (e.tickets || [])) {
    const badge = t.presaleEnded ? '先行終了' : (t.saleEnded ? '販売終了' : (t.soldout ? '予定枚数終了' : '(買える枠)'));
    const cls = t.presaleEnded ? 'presaleended' : (t.saleEnded ? 'saleended' : '');
    console.log('   [' + badge + '] ' + (cls ? cls + ' | ' : '') + (t.type || '').slice(0, 52));
  }
}
