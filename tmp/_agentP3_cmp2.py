# -*- coding: utf-8 -*-
import json,io,sys,re,unicodedata
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/_agentP3_result.json',encoding='utf-8'))
def np(p): return re.sub(r'(都|道|府|県)$','',p)
ok=0; bad=[]
for r in d:
    iss=[]
    if str(r['n_buy'])!=str(r['reg_cnt']): iss.append(('買える枠数',r['reg_cnt'],f"{r['n_buy']} (受付中{r['n_active']}/発売前{r['n_before']}/終了{r['n_end']})"))
    if r['maxdate_all'] and r['maxdate_all']!=r['reg_date']: iss.append(('千秋楽',r['reg_date'],r['maxdate_all']))
    if not r['maxdate_all']: iss.append(('千秋楽',r['reg_date'],'公演日読めず'))
    regp=set(re.split(r'[・,、]',r['reg_pref'])); piap={np(x) for x in r['prefs_all'] if x}
    if piap and regp!=piap: iss.append(('県',r['reg_pref'],'・'.join(sorted(piap))))
    if not piap: iss.append(('県',r['reg_pref'],'ぴあ券種カードに県表記なし'))
    if iss: bad.append((r,iss))
    else: ok+=1
print('一致',ok,'/ ズレ',len(bad))
for r,iss in bad:
    print(f"\n{r['id']} {r['reg_name']}")
    for a,b,c in iss: print(f"   {a}: 登録={b} / ぴあ={c}")
    for c in r['cards']:
        print(f"      [{c['state']}] {c['statustext']} | {c['perfdate']}~{c['perf_end']} | {c['pref']} {c['venue']} | {c['title']} | {c['when']}")
