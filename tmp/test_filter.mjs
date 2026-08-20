// 2026-07-01 を今日として実機ロジックを再現
const today = new Date(2026,6,1); today.setHours(0,0,0,0);
const now = new Date(2026,6,1,12,0,0);
function parseDateStr(s){const[y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d);}
function daysFrom(s){return Math.round((parseDateStr(s)-today)/86400000);}
function saleStartPending(t){
  if(!t.startDate)return false;
  const sd=parseDateStr(t.startDate);
  if(sd>today)return true;
  if(sd<today)return false;
  const m=(t.type||"").match(/(\d{1,2}):(\d{2})/);
  if(!m)return false;
  const start=new Date(sd);start.setHours(+m[1],+m[2],0,0);
  return now<start;
}
function releaseKind(t){
  if(t.soldout)return null;
  if(saleStartPending(t)){const d=daysFrom(t.startDate);return d<=7?"urgent":d<=31?"soon":"normal";}
  return null;
}
function eventReleaseStatus(ev){
  const kinds=(ev.tickets||[]).map(releaseKind).filter(Boolean);
  for(const p of["urgent","soon","normal"])if(kinds.includes(p))return p;
  return null;
}
function match(ev,activeStatus){
  const rel=eventReleaseStatus(ev);
  return activeStatus==="all"
    ||(activeStatus==="urgent"&&rel==="urgent")
    ||(activeStatus==="soon"&&(rel==="urgent"||rel==="soon"))
    ||(activeStatus==="upcoming"&&rel==="normal");
}
const cases=[
 ["発売前・今週(7/4発売)", {tickets:[{type:"一般発売 7/4 10:00発売",startDate:"2026-07-04",date:"2026-07-04"}]}],
 ["発売前・今月(7/20発売)", {tickets:[{type:"一般発売 7/20発売",startDate:"2026-07-20",date:"2026-07-20"}]}],
 ["発売前・先(8/20発売)",   {tickets:[{type:"一般発売 8/20発売",startDate:"2026-08-20",date:"2026-08-20"}]}],
 ["★販売中・今週締切(終了7/3)", {tickets:[{type:"一般発売",date:"2026-07-03"}]}],
 ["★販売中・開始済継続(start過去/終了未来)", {tickets:[{type:"一般発売",startDate:"2026-06-20",date:"2026-09-01"}]}],
];
console.log("ケース".padEnd(30),"今週発売  今月発売  先行受付前");
for(const [name,ev] of cases){
  console.log(name.padEnd(28),
    (match(ev,"urgent")?"✓":"・").padEnd(9),
    (match(ev,"soon")?"✓":"・").padEnd(9),
    (match(ev,"upcoming")?"✓":"・"));
}
