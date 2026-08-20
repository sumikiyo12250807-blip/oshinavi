# -*- coding: utf-8 -*-
import urllib.request, re, html as _html, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# id -> pia url(eventCd or bundle)
targets = {
110:'b2665524',128:'b2665378',203:'b2666419',256:'2611766',337:'2620605',
348:'2612820',413:'b2668409',425:'2617634',434:'b2668726',438:'2612127',
448:'b2667704',468:'b2668129',471:'2609830',533:'2621115',617:'2615930',
652:'b2562014',658:'2623282',692:'2618753',763:'2622037',803:'2617640',
832:'2623880',846:'2621158',866:'2615943',875:'2621916',921:'2615773',
927:'2619698',978:'2547320',979:'2613444',980:'2615842',982:'2614548',
983:'2617736',984:'2621819',985:'2624692',986:'2617765',987:'2619958',
988:'2606479',989:'2624688',990:'2624686',991:'2624683',992:'b2669038',
997:'2613272',998:'2617771',999:'2617374',1000:'2619469',1129:'2622901',
}

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8','replace')
def txt(s):
    return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()

def parse(cd):
    if cd.startswith('b'):
        url='https://t.pia.jp/pia/event/event.do?eventBundleCd='+cd
    else:
        url='https://t.pia.jp/pia/event/event.do?eventCd='+cd
    h=fetch(url)
    items=re.split(r'(?=<li class="ticketSalesList-2024__item)',h)
    rows=[]
    for it in items:
        if 'ticketSalesCard-2024__status' not in it: continue
        m_title=re.search(r'__title">(.*?)</p>',it,re.S)
        m_place=re.search(r'__place"[^>]*>(.*?)</span>',it,re.S)
        m_region=re.search(r'__region">(.*?)</span>',it,re.S)
        _dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it)
        ps=_dts[0] if _dts else ''; pe=_dts[-1] if _dts else ''
        m_stat=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)',it,re.S)
        m_sdate=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>',it,re.S)
        st=txt(m_stat.group(2)) if m_stat else ''
        sd=txt(m_sdate.group(1)) if m_sdate else ''
        if re.search(r'(販売期間中|受付中)',st): state='受付中'
        elif '発売前' in st: state='発売前'
        else: state='受付終了'
        rows.append({'pd':ps,'pe':pe,'venue':txt(m_place.group(1)) if m_place else '',
            'pref':txt(m_region.group(1)) if m_region else '','title':txt(m_title.group(1)) if m_title else '',
            'state':state,'stat_text':st,'when':sd})
    seen=set();uniq=[]
    for r in rows:
        k=(r['pd'],r['pe'],r['venue'],r['title'],r['state'],r['when'])
        if k in seen: continue
        seen.add(k);uniq.append(r)
    return url,uniq

result={}
for i,cd in targets.items():
    try:
        url,rows=parse(cd)
        buy=[r for r in rows if r['state'] in ('受付中','発売前')]
        result[i]={'url':url,'rows':rows,'n_buy':len(buy)}
        print(f"id={i}\tbuyable={len(buy)}/{len(rows)}\t{cd}")
    except Exception as e:
        result[i]={'error':str(e)}
        print(f"id={i}\tERROR {e}")
json.dump(result,open('tmp/parsed.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
