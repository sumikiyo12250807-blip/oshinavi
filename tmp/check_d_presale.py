# -*- coding: utf-8 -*-
import urllib.request,re,html as _html,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
D={128:'b2665378',434:'b2668726',468:'b2668129',652:'b2562014',658:'2623282',1129:'2622901'}
def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
def txt(s): return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
for eid,cd in D.items():
    url=('https://t.pia.jp/pia/event/event.do?eventBundleCd='+cd) if cd.startswith('b') else ('https://t.pia.jp/pia/event/event.do?eventCd='+cd)
    h=fetch(url)
    print(f"\n===== id={eid} ({cd}) =====")
    # 全カードの状態＋発売日らしき記述
    items=re.split(r'(?=<li class="ticketSalesList-2024__item)',h)
    seen=set()
    for it in items:
        if 'ticketSalesCard-2024__status' not in it:continue
        m_stat=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)',it,re.S)
        m_sd=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>',it,re.S)
        m_ti=re.search(r'__title">(.*?)</p>',it,re.S)
        st=txt(m_stat.group(2)) if m_stat else '';sd=txt(m_sd.group(1)) if m_sd else ''
        ti=txt(m_ti.group(1)) if m_ti else ''
        k=(st,sd,ti)
        if k in seen:continue
        seen.add(k)
        print(f"  [{st}] {sd} | {ti[:40]}")
    # 本文に「一般発売」＋日付がないか
    body=txt(h)
    for mm in re.finditer(r'一般発売[^。]{0,40}?(\d{1,2}[/／]\d{1,2})', body):
        print('   >> 本文一般発売:', mm.group(0)[:60])
