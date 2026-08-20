
const fs=require('fs');const html=fs.readFileSync('index.html','utf8');
const today=new Date(2026,6,19);const now=new Date(2026,6,19,20,0);
const pad=n=>String(n).padStart(2,'0');
const todayStr=`${today.getFullYear()}-${pad(today.getMonth()+1)}-${pad(today.getDate())}`;
function parseDateStr(s){const[y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d);}
eval(html.match(/(function saleStartPending\(t\) \{[\s\S]*?\n  \})/)[1]);
const EVENTS=JSON.parse(html.match(/const EVENTS\s*=\s*(\[[\s\S]*?\]);/)[1]);
eval(html.match(/const SORT_PRESALE[^\n]*/)[0].replace('const ','var '));
eval(html.match(/(const classify = \(ev\) => \{[\s\S]*?\n    \};)/)[1].replace('const classify =','var classify ='));
eval(html.match(/(EVENTS\.sort\(\(a, b\) => \{[\s\S]*?\n  \}\);)/)[1]);
let prev='';const out=[];let n=0;
for(const ev of EVENTS){
  const c=classify(ev); if(c.rank!==0) break;
  const tag=c.kind===0?'[発売開始]':'[締切]  ';
  const line=`${c.key} ${tag}`;
  if(line!==prev){ out.push(`${c.key}  ${tag}`); prev=line; if(++n>=8) break; }
}
fs.writeFileSync('tmp/_steps.txt', out.join('\n'), 'utf8');
