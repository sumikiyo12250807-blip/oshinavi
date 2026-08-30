# -*- coding: utf-8 -*-
import re,io,sys,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
src=open('tools/pia_kw_search.py',encoding='utf-8').read()
ns={'__name__':'kwmod'}
exec(compile(src,'pia_kw_search','exec'),ns)
h=open('index.html',encoding='utf-8').read()
reg=set(re.findall(r'event(?:Bundle)?Cd=(\w+)',h))
import unicodedata
def n(s): return unicodedata.normalize('NFKC',s or '').replace(' ','').replace('　','').lower()
KWS=['ORCALAND','大森靖子','夕闇に誘いし漆黒の天使達','ビッケブランカ','mekakushe','kiki vivi lily','伊波杏樹','MYTH & ROID','Guiano','サラ・オレイン','SILENT SIREN','バブルガム・ブラザーズ']
for kw in KWS:
    try:
        hits=ns['search'](kw)
    except Exception as e:
        print(kw,'検索失敗',type(e).__name__); continue
    miss=[]
    for u,x in hits.items():
        m=re.search(r'event(?:Bundle)?Cd=(\w+)',u)
        if not m or m.group(1) in reg: continue
        if n(kw) not in n(x['title']): continue
        miss.append((x['status'],x['title'],x['perfdate'],x['venue'],u))
    print('=== %s : ヒット%d / 未登録かつ名前一致 %d'%(kw,len(hits),len(miss)))
    for z in miss[:12]: print('    ',' | '.join(z))
    time.sleep(2)
