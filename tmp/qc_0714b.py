# -*- coding: utf-8 -*-
"""新着50件(2605-2654)の機械QC: 全角/空カッコ/飾り記号/日付逆転/重複/R9年/verified/価格"""
import io, json, re, unicodedata

s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\]);', s, re.S)
ev = json.loads(m.group(1))
new = [e for e in ev if 2655 <= e['id'] <= 2704]
old = [e for e in ev if e['id'] < 2655]

L = []
FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
DECO = re.compile(r'[●○★☆◎@※◆■▲]')

# 既存のeventCd/名前
def cds(e):
    t = json.dumps(e, ensure_ascii=False)
    return set(re.findall(r'event(?:Bundle)?Cd=(b?\d+)', t))

old_cds = set()
for e in old:
    old_cds |= cds(e)
old_names = {}
for e in old:
    key = unicodedata.normalize('NFKC', (e.get('name') or '')).lower().replace(' ', '')
    old_names.setdefault(key, e['id'])

seen_cd = {}
for e in new:
    i = e['id']
    nm = e.get('name') or ''
    vn = e.get('venue') or ''
    # 全角
    for f in ('name', 'venue', 'dateLabel', 'artist'):
        v = e.get(f) or ''
        if FW.search(v):
            L.append('%d 全角ローマ字/数字 %s=%s' % (i, f, v))
    # 空カッコ
    if re.search(r'[（(]\s*[）)]', vn + nm + (e.get('dateLabel') or '')):
        L.append('%d 空カッコ venue=%s' % (i, vn))
    # 飾り記号 / 日付逆転
    ed = e.get('date') or ''
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if DECO.search(ty):
            L.append('%d 飾り記号 ticket=%s' % (i, ty))
        td = t.get('date') or ''
        sd = t.get('startDate')
        if sd and td and sd > td:
            L.append('%d 日付逆転 start=%s > end=%s (%s)' % (i, sd, td, ty))
    # R9年: 2027年以降の公演はバッジ表記にR9/R10が要る
    if ed >= '2027-01-01':
        lab = json.dumps(e.get('tickets'), ensure_ascii=False) + (e.get('dateLabel') or '')
        if 'R9' not in lab and 'R10' not in lab and '2027' not in lab:
            L.append('%d R9年表記なし date=%s' % (i, ed))
    # verified
    if not e.get('verified'):
        L.append('%d verified無し' % i)
    # 価格
    if e.get('price'):
        L.append('%d price有り(要出典確認) %s' % (i, e['price']))
    # 重複(既存)
    for c in cds(e):
        if c in old_cds:
            L.append('%d eventCd重複(既存) %s' % (i, c))
        if c in seen_cd:
            L.append('%d eventCd重複(新着内 id%d) %s' % (i, seen_cd[c], c))
        seen_cd[c] = i
    key = unicodedata.normalize('NFKC', nm).lower().replace(' ', '')
    if key in old_names:
        L.append('%d 名前重複(既存 id%d) %s' % (i, old_names[key], nm))

with io.open('tmp/qc_0714b_result.txt', 'w', encoding='utf-8') as f:
    f.write('新着 %d件 QC\n' % len(new))
    if not L:
        f.write('=== 異常なし（間違い0）===\n')
    else:
        f.write('=== 要確認 %d件 ===\n' % len(L))
        for x in L:
            f.write(x + '\n')
print('done')
