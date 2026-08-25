# -*- coding: utf-8 -*-
import json, os, re
BASE = r'C:/Users/user/oshinavi'
items = json.load(open(os.path.join(BASE,'tmp','verify_in_2_0825.json'), encoding='utf-8'))
FULL = ['北海道','青森県','岩手県','宮城県','秋田県','山形県','福島県','茨城県','栃木県','群馬県','埼玉県','千葉県','東京都','神奈川県','新潟県','富山県','石川県','福井県','山梨県','長野県','岐阜県','静岡県','愛知県','三重県','滋賀県','京都府','大阪府','兵庫県','奈良県','和歌山県','鳥取県','島根県','岡山県','広島県','山口県','徳島県','香川県','愛媛県','高知県','福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県']
BARE = [p if p=='北海道' else p[:-1] for p in FULL]
# 東京都 を先に置く（「京都」誤マッチ回避）。長い順 + 東京都優先
FULL_SORTED = sorted(FULL, key=lambda s: (-len(s), s))
RE_FULL = re.compile('|'.join(FULL_SORTED))
BARE_SORTED = sorted(BARE, key=lambda s: -len(s))
RE_BARE = re.compile('|'.join(BARE_SORTED))
def short(p):
    return p if p=='北海道' else re.sub(r'(都|府|県)$','',p)
def prefs_from(s):
    s = (s or '')
    got = [short(m.group(0)) for m in RE_FULL.finditer(s)]
    if got: return got
    # 素の県名（「大阪城ホール」等）。東京都対策で先に東京を潰す
    got = [m.group(0) for m in RE_BARE.finditer(s)]
    return got
res = {}
for it in items:
    eid = str(it['id'])
    p = os.path.join(BASE,'tmp','w_%s.json'%eid)
    if not os.path.exists(p) or os.path.getsize(p)==0:
        res[eid] = {'error':'ページ取得に失敗（ファイル無し）'}; continue
    rows = json.load(open(p, encoding='utf-8'))
    buy = [r for r in rows if r.get('state') in ('受付中','発売前')]
    slots=[]; prefs=[]
    for r in buy:
        pr = prefs_from(r.get('pref','')) or prefs_from(r.get('venue',''))
        for x in pr:
            if x not in prefs: prefs.append(x)
        slots.append({'title':r.get('title',''),'when':r.get('when',''),'venue':r.get('venue',''),
                      'perfdate':r.get('perfdate',''),'perf_end':r.get('perf_end',''),
                      'state':r.get('state',''),'statustext':r.get('statustext',''),
                      'prefs':pr,'url':r.get('url','')})
    dates=[d for s in slots for d in (s['perfdate'],s['perf_end']) if d]
    res[eid]={'buyable':len(buy),'total_cards':len(rows),
              'last_perf':max(dates) if dates else None,
              'first_perf':min(dates) if dates else None,
              'prefs':prefs,'slots':slots,
              'not_buyable':[{'title':r.get('title',''),'statustext':r.get('statustext','')} for r in rows if r.get('state') not in ('受付中','発売前')]}
json.dump(res, open(os.path.join(BASE,'tmp','verify_out_2_0825.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
# ASCII-safe report
print('ids=%d errors=%d' % (len(res), sum(1 for v in res.values() if 'error' in v)))
print('zero_buyable=%s' % [k for k,v in res.items() if v.get('buyable')==0])
print('no_pref=%s' % [k for k,v in res.items() if not v.get('error') and not v['prefs']])
print('multi_pref=%s' % {k:len(v['prefs']) for k,v in res.items() if not v.get('error') and len(v['prefs'])>1})
print('empty_title=%s' % [k for k,v in res.items() if not v.get('error') and any(not s['title'].strip() for s in v['slots'])])
print('empty_when=%s' % [k for k,v in res.items() if not v.get('error') and any(not s['when'].strip() for s in v['slots'])])
print('empty_venue=%s' % [k for k,v in res.items() if not v.get('error') and any(not s['venue'].strip() for s in v['slots'])])
print('empty_perfdate=%s' % [k for k,v in res.items() if not v.get('error') and any(not s['perfdate'] for s in v['slots'])])
print('last_perf_before_today=%s' % [k for k,v in res.items() if not v.get('error') and v['last_perf'] and v['last_perf'] < '2026-08-25'])
print('dup_urls=%s' % [k for k,v in res.items() if not v.get('error') and len({s['url'] for s in v['slots']})!=len(v['slots'])])
print('states=%s' % sorted({s['state'] for v in res.values() if not v.get('error') for s in v['slots']}))
