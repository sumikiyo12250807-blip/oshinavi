import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
m=re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S)
ev=json.loads(m.group(1))
new=[e for e in ev if e.get('genre')=='new']
out=[]
for e in sorted(new,key=lambda x:x['id']):
    g=e.get('_genre','') or ''
    sub=e.get('_piaSub','') or ''
    u=''
    if e.get('links'):
        for k in ('pia','eplus','rakuten','official'):
            if e['links'].get(k): u=e['links'][k]; break
    out.append({'id':e['id'],'artist':e.get('artist',''),'title':e.get('title',''),'date':e.get('date',''),
                'pref':e.get('prefecture',''),'_genre':g,'_piaSub':sub,'url':u,'tickets':len(e.get('tickets',[]))})
json.dump(out,open('tmp/_pool_table_0831.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
from collections import Counter
print(Counter(o['_piaSub'] for o in out).most_common(40))
print('no _genre:',sum(1 for o in out if not o['_genre']))
