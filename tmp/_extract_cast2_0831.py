import re,sys,os,html,json
sys.stdout.reconfigure(encoding='utf-8')
IDS=[5989,5991,5994,5995,5998,5999,6001,6002,6005,6006,6008,6010,6011,6012,6015,6017,6020,6021,6023]
PAT=re.compile(r'<dt>\s*出演\s*</dt>\s*<dd>(.*?)</dd>',re.S)
out={}
for i in IDS:
    p=f'tmp/_agentB_cache/{i}.html'
    h=open(p,encoding='utf-8',errors='replace').read()
    t=re.search(r'<title>(.*?)</title>',h,re.S)
    title=html.unescape(t.group(1)).split('のチケット情報')[0].strip() if t else ''
    m=PAT.search(h)
    if not m:
        out[i]={'raw':None,'title':title}; print(f'--- {i} 出演欄なし / title={title}'); continue
    raw=m.group(1)
    raw=re.sub(r'<br\s*/?>','\u0001',raw)   # 改行は区切りとして温存
    raw=re.sub(r'<[^>]+>','',raw)
    v=html.unescape(raw)
    parts=[re.sub(r'\s+',' ',x).strip(' ･・/／、,') for x in re.split(r'[\u0001/／]',v)]
    parts=[x for x in parts if x]
    out[i]={'raw':parts,'title':title}
    print(f'--- {i} / title={title}')
    for x in parts: print('     ',x[:90])
json.dump(out,open('tmp/_cast_0831.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
