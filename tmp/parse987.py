import urllib.request,re,html as _html,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
cds={'宮崎10/21':'2619959','宮崎10/22':'2619960','大分10/23':'2619961'}
def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
def txt(s): return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
for k,cd in cds.items():
    h=fetch('https://t.pia.jp/pia/event/event.do?eventCd='+cd)
    items=re.split(r'(?=<li class="ticketSalesList-2024__item)',h)
    print(f"\n=== 梅沢{k} ({cd}) ===")
    seen=set()
    for it in items:
        if 'ticketSalesCard-2024__status' not in it:continue
        _dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it)
        ps=_dts[0] if _dts else '';pe=_dts[-1] if _dts else ''
        m_stat=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)',it,re.S)
        m_sd=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>',it,re.S)
        st=txt(m_stat.group(2)) if m_stat else '';sd=txt(m_sd.group(1)) if m_sd else ''
        state='受付中' if re.search(r'(販売期間中|受付中)',st) else('発売前' if '発売前' in st else '受付終了')
        k2=(ps,pe,state,sd)
        if k2 in seen:continue
        seen.add(k2)
        print(f"  [{state}|{st}] {ps}~{pe} | {sd}")
