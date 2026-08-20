import re, json
src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',text,re.S)
data=json.loads(m.group(1))

def fixdates(s):
    prev=None
    while prev!=s:
        prev=s
        s=re.sub(r'(\d{1,2})/(\d{1,2})([・〜])(\d{1,2})(?![\d/])', r'\1/\2\3\1/\4', s)
    return s

repls=[]
for e in data:
    for t in e.get('tickets',[]):
        ty=t['type']; nty=fixdates(ty)
        if nty!=ty:
            repls.append(('"type": "'+ty+'"','"type": "'+nty+'"'))

cnt=0; nf=0
for old,new in repls:
    if old in text:
        text=text.replace(old,new); cnt+=1
    else:
        nf+=1
open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print('略記→完全形 置換:',cnt,'件  (not found',nf,')')
