# -*- coding: utf-8 -*-
"""【投入前ゲート】build した新着候補が、既存エントリと同じアーティスト／同じ公演でないかを調べる。
2026-08-18 に、投入した50件のうち39件（午後の分は25件）が既存ツアーの分裂だったのを受けて恒久化。
 判定1: アーティスト名の正規化一致（記号・空白・全半角を潰す）
 判定2: ぴあの eventBundleCd / eventCd の一致（同じ売り場を二重登録していないか）
使い方: python tmp/dupcheck_built_0819.py tmp/built_0819.json
"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

SRC = sys.argv[1] if len(sys.argv) > 1 else 'tmp/built_0819.json'
built = json.load(open(SRC, encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・\-–—~〜"\'`()（）【】\[\]!！?？。、,.:：/／★☆]', '', s).lower()


def codes(e):
    out = set()
    for u in [(e.get('links') or {}).get('pia', '')] + [t.get('url', '') for t in (e.get('tickets') or [])]:
        for m in re.finditer(r'event(?:Bundle)?Cd=(\w+)', u or ''):
            out.add(m.group(1))
    return out


by_name = {}
for e in EVENTS:
    by_name.setdefault(norm(e.get('artist') or e.get('name')), []).append(e)
code_owner = {}
for e in EVENTS:
    for c in codes(e):
        code_owner.setdefault(c, []).append(e)

hit_name = hit_code = 0
for b in built:
    k = norm(b.get('artist') or b.get('name'))
    same = by_name.get(k) or []
    cs = codes(b)
    ccl = [o for c in cs for o in code_owner.get(c, [])]
    if same:
        hit_name += 1
        print('■名前一致 new=%d %s' % (b['id'], b['name'][:40]))
        for o in same:
            print('    ← 既存 id=%d %s (genre=%s, 千秋楽 %s)' % (o['id'], o['name'][:40], o.get('genre'), o.get('date')))
    if ccl:
        hit_code += 1
        print('■eventCd一致 new=%d %s' % (b['id'], b['name'][:40]))
        for o in {o['id']: o for o in ccl}.values():
            print('    ← 既存 id=%d %s' % (o['id'], o['name'][:40]))

print('=== 候補 %d件 / 名前一致 %d件 / eventCd一致 %d件 ===' % (len(built), hit_name, hit_code))
