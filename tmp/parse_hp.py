import urllib.request,re,html as _html,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
months={'9月':'b2669039','10月':'b2669040','11月':'b2669041','12月':'b2669042'}
def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
def txt(s): return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
for mo,cd in months.items():
    h=fetch('https://t.pia.jp/pia/event/event.do?eventBundleCd='+cd)
    items=re.split(r'(?=<li class="ticketSalesList-2024__item)',h)
    print(f"\n=== ハリポタ{mo} ({cd}) ===")
    seen=set()
    for it in items:
        if 'ticketSalesCard-2024__status' not in it:continue
        _dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it)
        ps=_dts[0] if _dts else '';pe=_dts[-1] if _dts else ''
        m_stat=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)',it,re.S)
        m_sd=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>',it,re.S)
        m_ti=re.search(r'__title">(.*?)</p>',it,re.S)
        st=txt(m_stat.group(2)) if m_stat else '';sd=txt(m_sd.group(1)) if m_sd else ''
        if re.search(r'(販売期間中|受付中)',st):state='受付中'
        elif '発売前' in st:state='発売前'
        else:state='受付終了'
        ti=txt(m_ti.group(1)) if m_ti else ''
        k=(ps,pe,state,sd,ti)
        if k in seen:continue
        seen.add(k)
        print(f"  [{state}|{st}] {ps}~{pe} | {ti[:40]} | {sd}")
