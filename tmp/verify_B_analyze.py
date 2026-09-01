# -*- coding: utf-8 -*-
import os,re,io,sys,html,json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT=r'C:\Users\user\oshinavi'
D=os.path.join(ROOT,'tmp','verify_B_html')
raw=json.load(open(os.path.join(ROOT,'tmp','verify_B_0902_raw.json'),encoding='utf-8'))
lines=[l.rstrip('\n') for l in open(os.path.join(ROOT,'tmp','verify_list_B_0902.txt'),encoding='utf-8') if l.strip()]
out=[]
for ln in lines:
    p=ln.split('\t')
    if len(p)<2: continue
    eid,url=p[0].strip(),p[1].strip()
    h=open(os.path.join(D,eid+'.html'),encoding='utf-8').read()
    m=re.search(r'<title>(.*?)</title>',h,re.S)
    t=html.unescape(m.group(1)).strip() if m else ''
    name=re.sub(r'\s*\|\s*チケットぴあ.*$','',t)
    genre=''
    mg=re.search(r'チケットぴあ\[(.*?)\]',t)
    if mg: genre=mg.group(1)
    rls=sorted(set(re.findall(r'[?&](?:lot)?[Rr]lsCd=(\w+)',h)))
    cards=h.count('ticketSalesCard-2024__status')
    # other event links on page (bundle detection)
    evlinks=sorted(set(re.findall(r'event\.do\?eventCd=(\d+)',h)))
    rows=raw[eid].get('rows',[])
    buy=[r for r in rows if r['state'] in ('受付中','発売前')]
    out.append(dict(id=eid,url=url,name=name,genre=genre,rls=rls,cards=cards,evlinks=evlinks,rows=rows,buy=buy))
json.dump(out,open(os.path.join(ROOT,'tmp','verify_B_0902_merged.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
for o in out:
    print('=== %s | %s | [%s]' % (o['id'], o['name'], o['genre']))
    print('   全%d券種 買える%d / rlsCd uniq=%d / cards(HTML)=%d / 他eventCdリンク=%d' % (len(o['rows']),len(o['buy']),len(o['rls']),o['cards'],len(o['evlinks'])))
    for r in o['rows']:
        pr=r['perfdate']+('〜'+r['perf_end'] if r['perf_end']!=r['perfdate'] else '')
        print('   [%s] %s | %s | %s | %s | %s | %s' % (r['state'],pr,r['pref'],r['venue'],r['title'],r['statustext'],r['when']))
