import re,os,json,html as H
D='C:/Users/user/oshinavi/tmp/verify_a_0829'; RAW=D+'/raw'
def txt(s):
    s=re.sub(r'<br\s*/?>','\n',s,flags=re.I)
    s=re.sub(r'<[^>]+>','\n',s); s=H.unescape(s)
    s=s.replace('\u00a0',' ').replace('\u3000',' ')
    s=re.sub(r'[ \t]+',' ',s); s=re.sub(r'\n\s*\n+','\n',s)
    return s.strip()
def one(s): return ' '.join(x.strip() for x in txt(s).split('\n') if x.strip())
def clean(h):
    h=re.sub(r'<script.*?</script>','',h,flags=re.S)
    return re.sub(r'<style.*?</style>','',h,flags=re.S)
def key(u): return re.sub(r'[^A-Za-z0-9]+','_',u.split('pia/')[-1])[:120]
def load(u):
    p=os.path.join(RAW,key(u)+'.html')
    if not os.path.exists(p): return ''
    return open(p,encoding='utf-8',errors='replace').read()

def split_items(b):
    """return list of (ended_flag, item_html)"""
    out=[]
    # locate ended wrapper
    endi=b.find('ticketSalesEnd-2024')
    for m in re.finditer(r'<li class="ticketSalesList-2024__item vevent"',b):
        s=m.start()
        e=b.find('<li class="ticketSalesList-2024__item vevent"',s+10)
        seg=b[s: e if e>0 else s+9000]
        out.append(((endi>=0 and s>endi), seg))
    return out

def parse_card(seg):
    o={}
    m=re.search(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"',seg); o['url']=m.group(1) if m else ''
    m=re.search(r'ticketSalesCard-2024__title">(.*?)</p>',seg,re.S); o['name']=one(m.group(1)) if m else ''
    m=re.search(r'ticketSalesCard-2024__tagList">(.*?)</ul>',seg,re.S); o['tags']=one(m.group(1)) if m else ''
    md=re.search(r'ticketSalesCard-2024__date">(.*?)</p>',seg,re.S)
    ds=re.findall(r'itemprop="(?:startDate|endDate)" datetime="([^"]+)"',md.group(1)) if md else []
    o['show_dates']=[v[:10] for v in ds]
    o['date_text']=one(md.group(1)) if md else ''
    ml=re.search(r'ticketSalesCard-2024__location"(.*?)</p>',seg,re.S)
    lb=ml.group(1) if ml else ''
    m=re.search(r'ticketSalesCard-2024__place"[^>]*>(.*?)</span>',lb,re.S); o['venue']=one(m.group(1)) if m else ''
    m=re.search(r'ticketSalesCard-2024__region">(.*?)</span>',lb,re.S); o['pref']=one(m.group(1)) if m else ''
    m=re.search(r'ticketSalesCard-2024__status ([^"]*)">(.*?)</p>',seg,re.S)
    if m:
        o['status_class']=m.group(1).strip(); o['status_text']=one(m.group(2))
    else:
        o['status_class']=''; o['status_text']=''
    o['soldout']= 'is-soldout' in seg or '予定枚数終了' in txt(seg)
    return o

def parse_event_page(u):
    h=load(u)
    if len(h)<2000: return {'url':u,'ok':False}
    b=clean(h)
    o={'url':u,'ok':True}
    m=re.search(r'<title>(.*?)</title>',b,re.S); o['title_tag']=one(m.group(1)) if m else ''
    m=re.search(r'<h1[^>]*>(.*?)</h1>',b,re.S); o['h1']=one(m.group(1)) if m else ''
    # breadcrumb-ish footer nav
    m=re.search(r'公演期間(.*?)会場(.*?)(出演者|公演などに関する)',b,re.S)
    if m:
        o['period']=one(m.group(1)); o['venue_list']=[x.strip() for x in txt(m.group(2)).split('\n') if x.strip()]
    cards=[]
    for ended,seg in split_items(b):
        c=parse_card(seg); c['in_ended_list']=ended
        cards.append(c)
    # dedupe by url keeping first
    seen={}; uniq=[]
    for c in cards:
        k=(c['url'],c['name'],tuple(c['show_dates']),c['venue'])
        if k in seen: continue
        seen[k]=1; uniq.append(c)
    o['cards']=uniq
    return o

def parse_ti_page(u):
    h=load(u)
    if len(h)<2000: return {'url':u,'ok':False}
    b=clean(h); o={'url':u,'ok':True}
    m=re.search(r'<h1 class="rsTitle__text">(.*?)</h1>',b,re.S); o['h1']=one(m.group(1)) if m else ''
    m=re.search(r'<ol class="breadcrumb breadcrumb--pcOnly">(.*?)</ol>',b,re.S)
    o['breadcrumb']=' > '.join(x.strip() for x in txt(m.group(1)).split('\n') if x.strip()) if m else ''
    m=re.search(r'<p class="textLabel">(.*?)</p>',b,re.S); o['label']=one(m.group(1)) if m else ''
    per=[]
    for m in re.finditer(r'<dl class="dataList">(.*?)</dl>',b,re.S):
        s=one(m.group(1))
        if re.search(r'(発売開始|受付期間|申込期間|抽選)',s): per.append(s)
    o['window']=per
    sec=b
    i=b.find('公演日時・座席')
    if i>=0: sec=b[i:]
    tt=re.sub(r'\s+','',txt(sec))
    PREF=r'(?:北海道|東京都|大阪府|京都府|.{2,4}県)'
    DATE=r'(\d{4}/\d{1,2}/\d{1,2}\([月火水木金土日]\))'
    o['perf_dates']=sorted(set(re.findall(DATE,tt)))
    o['venues']=sorted(set(re.findall(r'会場：(.{1,40}?\('+PREF+r'\))',tt)))
    o['perf_pairs']=re.findall(DATE+r'(?:(?!\d{4}/\d).){0,300}?会場：(.{1,40}?\('+PREF+r'\))',tt)[:80]
    return o

man=json.load(open(D+'/manifest.json',encoding='utf-8'))
out=[]
for i,ent in man.items():
    rec={'id':i,'events':[parse_event_page(u) for u in ent['pages']],'ti':[parse_ti_page(u) for u in ent['ti']]}
    out.append(rec)
json.dump(out,open(D+'/parsed.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('ids',len(out))
