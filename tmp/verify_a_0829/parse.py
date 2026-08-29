import re,os,json,glob,html as H
D=os.path.dirname(os.path.abspath(__file__)); RAW=os.path.join(D,'raw')
def txt(s):
    s=re.sub(r'<[^>]+>','\n',s); s=H.unescape(s)
    s=s.replace(' ',' ')
    s=re.sub(r'[ \t　]+',' ',s); s=re.sub(r'\n\s*\n+','\n',s)
    return s.strip()
def load(p): return open(p,encoding='utf-8',errors='replace').read()
def clean(h):
    h=re.sub(r'<script.*?</script>','',h,flags=re.S)
    return re.sub(r'<style.*?</style>','',h,flags=re.S)

def parse_event(h):
    o={}
    m=re.search(r'<title>(.*?)</title>',h,re.S)
    o['title_tag']=txt(m.group(1)) if m else ''
    m=re.search(r'公演期間.*?</dt>(.*?)</dd>',h,re.S)
    b=clean(h)
    # 公演期間 / 会場 from detail block
    m=re.search(r'公演期間(.{0,600}?)会場(.{0,1500}?)出演者',b,re.S)
    if m:
        o['period']=txt(m.group(1)); o['venues']=txt(m.group(2))
    return o

def parse_ti(h):
    b=clean(h); o={}
    m=re.search(r'<h1 class="rsTitle__text">(.*?)</h1>',b,re.S)
    o['h1']=txt(m.group(1)) if m else ''
    m=re.search(r'<ol class="breadcrumb breadcrumb--pcOnly">(.*?)</ol>',b,re.S)
    o['breadcrumb']=' > '.join(x.strip() for x in txt(m.group(1)).split('\n') if x.strip()) if m else ''
    m=re.search(r'<p class="textLabel">(.*?)</p>',b,re.S)
    o['label']=' | '.join(x.strip() for x in txt(m.group(1)).split('\n') if x.strip()) if m else ''
    o['periods']=[]
    for m in re.finditer(r'<dl class="dataList">(.*?)</dl>',b,re.S):
        parts=[x.strip() for x in txt(m.group(1)).split('\n') if x.strip()]
        o['periods'].append(' :: '.join(parts))
    # status words present
    o['status_words']=sorted(set(w for w in ['受付前','受付中','受付終了','予定枚数終了','販売終了','発売前','販売中','完売','取扱終了'] if w in txt(b)))
    # performances
    perfs=[]
    for m in re.finditer(r'<(?:li|div)[^>]*class="[^"]*(?:performanceList__item|eventDetail__item)[^"]*"[^>]*>(.*?)</\1>',b,re.S):
        pass
    # generic: find 会場： lines with preceding date
    sec=b
    i=sec.find('公演日時・座席')
    if i>=0: sec=sec[i:]
    t=txt(sec)
    lines=[x.strip() for x in t.split('\n') if x.strip()]
    cur=None
    for j,l in enumerate(lines):
        if re.match(r'^\d{4}/\d{1,2}/\d{1,2}\([月火水木金土日]\)',l):
            cur={'date':l,'venue':'','time':''}
            perfs.append(cur)
        elif cur is not None and l.startswith('会場：') and not cur['venue']:
            cur['venue']=l
        elif cur is not None and ('開演' in l) and not cur['time']:
            cur['time']=l
    o['perfs']=perfs[:60]
    return o

man=json.load(open(os.path.join(D,'manifest.json'),encoding='utf-8')) if os.path.exists(os.path.join(D,'manifest.json')) else {}
out=[]
def key(u): return re.sub(r'[^A-Za-z0-9]+','_',u.split('pia/')[-1])[:120]
for i,ent in man.items():
    rec={'id':i,'pages':[],'ti':[]}
    for u,pv in ent['pages'].items():
        p=os.path.join(RAW,key(u)+'.html')
        h=load(p) if os.path.exists(p) else ''
        rec['pages'].append({'url':u,'ok':len(h)>2000,'ev':parse_event(h) if h else {}})
    for u in ent['ti']:
        p=os.path.join(RAW,key(u)+'.html')
        h=load(p) if os.path.exists(p) else ''
        rec['ti'].append({'url':u,'ok':len(h)>2000,'d':parse_ti(h) if len(h)>2000 else {}})
    out.append(rec)
json.dump(out,open(os.path.join(D,'parsed.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('ids',len(out))
