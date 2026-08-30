# e+の生HTMLから <dt>出演</dt><dd>…</dd> を丸ごと抜く（自前で再導出）
import re,sys,os,html,json
sys.stdout.reconfigure(encoding='utf-8')
IDS=[5989,5991,5994,5995,5998,5999,6001,6002,6005,6006,6008,6010,6011,6012,6015,6017,6020,6021,6023]
PAT=re.compile(r'<dt>\s*出演\s*</dt>\s*<dd>(.*?)</dd>',re.S)
out={}
for i in IDS:
    p=f'tmp/_agentB_cache/{i}.html'
    if not os.path.exists(p):
        out[i]=None; print(i,'キャッシュ無し'); continue
    h=open(p,encoding='utf-8',errors='replace').read()
    m=PAT.search(h)
    if not m:
        t=re.search(r'<title>(.*?)</title>',h,re.S)
        out[i]={'cast':None,'title':html.unescape(t.group(1)).replace('のチケット情報','|').split('|')[0].strip() if t else ''}
        print(f'{i}: 出演欄なし  title={out[i]["title"]}')
        continue
    raw=m.group(1)
    raw=re.sub(r'<br\s*/?>','',raw)          # 途中の改行タグは名前を割るだけなので除去
    raw=re.sub(r'<[^>]+>','',raw)
    v=html.unescape(raw).strip()
    v=re.sub(r'\s+',' ',v)
    out[i]={'cast':v,'title':''}
    print(f'{i}: {v}')
json.dump(out,open('tmp/_cast_0831.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
