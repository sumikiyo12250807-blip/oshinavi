# -*- coding: utf-8 -*-
"""投入前の重複チェック（feedback_harvest_dedup_check）。
eventCd / eventBundleCd の一致＝確実な重複。名前は NFKC 正規化して完全一致/部分一致も見る。
"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

CD = re.compile(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)')


def cds(e):
    s = set()
    for u in [(e.get('links') or {}).get('pia') or ''] + [(t.get('url') or '') for t in (e.get('tickets') or [])]:
        s |= set(CD.findall(u))
    return s


def norm(s):
    return unicodedata.normalize('NFKC', s or '').replace(' ', '').replace('　', '').lower()


h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
OLD = json.loads(m.group(2))
NEW = json.load(open('tmp/entries_0815.json', encoding='utf-8'))

old_cd = {}
for e in OLD:
    for c in cds(e):
        old_cd.setdefault(c, []).append(e)
old_name = {}
for e in OLD:
    old_name.setdefault(norm(e.get('name')), []).append(e)

hits = []
for n in NEW:
    same_cd = []
    for c in cds(n):
        same_cd += old_cd.get(c, [])
    same_nm = old_name.get(norm(n.get('name')), [])
    if same_cd or same_nm:
        hits.append((n, same_cd, same_nm))

print('新着 %d件 / 既存 %d件' % (len(NEW), len(OLD)))
print('=== eventCd or 名前が既存と一致: %d件 ===' % len(hits))
for n, cd, nm in hits:
    print('  new id%s %s' % (n['id'], n['name'][:40]))
    for e in cd:
        print('     ↔ eventCd一致 既存 id%s %s' % (e['id'], e['name'][:40]))
    for e in nm:
        print('     ↔ 名前一致   既存 id%s %s | %s' % (e['id'], e['name'][:40], e.get('date')))

# 新着どうしの重複も見る
seen = {}
for n in NEW:
    k = norm(n.get('name'))
    seen.setdefault(k, []).append(n['id'])
dups = {k: v for k, v in seen.items() if len(v) > 1}
print('=== 新着どうしの同名: %d件 ===' % len(dups))
for k, v in dups.items():
    print('  ', v, k[:40])
