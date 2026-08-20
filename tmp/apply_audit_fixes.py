import re,io

PIA='https://t.pia.jp/pia/event/event.do?eventCd='

fixes = {
 884: [
   {"type":"一般発売（東京 11/7公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27"},
 ],
 881: [
   {"type":"8次受付〔先行〕（新潟 9/12公演）〜6/22 11:00","date":"2026-06-22"},
   {"type":"一般発売（新潟 9/12公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27"},
 ],
 892: [
   {"type":"プレリザーブ（東京 10/9公演）6/20 10:00受付開始","startDate":"2026-06-20","date":"2026-06-20"},
   {"type":"一般発売（東京 10/9公演）7/18 10:00発売","startDate":"2026-07-18","date":"2026-07-18"},
 ],
 905: [
   {"type":"プレリザーブ（長野 9/13公演）〜6/28 23:59","date":"2026-06-28"},
   {"type":"一般発売（長野 9/13公演）7/11 10:00発売","startDate":"2026-07-11","date":"2026-07-11"},
 ],
 923: [
   {"type":"一般発売（東京 11/13公演）7/1 10:00発売","startDate":"2026-07-01","date":"2026-07-01"},
 ],
 933: [
   {"type":"一般発売（宮城 8/9公演）6/20 10:00発売","startDate":"2026-06-20","date":"2026-06-20"},
 ],
 935: [
   {"type":"一般発売（大阪 9/12公演）7/4 10:00発売","startDate":"2026-07-04","date":"2026-07-04","url":PIA+"2616646"},
   {"type":"一般発売（大阪 9/13公演）7/4 10:00発売","startDate":"2026-07-04","date":"2026-07-04","url":PIA+"2616646"},
   {"type":"一般発売（大阪 2DAYS通し）7/4 10:00発売","startDate":"2026-07-04","date":"2026-07-04","url":PIA+"2616645"},
 ],
 893: [
   {"type":"一般発売（宮城 9/19公演）〜9/18 23:59","date":"2026-09-18"},
 ],
 906: [
   {"type":"一般発売（愛知 7/29公演）〜7/13 23:59","date":"2026-07-13"},
 ],
 912: [
   {"type":"プレリザーブ先行（北海道 9/13公演）〜6/24 11:00","date":"2026-06-24"},
 ],
 913: [
   {"type":"プレリザーブ先行（新潟 10/16公演）〜6/29 11:00","date":"2026-06-29"},
   {"type":"プレリザーブ先行（石川 10/17公演）〜6/29 11:00","date":"2026-06-29"},
 ],
 926: [
   {"type":"先行抽選（長崎11/3・熊本11/5公演）〜6/24 23:59","date":"2026-06-24"},
 ],
 934: [
   {"type":"ぴあ独占3次先行（神奈川 10/24・10/25公演）〜6/30 23:59","date":"2026-06-30"},
 ],
 879: [
   {"type":"一般発売（栃木 11/29公演）〜11/28 23:59","date":"2026-11-28"},
 ],
}

KEY_ORDER=["type","startDate","date","saleUntilSoldOut","saleEndUnknown","url"]
def build_tickets(tks):
    import json
    out=["["]
    for i,t in enumerate(tks):
        out.append("      {")
        keys=[k for k in KEY_ORDER if k in t]
        for j,k in enumerate(keys):
            v=t[k]
            vs = json.dumps(v,ensure_ascii=False) if not isinstance(v,bool) else ("true" if v else "false")
            comma="," if j<len(keys)-1 else ""
            out.append(f'        "{k}": {vs}{comma}')
        out.append("      }"+("," if i<len(tks)-1 else ""))
    out.append("    ]")
    return "\n".join(out)

src=open('index.html',encoding='utf-8',newline='').read()
# detect newline
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')

def replace_tickets(text, eid, newarr):
    mi=re.search(rf'"id":\s*{eid},', text)
    if not mi: return text,False
    start=mi.end()
    tk=text.find('"tickets":', start)
    if tk<0: return text,False
    br=text.find('[', tk)
    depth=0;i=br
    while i<len(text):
        if text[i]=='[':depth+=1
        elif text[i]==']':
            depth-=1
            if depth==0:break
        i+=1
    end=i  # index of closing ]
    newblock=build_tickets(newarr)
    return text[:br]+newblock+text[end+1:],True

changed=[]
for eid,arr in fixes.items():
    text,ok=replace_tickets(text,eid,arr)
    changed.append((eid,ok))

out=text.replace('\n',nl)
open('index.html','w',encoding='utf-8',newline='').write(out)
print("nl=",repr(nl))
for eid,ok in changed:
    print(eid,"OK" if ok else "FAIL")
