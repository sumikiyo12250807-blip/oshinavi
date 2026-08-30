import json,re,sys,unicodedata
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
def norm(x):
    x=unicodedata.normalize('NFKC',x or '')
    return re.sub(r'[\s　・･/／「」『』【】（）()\[\]~〜\-–—!！?？,、。.]','',x).lower()
names=[(e['id'],e.get('artist',''),norm(e.get('artist','')),e.get('date','')) for e in ev]
rows=[]
for path in ('tmp/active2_hold_0830.md','tmp/engeki_hold_0830.md'):
    for ln in open(path,encoding='utf-8'):
        m=re.match(r'\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([\d-]+)\s*\|\s*(.+?)\s*\|\s*(\S+)\s*\|',ln)
        if not m: continue
        pid,nm,dt,pref,url=m.groups()
        n=norm(nm)
        hits=[]
        for i,a,na,d in names:
            if not na: continue
            if na==n or (len(na)>=4 and na in n) or (len(n)>=4 and n in na):
                hits.append((i,a,d))
        rows.append((pid,nm,dt,pref,url,hits))
for r in rows:
    print(f"[{r[0]}] {r[1]}  {r[2]} {r[3]}")
    print(f"    {r[4]}")
    if r[5]:
        for i,a,d in r[5][:6]: print(f"    ↔ 既存 id={i} {a} ({d})")
    else:
        print("    ↔ 既存ヒット無し")
