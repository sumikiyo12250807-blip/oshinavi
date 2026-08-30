# -*- coding: utf-8 -*-
import json,io,sys,re,unicodedata
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/_agentP3_result.json',encoding='utf-8'))
def norm(s):
    s=unicodedata.normalize('NFKC',s or '')
    return re.sub(r'[\s　・･!！?？\-‐―ー~〜\'"”“’‘,、。/／\[\]（）()【】<>＜＞]','',s).lower()
for r in d:
    if r['status']!='OK': print(r['id'],'FETCH_FAIL'); continue
    issues=[]
    if str(r['n_buy'])!=str(r['reg_cnt']): issues.append(f"枠数 登録{r['reg_cnt']} / ぴあ買える{r['n_buy']} (受付中{r['n_active']}/発売前{r['n_before']}/終了{r['n_end']} 全{r['n_all']})")
    md=r['maxdate_all']
    if md and md!=r['reg_date']: issues.append(f"千秋楽 登録{r['reg_date']} / ぴあ最大{md} (買える枠内最大{r['maxdate_buy']})")
    if not md: issues.append("千秋楽 ぴあ公演日読めず")
    regp=set(re.split(r'[・,、]',r['reg_pref']))
    piap=set(r['prefs_all'])
    if regp!=piap: issues.append(f"県 登録{r['reg_pref']} / ぴあ{'・'.join(sorted(piap))}")
    nn=norm(r['reg_name']); pn=norm(r['pia_name'])
    if nn not in pn and pn not in nn: issues.append(f"名前 登録『{r['reg_name']}』/ ぴあ『{r['pia_name']}』")
    print(f"### {r['id']} | {r['reg_name']} | genre={r['genre']} | crumbs={'>'.join(r['crumbs'][1:])}")
    for i in issues: print('   -',i)
    if not issues: print('   OK')
