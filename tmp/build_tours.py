# -*- coding: utf-8 -*-
"""バンドルツアー9件: 受付中cardを終了日でグループ化して販売中チケットを構築。
同一終了日→1バッジ(会場列挙)、別終了日→別バッジ。link.piaは単一bundleで全会場カバー。"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open('tmp/presale_ends.json', encoding='utf-8'))
PREF = {'北海道':'北海道','青森県':'青森','岩手県':'岩手','宮城県':'宮城','秋田県':'秋田','山形県':'山形',
'福島県':'福島','茨城県':'茨城','栃木県':'栃木','群馬県':'群馬','埼玉県':'埼玉','千葉県':'千葉','東京都':'東京',
'神奈川県':'神奈川','新潟県':'新潟','富山県':'富山','石川県':'石川','福井県':'福井','山梨県':'山梨','長野県':'長野',
'岐阜県':'岐阜','静岡県':'静岡','愛知県':'愛知','三重県':'三重','滋賀県':'滋賀','京都府':'京都','大阪府':'大阪',
'兵庫県':'兵庫','奈良県':'奈良','和歌山県':'和歌山','鳥取県':'鳥取','島根県':'島根','岡山県':'岡山','広島県':'広島',
'山口県':'山口','徳島県':'徳島','香川県':'香川','愛媛県':'愛媛','高知県':'高知','福岡県':'福岡','佐賀県':'佐賀',
'長崎県':'長崎','熊本県':'熊本','大分県':'大分','宮崎県':'宮崎','鹿児島県':'鹿児島','沖縄県':'沖縄'}
def md(iso):
    y,m,dd=iso.split('-'); return f'{int(m)}/{int(dd)}'
def when_to(w):
    m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2}).*?(\d{1,2}:\d{2})',w)
    if not m:
        m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})',w)
        return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}','23:59',f'{int(m.group(2))}/{int(m.group(3))}')
    return (f'{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}',m.group(4),f'{int(m.group(2))}/{int(m.group(3))}')

IDS=['334','401','528','541','631','673','802','872','883']
result={}
for eid in IDS:
    rec=d[eid]
    cards=[c for c in rec['uketsuke'] if c['state']=='受付中']
    # group by (end_iso, end_hm)
    groups={}
    for c in cards:
        ei,hm,emd=when_to(c['when'])
        pref=PREF.get(c['pref'].split('／')[0].strip(),c['pref'])
        # perf day(s)
        if c['perf_end'] and c['perf_end']!=c['perf']:
            perf=f"{md(c['perf'])}〜{md(c['perf_end'])}"
        else:
            perf=md(c['perf'])
        groups.setdefault((ei,hm),[]).append((pref,perf))
    tickets=[]
    for (ei,hm),vens in sorted(groups.items()):
        # dedup venue/perf pairs
        seen=[];uv=[]
        for v in vens:
            if v not in seen: seen.append(v);uv.append(v)
        body='・'.join(f'{p} {pf}公演' for p,pf in uv)
        emd=md(ei)
        tickets.append({'type':f'一般発売（{body}）〜{emd} {hm}','date':ei})
    result[eid]={'name':rec['name'][:40],'tickets':tickets}
    print(f"\nid{eid} {rec['name'][:40]}")
    for t in tickets: print(f"   {t['type']}  (date {t['date']})")
json.dump(result,open('tmp/tour_tickets.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
