// renderCardの発売前/販売中判定を再現してテスト
function mkTest(nowStr){
  const today=new Date(nowStr); today.setHours(0,0,0,0);
  const now=new Date(nowStr);
  const parseDateStr=s=>{const[y,m,d]=s.split("-").map(Number);return new Date(y,m-1,d);};
  function saleStartPending(t){
    if(!t.startDate)return false;
    const sd=parseDateStr(t.startDate);
    if(sd>today)return true;
    if(sd<today)return false;
    const m=(t.type||"").match(/(\d{1,2}):(\d{2})/);
    if(!m)return false;
    const start=new Date(sd); start.setHours(+m[1],+m[2],0,0);
    return now<start;
  }
  function decide(t){
    if(t.saleUntilSoldOut)return"販売中(SUS)";
    if(saleStartPending(t))return"発売前";
    if(t.startDate&&parseDateStr(t.date)>=today)return"販売中";
    if(!t.startDate&&parseDateStr(t.date)>=today)return"販売中";
    return"終了";
  }
  return decide;
}
const presale={type:"一般発売（東京 8/22公演）7/4 10:00発売",date:"2026-07-04",startDate:"2026-07-04"};
const selling={type:"一般発売（東京 9/1公演）〜9/10 23:59",date:"2026-09-10"};
console.log("=== 6/21(発売日7/4より前) ===");
console.log(" 発売前チケット →",mkTest("2026-06-21T19:30:00")(presale),"(期待:発売前)");
console.log("=== 7/4 09:59(発売10:00直前) ===");
console.log(" 発売前チケット →",mkTest("2026-07-04T09:59:00")(presale),"(期待:発売前=本日発売)");
console.log("=== 7/4 10:01(発売時刻後) ===");
console.log(" 発売前チケット →",mkTest("2026-07-04T10:01:00")(presale),"(期待:販売中)");
console.log("=== 7/5(発売日翌日) ===");
console.log(" 発売前チケット →",mkTest("2026-07-05T08:00:00")(presale),"(期待:販売中)");
console.log("=== 販売中チケット(startDateなし) 9/1 ===");
console.log(" 販売中チケット →",mkTest("2026-09-01T12:00:00")(selling),"(期待:販売中)");
console.log("=== 時刻なし発売前 7/4当日0:30 ===");
console.log(" 時刻なし →",mkTest("2026-07-04T00:30:00")({type:"一般発売 7/4発売",date:"2026-07-04",startDate:"2026-07-04"}),"(期待:販売中=従来通り)");
