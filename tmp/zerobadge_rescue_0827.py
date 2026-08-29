# -*- coding: utf-8 -*-
"""バッジ0（買える枠ゼロ）のエントリを、アーティスト名でぴあを総ざらいして後継URLを探す。
   登録してあるeventCdには一般発売が無く、別eventCd/bundleに生きている型を拾う。
   ⚠️読むだけ。データは触らない。候補を tmp/zerobadge_cand_0827.md に出す。"""
import json,re,io,sys,subprocess,time
sys.stdout.reconfigure(encoding='utf-8')
IDS=[int(x) for x in sys.argv[1].split(',')]
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV={e['id']:e for e in json.loads(m.group(2))}
have=set(re.findall(r'event(?:Bundle)?Cd=(\w+)',h))
o=io.open('tmp/zerobadge_cand_0827.md','w',encoding='utf-8')
o.write('# バッジ0の後継URL探索（%d件・読むだけ）\n\n'%len(IDS))
found=0
for n,i in enumerate(IDS,1):
    e=EV.get(i)
    if not e: continue
    kw=e.get('artist','')
    out='tmp/_kw_%d.txt'%i
    r=subprocess.run([sys.executable,'tools/pia_kw_search.py',kw,'--out',out],
                     capture_output=True,text=True,encoding='utf-8',timeout=300)
    try: t=io.open(out,encoding='utf-8').read()
    except Exception: t=''
    blocks=re.split(r'\n(?=\[)',t)
    hits=[]
    for b in blocks:
        mu=re.search(r'URL\s+:\s+(\S+)',b)
        if not mu: continue
        codes=set(re.findall(r'event(?:Bundle)?Cd=(\w+)',mu.group(1)))
        if codes & have: continue     # すでに登録済みのコードは除く
        hits.append(b.strip())
    o.write('## id=%d %s （公演日 %s）\n- 登録URL: %s\n'%(i,kw,e.get('date'),(e.get('links') or {}).get('pia')))
    if hits:
        found+=1
        for b in hits[:6]:
            o.write('```\n%s\n```\n'%b[:600])
    else:
        o.write('- 🔎ぴあに未登録の枠は見つからなかった\n')
    o.write('\n')
    print('[%d/%d] id=%d hits=%d'%(n,len(IDS),i,len(hits)))
    time.sleep(1.0)
o.close()
print('後継候補が見つかったエントリ',found)
