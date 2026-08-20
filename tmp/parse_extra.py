# -*- coding: utf-8 -*-
import urllib.request,re,html as _html,json,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
extra={'617宮崎':'2615977','617神奈川':'2620866','763石川富山':'2621691','763新潟長野':'2621692'}
def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
def txt(s): return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
for k,cd in extra.items():
    h=fetch('https://t.pia.jp/pia/event/event.do?eventCd='+cd)
    items=re.split(r'(?=<li class="ticketSalesList-2024__item)',h)
    print(f"\n=== {k} (eventCd={cd}) ===")
    seen=set()
    for it in items:
        if 'ticketSalesCard-2024__status' not in it: continue
        _dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it)
        ps=_dts[0] if _dts else '';pe=_dts[-1] if _dts else ''
        m_stat=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)',it,re.S)
        m_sdate=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>',it,re.S)
        m_region=re.search(r'__region">(.*?)</span>',it,re.S)
        m_title=re.search(r'__title">(.*?)</p>',it,re.S)
        st=txt(m_stat.group(2)) if m_stat else '';sd=txt(m_sdate.group(1)) if m_sdate else ''
        if re.search(r'(販売期間中|受付中)',st):state='受付中'
        elif '発売前' in st:state='発売前'
        else:state='受付終了'
        reg=txt(m_region.group(1)) if m_region else '';ti=txt(m_title.group(1)) if m_title else ''
        k2=(ps,pe,reg,state,sd,ti)
        if k2 in seen:continue
        seen.add(k2)
        print(f"  [{state}|{st}] {ps}~{pe} {reg} | {ti[:36]} | {sd}")
