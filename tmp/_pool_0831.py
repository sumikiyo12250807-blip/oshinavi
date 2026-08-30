import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
m=re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S)
ev=json.loads(m.group(1))
new=[e for e in ev if e.get('genre')=='new']
print('total events',len(ev),'new pool',len(new))
from collections import Counter
def src(e):
    u=json.dumps(e,ensure_ascii=False)
    if 'eplus.jp' in u: return 'eplus'
    if 't.pia.jp' in u: return 'pia'
    if 'rakuten' in u: return 'rakuten'
    return 'other'
print(Counter(src(e) for e in new))
ids=[e['id'] for e in new]
print('id range',min(ids),max(ids))
open('tmp/_pool_ids_0831.txt','w').write(','.join(str(i) for i in ids))
# group by contiguous
print(Counter(e.get('_genre','') for e in new).most_common(20))
