# -*- coding: utf-8 -*-
"""8件の取りこぼしツアーを bundle から全枠再構築。or21ロジック汎用化。"""
import json, io, sys, re, urllib.request, html as _html, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
txt = open('index.html', encoding='utf-8').read()
i = txt.index('const EVENTS = [') + len('const EVENTS = ')
arr, _ = json.JSONDecoder().raw_decode(txt, i)
byid = {e['id']: e for e in arr}
PREF = {'北海道':'北海道','青森県':'青森','岩手県':'岩手','宮城県':'宮城','秋田県':'秋田','山形県':'山形','福島県':'福島','茨城県':'茨城','栃木県':'栃木','群馬県':'群馬','埼玉県':'埼玉','千葉県':'千葉','東京都':'東京','神奈川県':'神奈川','新潟県':'新潟','富山県':'富山','石川県':'石川','福井県':'福井','山梨県':'山梨','長野県':'長野','岐阜県':'岐阜','静岡県':'静岡','愛知県':'愛知','三重県':'三重','滋賀県':'滋賀','京都府':'京都','大阪府':'大阪','兵庫県':'兵庫','奈良県':'奈良','和歌山県':'和歌山','鳥取県':'鳥取','島根県':'島根','岡山県':'岡山','広島県':'広島','山口県':'山口','徳島県':'徳島','香川県':'香川','愛媛県':'愛媛','高知県':'高知','福岡県':'福岡','佐賀県':'佐賀','長崎県':'長崎','熊本県':'熊本','大分県':'大分','宮崎県':'宮崎','鹿児島県':'鹿児島','沖縄県':'沖縄'}
def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'});return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
def clean(s):return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
def parse(h):
    out=[]
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)',h):
        if 'ticketSalesCard-2024__status' not in it:continue
        m=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)',it,re.S);st=clean(m.group(2)) if m else ''
        m2=re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>',it,re.S);when=clean(m2.group(1)) if m2 else ''
        dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it)
        mr=re.search(r'__region">(.*?)</span>',it,re.S);pr=clean(mr.group(1)) if mr else ''
        mt=re.search(r'__title">(.*?)</p>',it,re.S);ti=clean(mt.group(1)) if mt else ''
        if re.search(r'(販売期間中|受付中)',st):s='受付中'
        elif '発売前' in st:s='発売前'
        else:continue
        out.append({'state':s,'perf':dts[0] if dts else '','perf_end':dts[-1] if dts else '','pref':pr,'title':ti,'when':when})
    seen=[];u=[]
    for c in out:
        k=(c['state'],c['perf'],c['perf_end'],c['pref'],c['title'],c['when'])
        if k in seen:continue
        seen.append(k);u.append(c)
    return u
def md(iso):y,m,d=iso.split('-');return f'{int(m)}/{int(d)}'
def pref_disp(p,title):
    if p.strip():
        return '・'.join(PREF.get(x.strip(),x.strip()) for x in p.split('／') if x.strip())
    mt=re.search(r'〔([^〕]+)〕',title)
    if mt:
        return '・'.join(PREF.get(x.strip()+'県',x.strip()) for x in re.split(r'[・／]',mt.group(1)))
    return ''
def perf_disp(c):
    return md(c['perf'])+('〜'+md(c['perf_end']) if c['perf_end'] and c['perf_end']!=c['perf'] else '')
def kind(t):
    if 'ファミリーマート' in t or 'ファミマ' in t:return '先行（ファミマ）'
    if 'プレリザーブ' in t:return 'プレリザーブ'
    if 'プリセール' in t:return 'プリセール'
    if 'オフィシャル' in t and '先行' in t:return 'オフィシャル先行'
    if 'セブン' in t:return 'セブン先行'
    if '一般' in t:return '一般発売'
    return '先行'
def edt(w):
    m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2}).*?(\d{1,2}:\d{2})',w)
    if not m:
        m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})',w)
        return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}','23:59',f'{int(m.group(2))}/{int(m.group(3))}')
    return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}',m.group(4),f'{int(m.group(2))}/{int(m.group(3))}')

def jisuu(t):
    m=re.search(r'(\d+)\s*次',t)
    return f'{m.group(1)}次' if m else ''
def is_combo(c):
    # region空(複数地域まとめ)のみ複数公演扱い。1会場ロングランは県名+範囲で出す
    return not c['pref'].strip()
def build(cards):
    g_now={};g_pre={}
    for c in cards:
        k=kind(c['title']);js=jisuu(c['title'])
        klabel=f'{k}{js}' if (js and 'プレリザーブ' in k) else k
        if is_combo(c):
            pd='';pf='複数'
        else:
            pd=pref_disp(c['pref'],c['title']);pf=perf_disp(c)
        if c['state']=='受付中':
            ei,hm,emd=edt(c['when']);g_now.setdefault((klabel,ei,emd,hm),[]).append((pd,pf))
        else:
            si,hm,smd=edt(c['when']);g_pre.setdefault((klabel,si,smd,hm),[]).append((pd,pf))
    def mkbody(v):
        seen=[];uv=[]
        for x in v:
            if x not in seen:seen.append(x);uv.append(x)
        parts=[]
        for p,pf in uv:
            if pf=='複数': parts.append('複数公演')
            elif p: parts.append(f'{p} {pf}公演')
            else: parts.append(f'{pf}公演')
        # 複数公演が複数あれば1つに
        out=[];s2=set()
        for x in parts:
            if x=='複数公演':
                if '複数公演' in s2: continue
                s2.add('複数公演')
            out.append(x)
        return '・'.join(out)
    tk=[]
    for (k,ei,emd,hm),v in sorted(g_now.items(),key=lambda x:(x[0][1],x[0][0])):
        tk.append({'type':f'{k}（{mkbody(v)}）〜{emd} {hm}','date':ei})
    for (k,si,smd,hm),v in sorted(g_pre.items(),key=lambda x:(x[0][1],x[0][0])):
        tk.append({'type':f'{k}（{mkbody(v)}）{smd} {hm}発売','startDate':si,'date':si})
    return tk

IDS=[129,237,529,539,824,665,431,269]
res={}
for eid in IDS:
    e=byid[eid]
    cards=parse(fetch(e['links']['pia']))
    tk=build(cards)
    # span: last perf for date
    perfs=sorted([c['perf_end'] or c['perf'] for c in cards if c['perf']])
    res[str(eid)]={'tickets':tk,'last_perf':perfs[-1] if perfs else e['date'],'first_perf':perfs[0] if perfs else e['date']}
    print(f"\n==== id{eid} {e['name'][:30]} → {len(tk)}枠 (公演 {res[str(eid)]['first_perf']}〜{res[str(eid)]['last_perf']}) ====")
    for t in tk:print("  ",t['type'],"|",t['date'])
    time.sleep(0.3)
json.dump(res,open('tmp/eight_tours.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
