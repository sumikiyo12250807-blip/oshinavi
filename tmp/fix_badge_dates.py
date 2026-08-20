import re, json

src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')

m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',text,re.S)
data=json.loads(m.group(1))
new_ids={e['id'] for e in data if e.get('genre')=='new'}

def fixdates(s):
    prev=None
    while prev!=s:
        prev=s
        # M/D[・〜]D(day without month) -> add month to 2nd
        s=re.sub(r'(\d{1,2})/(\d{1,2})([・〜])(\d{1,2})(?![\d/])', r'\1/\2\3\1/\4', s)
    return s

# collect replacements (only within new-pool entries' ticket types & dateLabel)
repls=[]  # (old, new)
for e in data:
    if e['id'] not in new_ids: continue
    # dateLabel
    dl=e.get('dateLabel','')
    ndl=fixdates(dl)
    if ndl!=dl:
        repls.append(('"dateLabel": "'+dl+'"','"dateLabel": "'+ndl+'"'))
    for t in e.get('tickets',[]):
        ty=t['type']; nty=fixdates(ty)
        # 966 喜楽館: 昼席 badges lack 公演 keyword -> insert 公演
        if e['id']==966 and '昼席' in nty and '公演' not in nty:
            nty=nty.replace('昼席）','公演）昼席')
        if nty!=ty:
            repls.append(('"type": "'+ty+'"','"type": "'+nty+'"'))

cnt=0
for old,new in repls:
    if old in text:
        text=text.replace(old,new); cnt+=1
    else:
        print('NOT FOUND:',old)

open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print('置換',cnt,'件')
for o,n in repls[:40]:
    print('  ',o.split('": "')[1][:-1],'=>',n.split('": "')[1][:-1])
