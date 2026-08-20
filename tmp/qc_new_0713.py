# -*- coding: utf-8 -*-
"""新着プール(genre:new)の機械QC。過去に事故った項目を全部見る。
 ①全角ローマ字/数字の残り ②空カッコ会場「（）」 ③日付逆転(販売開始>販売終了 / 販売>公演)
 ④eventCd重複・正規化名重複（既存含む） ⑤2027公演のR9年表記漏れ ⑥価格捏造(priceは基本null)
 ⑦verified欠落 ⑧飾り記号(●○★@※)の残り
"""
import re, json, sys, unicodedata, collections
sys.stdout = io.StringIO() if False else sys.stdout
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
NEW = [e for e in E if e.get('genre') == 'new']
OLD = [e for e in E if e.get('genre') != 'new']
print(f'新着 {len(NEW)}件 / 既存 {len(OLD)}件')

def norm(s):
    return re.sub(r'[\s　・･]', '', unicodedata.normalize('NFKC', s or '')).lower()

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
DECO = re.compile(r'[●○★☆@※◎■]')

bad = collections.defaultdict(list)
for e in NEW:
    i, a = e['id'], e.get('artist', '')
    blob = ' '.join(str(e.get(k, '')) for k in ('artist', 'name', 'venue', 'dateLabel'))
    if FW.search(blob):
        bad['全角ローマ字/数字'].append(f"id{i} {a}")
    if '（）' in blob or '()' in blob:
        bad['空カッコ'].append(f"id{i} {a} | {e.get('venue','')} | {e.get('dateLabel','')}")
    if e.get('price'):
        bad['price入り(要2サイト一致)'].append(f"id{i} {a} price={e.get('price')}")
    if not e.get('verified'):
        bad['verified欠落'].append(f"id{i} {a}")
    d = e.get('date', '')
    for t in e.get('tickets', []):
        tp, sd, td = t.get('type', ''), t.get('startDate'), t.get('date')
        if DECO.search(tp):
            bad['飾り記号'].append(f"id{i} {a} | {tp}")
        if sd and td and sd > td:
            bad['日付逆転(発売>締切)'].append(f"id{i} {a} | {tp} | {sd} > {td}")
        if td and d and td > d:
            bad['締切>公演日'].append(f"id{i} {a} | {tp} | 締切{td} > 公演{d}")
        if td and td.startswith('2027') and 'R9' not in tp and 'R9' not in (t.get('dateLabel') or ''):
            bad['2027でR9表記なし'].append(f"id{i} {a} | {tp} | {td}")

# 重複（eventCd / 正規化名）— 既存とも突き合わせる
def cds(e):
    out = set()
    for u in [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets', [])]:
        if not u:
            continue
        mm = re.search(r'event(?:Bundle)?Cd=(\w+)', u)
        if mm:
            out.add(mm.group(1))
    return out

cd2 = collections.defaultdict(list)
nm2 = collections.defaultdict(list)
for e in E:
    for c in cds(e):
        cd2[c].append(e['id'])
    nm2[norm(e.get('artist', '')) + '|' + norm(e.get('venue', ''))].append(e['id'])

newids = {e['id'] for e in NEW}
for c, ids in cd2.items():
    if len(ids) > 1 and newids & set(ids):
        bad['eventCd重複'].append(f"{c} → id{ids}")
for k, ids in nm2.items():
    if len(ids) > 1 and newids & set(ids) and k.strip('|'):
        bad['名前+会場 重複'].append(f"{k} → id{ids}")

if not bad:
    print('\n✅ 異常なし')
for k, v in bad.items():
    print(f'\n🚨 {k} {len(v)}件')
    for x in v[:20]:
        print('   ', x)
    if len(v) > 20:
        print(f'    … 他{len(v)-20}件')
