import json,re,sys
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
m=re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S)
ev=json.loads(m.group(1))
new=[e for e in ev if e.get('genre')=='new']
def src(e):
    u=json.dumps(e,ensure_ascii=False)
    if 'eplus.jp' in u: return 'eplus'
    if 't.pia.jp' in u: return 'pia'
    return 'other'
# contiguous runs by source
runs=[]
for e in sorted(new,key=lambda x:x['id']):
    s2=src(e)
    if runs and runs[-1][0]==s2 and e['id']-runs[-1][2]<=6:
        runs[-1][2]=e['id']; runs[-1][3]+=1
    else:
        runs.append([s2,e['id'],e['id'],1])
for r in runs: print(f"{r[0]:8} {r[1]}-{r[2]}  {r[3]}件")
