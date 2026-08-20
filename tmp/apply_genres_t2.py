import re
gmap={}
for line in open('tmp/genre_table_theater2.tsv',encoding='utf-8').read().splitlines():
    if not line.strip(): continue
    i,g,name=line.split('\t'); gmap[int(i)]=g
lines=open('index.html',encoding='utf-8',newline='').read().split('\r\n')
out=[];cur=None;applied=0
id_re=re.compile(r'^\s*"id":\s*(\d+),')
for ln in lines:
    mm=id_re.match(ln)
    if mm: cur=int(mm.group(1))
    if ln.strip().startswith('"genre": "new"') and cur in gmap:
        ind=ln[:len(ln)-len(ln.lstrip())]
        comma=',' if ln.rstrip().endswith(',') else ''
        out.append(f'{ind}"genre": "{gmap[cur]}"{comma}'); applied+=1; continue
    out.append(ln)
open('index.html','w',encoding='utf-8',newline='').write('\r\n'.join(out))
print('genre applied:',applied)
