import re,json
PB='https://t.pia.jp/pia/event/event.do?eventBundleCd='
e992={
 "id":992,
 "artist":"舞台『ハリー・ポッターと呪いの子』",
 "name":"舞台『ハリー・ポッターと呪いの子』",
 "date":"2026-12-27",
 "dateLabel":"2026年8月16日〜12月27日 東京 TBS赤坂ACTシアター",
 "venue":"TBS赤坂ACTシアター","prefecture":"東京","genre":"new","price":None,
 "links":{"rakuten":None,"lawson":None,"pia":PB+"b2669038","eplus":None},
 "tickets":[
   {"type":"一般発売（東京 8/16〜8/31公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21","url":PB+"b2669038"},
   {"type":"一般発売（東京 9/2〜9/30公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21","url":PB+"b2669039"},
   {"type":"一般発売（東京 10/1〜10/31公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21","url":PB+"b2669040"},
   {"type":"一般発売（東京 11/1〜11/29公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21","url":PB+"b2669041"},
   {"type":"一般発売（東京 12/1〜12/27公演）6/21 10:00発売","startDate":"2026-06-21","date":"2026-06-21","url":PB+"b2669042"}
 ],
 "longrun":True,"verified":True,"verifiedAt":"2026-06-19"
}
def fmt(o):
    s=json.dumps(o,ensure_ascii=False,indent=2)
    return '\n'.join('  '+ln for ln in s.split('\n'))
src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\n','\n').replace('\r\n','\n')
lines=text.split('\n')
def span(eid):
    pat=re.compile(r'^\s*"id":\s*'+str(eid)+r'\s*,')
    idx=next((i for i,l in enumerate(lines) if pat.match(l)),None)
    if idx is None:return None
    s=idx
    while lines[s].strip()!='{':s-=1
    oi=len(lines[s])-len(lines[s].lstrip())
    e=idx
    while e<len(lines):
        st=lines[e].strip();ind=len(lines[e])-len(lines[e].lstrip())
        if st in('}','},') and ind==oi and e>s:break
        e+=1
    return s,e
# delete 993-996 and replace 992 (process desc order)
ops=[]
for eid in [992,993,994,995,996]:
    sp=span(eid); ops.append((sp[0],sp[1],eid))
ops.sort(reverse=True)
for s,e,eid in ops:
    had=lines[e].strip()=='},'
    if eid in (993,994,995,996):
        del lines[s:e+1]
    else:
        blk=fmt(e992).split('\n')
        if had: blk[-1]+=','
        lines[s:e+1]=blk
text='\n'.join(lines)
# NEW_ORDER remove 993-996
m=re.search(r'const NEW_ORDER = \[([0-9,]*)\]',text)
ids=[int(x) for x in m.group(1).split(',') if x]
ids=[i for i in ids if i not in (993,994,995,996)]
text=re.sub(r'const NEW_ORDER = \[[0-9,]*\]','const NEW_ORDER = ['+','.join(map(str,ids))+']',text)
open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print('ハリポタ統合: 992に5枠・993-996削除 / NEW_ORDER',len(ids))
