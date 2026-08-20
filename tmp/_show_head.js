
const fs=require('fs');const html=fs.readFileSync('index.html','utf8');
const today=new Date(2026,6,19);const now=new Date(2026,6,19,19,40);
const pad=n=>String(n).padStart(2,'0');
const todayStr=`${today.getFullYear()}-${pad(today.getMonth()+1)}-${pad(today.getDate())}`;
function parseDateStr(s){const[y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d);}
eval(html.match(/(function saleStartPending\(t\) \{[\s\S]*?\n  \})/)[1]);
const EVENTS=JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);
eval(html.match(/const SORT_PRESALE[^\n]*/)[0].replace('const ','var '));
eval(html.match(/(const classify = \(ev\) => \{[\s\S]*?\n    \};)/)[1].replace('const classify =','var classify ='));
eval(html.match(/(EVENTS\.sort\(\(a, b\) => \{[\s\S]*?\n  \}\);)/)[1]);
for(const ev of EVENTS.slice(0,20)){
  const c=classify(ev);
  // カードに出る日付＝その枠の締切(sub)
  console.log(`${c.kind===0?'本日発売/発売開始':'販売中'}  表示日付=${c.sub}  ${(ev.name||'').slice(0,30)}`);
}
