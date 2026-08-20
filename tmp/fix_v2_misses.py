import re,json
KEY=["type","startDate","date","saleUntilSoldOut","saleEndUnknown","url"]
def build(tks):
    out=["["]
    for i,t in enumerate(tks):
        out.append("      {")
        ks=[k for k in KEY if k in t]
        for j,k in enumerate(ks):
            v=t[k]; vs=("true" if v else "false") if isinstance(v,bool) else json.dumps(v,ensure_ascii=False)
            out.append(f'        "{k}": {vs}'+("," if j<len(ks)-1 else ""))
        out.append("      }"+("," if i<len(tks)-1 else ""))
    out.append("    ]")
    return "\n".join(out)

fixes={
 1006:[
   {"type":"一般発売（兵庫 8/2朝席公演）〜8/1 23:59","date":"2026-08-01"},
   {"type":"一般発売（兵庫 8/7夜席公演）〜8/6 23:59","date":"2026-08-06"},
   {"type":"一般発売（兵庫 8/8夜席公演）〜8/7 23:59","date":"2026-08-07"},
   {"type":"一般発売（兵庫 8/9夜席公演）〜8/8 23:59","date":"2026-08-08"},
   {"type":"一般発売（兵庫 8/16朝席公演）〜8/15 23:59","date":"2026-08-15"},
   {"type":"一般発売（兵庫 8/19夜席公演）〜8/18 23:59","date":"2026-08-18"},
   {"type":"一般発売（兵庫 8/23夜席公演）6/23 12:00発売","startDate":"2026-06-23","date":"2026-06-23"},
   {"type":"一般発売（兵庫 8/30夜席公演）〜8/29 23:59","date":"2026-08-29"},
 ],
 1016:[
   {"type":"プリセール（宮城 10/31公演）〜6/24 23:59","date":"2026-06-24"},
   {"type":"一般発売（宮城 10/31公演）6/26 10:00発売","startDate":"2026-06-26","date":"2026-06-26"},
 ],
 1025:[
   {"type":"2次受付（静岡 10/17・10/18公演）〜6/21 23:59","date":"2026-06-21"},
   {"type":"一般発売（静岡 10/17・10/18公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27"},
 ],
 1026:[
   {"type":"オフィシャル先行（宮城 8/23公演）〜6/21 23:59","date":"2026-06-21"},
   {"type":"一般発売（宮城 8/23公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27"},
 ],
 1032:[
   {"type":"一般発売（神奈川 9/23公演）6/27 10:00発売","startDate":"2026-06-27","date":"2026-06-27"},
 ],
}

src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')
def replace_tickets(text,eid,arr):
    mi=re.search(rf'"id":\s*{eid},',text)
    tk=text.find('"tickets":',mi.end()); br=text.find('[',tk)
    depth=0;i=br
    while i<len(text):
        if text[i]=='[':depth+=1
        elif text[i]==']':
            depth-=1
            if depth==0:break
        i+=1
    return text[:br]+build(arr)+text[i+1:]
for eid,arr in fixes.items():
    text=replace_tickets(text,eid,arr)
open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print("fixed:",sorted(fixes))
