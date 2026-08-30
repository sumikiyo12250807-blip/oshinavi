# -*- coding: utf-8 -*-
import re, io, sys, os, json, html as _html, unicodedata
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
OUT='tmp/_agentP1_html'
def txt(s):
    return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
def parse(h):
    items=re.split(r'(?=<li class="ticketSalesList-2024__item)',h)
    rows=[]
    for it in items:
        if 'ticketSalesCard-2024__status' not in it: continue
        m_url=re.search(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"',it)
        m_title=re.search(r'__title">(.*?)</p>',it,re.S)
        m_place=re.search(r'__place"[^>]*>(.*?)</span>',it,re.S)
        _dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it)
        m_stat=re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)',it,re.S)
        m_sdate=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>',it,re.S)
        m_region=re.search(r'__region">(.*?)</span>',it,re.S)
        st=txt(m_stat.group(2)) if m_stat else ''
        cls=m_stat.group(1) if m_stat else ''
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|販売期間終了|終了しました|結果発表)',st): state='受付終了'
        elif cls=='is-active' or re.search(r'(販売期間中|受付中|発売中|販売中|発売初日|本日発売)',st): state='受付中'
        elif cls=='is-before' or '発売前' in st or 'まもなく' in st: state='発売前'
        else: state='受付終了'
        rows.append(dict(pd=_dts[0] if _dts else '', pe=_dts[-1] if _dts else '',
            st=st, cls=cls, venue=txt(m_place.group(1)) if m_place else '',
            pref=txt(m_region.group(1)) if m_region else '',
            title=txt(m_title.group(1)) if m_title else '', state=state,
            when=txt(m_sdate.group(1)) if m_sdate else '',
            url=m_url.group(1) if m_url else ''))
    seen=set(); u=[]
    for r in rows:
        k=(r['pd'],r['pe'],r['venue'],r['title'],r['state'],r['when'],r['url'])
        if k in seen: continue
        seen.add(k); u.append(r)
    return u
res={}
for line in open('tmp/_poolgrp1_0831.txt',encoding='utf-8'):
    line=line.strip()
    if not line: continue
    p=line.split('|'); eid=p[0]
    h=open(os.path.join(OUT,eid+'.html'),encoding='utf-8').read()
    cards=parse(h)
    og=re.search(r'<meta property="og:title" content="([^"]*)"',h)
    ogt=_html.unescape(og.group(1)) if og else ''
    g=re.search(r'\[(.*?)のチケット',ogt)
    genre=g.group(1) if g else ''
    name=ogt.split(' | ')[0]
    bread=re.findall(r'breadCrumb-2024__item[^>]*>(?:<a[^>]*>)?(.*?)(?:</a>)?</li>',h)
    res[eid]=dict(line=line, name=unicodedata.normalize('NFKC',name), genre=genre,
                  bread=[txt(b) for b in bread], cards=cards)
json.dump(res,open('tmp/_agentP1_parsed.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
# summary
print('id|regname|regdate|regpref|regn || piaN(buy)|piaMaxAll|piaMaxBuy|piaPrefs|genre|piaName')
for eid,d in res.items():
    p=d['line'].split('|')
    buy=[c for c in d['cards'] if c['state'] in ('受付中','発売前')]
    alld=[c['pe'] for c in d['cards'] if c['pe']]
    buyd=[c['pe'] for c in buy if c['pe']]
    prefs=sorted(set(c['pref'] for c in buy if c['pref']))
    print(f"{eid}|{p[1]}|{p[2]}|{p[3]}|{p[4]} || {len(buy)}|{max(alld) if alld else '-'}|{max(buyd) if buyd else '-'}|{','.join(prefs)}|{d['genre']}|{d['name']}")
