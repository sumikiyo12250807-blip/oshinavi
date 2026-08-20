// renderCard のステータス判定を index.html から写経して検証（today=2026-07-09固定）。
const today = new Date(2026, 6, 9); today.setHours(0,0,0,0);
function parseDateStr(str){ const [y,m,d]=str.split("-").map(Number); return new Date(y,m-1,d); }
function daysFrom(dateStr){ return Math.round((parseDateStr(dateStr)-today)/86400000); }
function saleStartPending(t, now){
  if(!t.startDate) return false;
  const sd = parseDateStr(t.startDate);
  if(sd>today) return true;
  if(sd<today) return false;
  const m=(t.type||"").match(/(\d{1,2}):(\d{2})/);
  if(!m) return false;
  const start=new Date(sd); start.setHours(+m[1],+m[2],0,0);
  return now<start;
}
function status(t, now){
  let status,label,displayDate;
  if(t.saleUntilSoldOut){ status="selling"; label="販売中"; displayDate=null; }
  else if(saleStartPending(t,now)){
    const sdiff=daysFrom(t.startDate);
    status=sdiff<=7?"urgent":sdiff<=31?"soon":"normal";
    label=sdiff===0?"本日発売":sdiff===1?"明日発売":`発売開始まで あと ${sdiff} 日`;
    displayDate=t.startDate;
  } else if(t.startDate && parseDateStr(t.date)>=today){
    if(t.startDate===t.date){ status="urgent"; label="本日発売"; displayDate=t.startDate; }
    else { status="selling"; label="販売中"; displayDate=t.date; }
  } else if(!t.startDate && parseDateStr(t.date)>=today){
    status="selling"; label="販売中"; displayDate=t.date;
  } else { status="passed"; label="終了"; displayDate=t.date; }
  return {status,label,displayDate};
}
const AM9 = new Date(2026,6,9,9,0), AM11 = new Date(2026,6,9,11,0);
const cases = [
  ["本日発売・締切無し・発売時刻前(9:00)", {type:"一般発売（山口 11/17公演）7/9 10:00発売",startDate:"2026-07-09",date:"2026-07-09"}, AM9, "本日発売"],
  ["本日発売・締切無し・発売時刻後(11:00)＝修正対象", {type:"一般発売（山口 11/17公演）7/9 10:00発売",startDate:"2026-07-09",date:"2026-07-09"}, AM11, "本日発売"],
  // 受付中(実データ): startDate無し・type「〜締切」
  ["受付中・締切あり・startDate無し", {type:"一般発売〜11/24 23:59",date:"2026-11-24"}, AM11, "販売中"],
  // 発売前レンジ修正後・発売日today・発売時刻後: startDate=発売日/date=END(≠)/type=発売時刻 → 販売中〜END
  ["発売前レンジ・発売日today・発売時刻後(END取込済)", {type:"先行（東京 8/1公演）7/9 10:00発売",startDate:"2026-07-09",date:"2026-08-01"}, AM11, "販売中"],
  ["発売前(将来7/15)", {type:"一般発売 7/15 10:00発売",startDate:"2026-07-15",date:"2026-07-15"}, AM11, "発売開始まで あと 6 日"],
];
let ok=0;
for(const [name,t,now,exp] of cases){
  const r=status(t,now);
  const pass=r.label===exp;
  if(pass) ok++;
  console.log(`${pass?"OK":"NG"} | ${name} => label="${r.label}" status=${r.status} date=${r.displayDate}` + (pass?"":`  期待:"${exp}"`));
}
console.log(`\n=== ${ok}/${cases.length} passed ===`);
