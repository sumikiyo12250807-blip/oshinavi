// ① 対象19件が「9/9以前公演」の全部か（他に取り残しが無いか）
// ② id5014 の全生データを確認
const fs = require('fs');
const html = fs.readFileSync('C:/Users/user/oshinavi/index.html', 'utf8');
const EVENTS = JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);
const IDS = new Set([809,1052,1812,2084,2728,3154,3765,4203,4324,4941,4978,5014,5577,5643,5731,6187,6195,7434,7466]);
const TODAY = '2026-09-10';
const past = EVENTS.filter(e => e.verified === true && (e.date || '') && e.date < TODAY);
const notListed = past.filter(e => !IDS.has(e.id)).map(e => `id${e.id} 公演${e.date} ${e.artist}`);
const out = {
  総エントリ数: EVENTS.length,
  verified済み公演日が過去: past.length,
  対象19件に入っていない過去公演: notListed,
  id5014生データ: EVENTS.find(e => e.id === 5014)
};
fs.writeFileSync('C:/Users/user/oshinavi/tmp/verify_del_0910c.json', JSON.stringify(out, null, 1), 'utf8');
console.log('ok');
