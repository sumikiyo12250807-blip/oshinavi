import json,re
e=json.load(open('tmp/out1048.json',encoding='utf-8'))[0]
g=e.pop('_genre','classic'); e['genre']='new'
print('1048 _genre =',g)
def fmt(o):
    s=json.dumps(o,ensure_ascii=False,indent=2);return '\n'.join('  '+l for l in s.split('\n'))
src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n');lines=text.split('\n')
pat=re.compile(r'^\s*"id":\s*1048\s*,')
idx=next(i for i,l in enumerate(lines) if pat.match(l))
s=idx
while lines[s].strip()!='{':s-=1
oi=len(lines[s])-len(lines[s].lstrip());en=idx
while en<len(lines):
    st=lines[en].strip();ind=len(lines[en])-len(lines[en].lstrip())
    if st in('}','},') and ind==oi and en>s:break
    en+=1
had=lines[en].strip()=='},'
blk=fmt(e).split('\n')
if had:blk[-1]+=','
lines[s:en+1]=blk
open('index.html','w',encoding='utf-8',newline='').write('\n'.join(lines).replace('\n',nl))
print('1048 replaced')
