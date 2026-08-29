# -*- coding: utf-8 -*-
"""後継候補のうち「登録エントリと同じ公演日」のものだけに絞る。
   同じアーティストの別公演を後継と誤認しないため。"""
import json,re,io,sys,datetime
sys.stdout.reconfigure(encoding='utf-8')
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV={e['id']:e for e in json.loads(m.group(2))}
txt=io.open('tmp/zerobadge_cand_0827.md',encoding='utf-8').read()
secs=re.split(r'\n(?=## id=)',txt)
o=io.open('tmp/zerobadge_match_0827.md','w',encoding='utf-8')
o.write('# バッジ0の後継候補（登録の公演日と一致したものだけ）\n\n')
nmatch=0; nother=0
for s in secs:
    mi=re.match(r'## id=(\d+)',s)
    if not mi: continue
    i=int(mi.group(1)); e=EV.get(i)
    if not e: continue
    d=e.get('date','')                    # YYYY-MM-DD（千秋楽）
    y,mo,da=d.split('-')
    pat='%s/%d/%d'%(y,int(mo),int(da))
    blocks=re.findall(r'```\n(.*?)\n```',s,re.S)
    hit=[b for b in blocks if pat in b]
    if hit:
        nmatch+=1
        o.write('## id=%d %s （登録の公演日 %s）\n'%(i,e.get('artist'),d))
        o.write('- 登録URL: %s\n'%((e.get('links') or {}).get('pia')))
        for b in hit: o.write('```\n%s\n```\n'%b[:500])
        o.write('\n')
    elif blocks:
        nother+=1
print('公演日が一致した後継候補: %d件／別公演だけ見つかった: %d件'%(nmatch,nother))
o.close()
