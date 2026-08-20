# -*- coding: utf-8 -*-
"""新着プール(genre:new)の目視QC支援。機械で拾える異常を全部出す。
 - 全角ローマ字/数字の残り（（）〜 は保護）[[feedback_newpool_fullwidth_halfwidth]]
 - 空カッコ会場 / venue空
 - 販売終了日 > 公演日（[[feedback_sale_end_cap_show_date]]）
 - 公演日が過去
 - バッジに公演日(M/D)が無い
 - 同一eventCdの重複、正規化名の重複
 - 2027年公演でR9年表記が無い
 - チケット0枠
"""
import re, json, io, sys, unicodedata, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-07-10'
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
news = [e for e in E if e.get('genre') == 'new']
print(f'genre:new {len(news)}件\n')
issues = collections.defaultdict(list)

def has_fullwidth(s):
    # 全角英数（（）〜／・は許容）
    return bool(re.search(r'[Ａ-Ｚａ-ｚ０-９]', s or ''))

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/（）()「」『』【】\-—]', '', s).lower()

cds = collections.Counter()
nms = collections.Counter()
for e in news:
    i, a = e['id'], e.get('artist', '')
    for u in re.findall(r'event(?:Bundle)?Cd=(\w+)', json.dumps(e, ensure_ascii=False)):
        cds[u] += 1
    nms[norm(a)] += 1
    if has_fullwidth(a):        issues['全角英数がartistに残る'].append(f'{i} {a}')
    if has_fullwidth(e.get('name', '')): issues['全角英数がnameに残る'].append(f'{i} {e.get("name","")}')
    v = e.get('venue') or ''
    if not v:                   issues['venue が空'].append(f'{i} {a}')
    if '（）' in v or '()' in v: issues['空カッコ会場'].append(f'{i} {a} / {v}')
    d = e.get('date') or ''
    if d and d < TODAY:         issues['公演日が過去'].append(f'{i} {a} / {d}')
    ts = e.get('tickets') or []
    if not ts:                  issues['チケット0枠'].append(f'{i} {a}')
    for t in ts:
        td = t.get('date') or ''
        ty = t.get('type') or ''
        if td and d and td > d and not t.get('saleUntilSoldOut'):
            issues['販売終了日が公演日より後'].append(f'{i} {a} / 締切{td} > 公演{d} / {ty}')
        if not re.search(r'\d{1,2}/\d{1,2}', ty):
            issues['バッジに公演日(M/D)が無い'].append(f'{i} {a} / {ty}')
        if has_fullwidth(ty):   issues['全角英数がバッジに残る'].append(f'{i} {a} / {ty}')
    if d.startswith('2027') and not any('R9年' in (t.get('type') or '') for t in ts):
        issues['2027公演だがR9年表記なし'].append(f'{i} {a} / {d}')

for u, c in cds.items():
    if c > 1: issues['同一eventCdが複数エントリ'].append(f'{u} x{c}')
for n, c in nms.items():
    if c > 1: issues['正規化名の重複'].append(f'{n} x{c}')

if not issues:
    print('✅ 機械チェックで異常なし')
for k, v in issues.items():
    print(f'--- {k} ({len(v)}件) ---')
    for x in v[:14]: print('   ', x)
    if len(v) > 14: print(f'    … 他 {len(v)-14}件')
    print()
