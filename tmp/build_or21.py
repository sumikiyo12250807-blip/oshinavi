# -*- coding: utf-8 -*-
"""id21 ORANGE RANGE 25周年ツアーを bundle b2666269 から全会場再構築。
受付中→販売中(〜end・販売日でグループ)、発売前→発売前(startDate・発売日でグループ)。"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
rows = json.load(open('tmp/or21.json', encoding='utf-8'))
PREF = {'北海道':'北海道','青森県':'青森','岩手県':'岩手','宮城県':'宮城','秋田県':'秋田','山形県':'山形','福島県':'福島','茨城県':'茨城','栃木県':'栃木','群馬県':'群馬','埼玉県':'埼玉','千葉県':'千葉','東京都':'東京','神奈川県':'神奈川','新潟県':'新潟','富山県':'富山','石川県':'石川','福井県':'福井','山梨県':'山梨','長野県':'長野','岐阜県':'岐阜','静岡県':'静岡','愛知県':'愛知','三重県':'三重','滋賀県':'滋賀','京都府':'京都','大阪府':'大阪','兵庫県':'兵庫','奈良県':'奈良','和歌山県':'和歌山','鳥取県':'鳥取','島根県':'島根','岡山県':'岡山','広島県':'広島','山口県':'山口','徳島県':'徳島','香川県':'香川','愛媛県':'愛媛','高知県':'高知','福岡県':'福岡','佐賀県':'佐賀','長崎県':'長崎','熊本県':'熊本','大分県':'大分','宮崎県':'宮崎','鹿児島県':'鹿児島','沖縄県':'沖縄'}
def md(iso):
    y,m,d=iso.split('-');return f'{int(m)}/{int(d)}'
def pref_disp(p):
    parts=[PREF.get(x.strip(),x.strip()) for x in p.split('／') if x.strip()]
    return '・'.join(parts)
def perf_disp(r):
    return md(r['perfdate'])+('〜'+md(r['perf_end']) if r['perf_end'] and r['perf_end']!=r['perfdate'] else '')
def kind(title):
    if 'ファミリーマート' in title or 'ファミマ' in title: return '先行（ファミマ）'
    if 'プレリザーブ' in title: return 'プレリザーブ'
    if 'プリセール' in title: return 'プリセール'
    if '一般' in title: return '一般発売'
    return '先行'
def end_dt(w):
    m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2}).*?(\d{1,2}:\d{2})',w)
    if not m:
        m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})',w)
        return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}','23:59',f'{int(m.group(2))}/{int(m.group(3))}')
    return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}',m.group(4),f'{int(m.group(2))}/{int(m.group(3))}')
def start_dt(w):
    m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2}).*?(\d{1,2}:\d{2})',w)
    return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}',m.group(4),f'{int(m.group(2))}/{int(m.group(3))}')

# 受付中 group by (kind, end iso, end hm)
g_now={}; g_pre={}
for r in rows:
    pd=pref_disp(r['pref']); pf=perf_disp(r); k=kind(r['title'])
    if r['state']=='受付中':
        ei,hm,emd=end_dt(r['when']); g_now.setdefault((k,ei,emd,hm),[]).append((pd,pf))
    else:
        si,hm,smd=start_dt(r['when']); g_pre.setdefault((k,si,smd,hm),[]).append((pd,pf))

tickets=[]
for (k,ei,emd,hm),v in sorted(g_now.items(),key=lambda x:x[0][1]):
    seen=[];uv=[]
    for x in v:
        if x not in seen:seen.append(x);uv.append(x)
    body='・'.join(f'{p} {pf}公演' for p,pf in uv)
    tickets.append({'type':f'{k}（{body}）〜{emd} {hm}','date':ei})
for (k,si,smd,hm),v in sorted(g_pre.items(),key=lambda x:x[0][1]):
    seen=[];uv=[]
    for x in v:
        if x not in seen:seen.append(x);uv.append(x)
    body='・'.join(f'{p} {pf}公演' for p,pf in uv)
    tickets.append({'type':f'{k}（{body}）{smd} {hm}発売','startDate':si,'date':si})

for t in tickets:
    print(json.dumps(t,ensure_ascii=False))
print('\n計',len(tickets),'枠')
json.dump(tickets,open('tmp/or21_tickets.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
