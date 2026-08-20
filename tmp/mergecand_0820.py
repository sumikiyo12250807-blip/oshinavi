# -*- coding: utf-8 -*-
"""同名ヒット18件について、新候補と既存エントリを並べて「統合か新規か」を人が判断できる形で出す。
判断材料＝公演日・会場・都道府県・ぴあURL・枠の中身。"""
import re, json, sys, io, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

PAIRS = [(4740, 850), (4742, 3129), (4743, 1149), (4745, 741), (4748, 3035), (4749, 3526),
         (4750, 2500), (4751, 738), (4752, 3040), (4753, 1203), (4755, 950), (4758, 1028),
         (4759, 4189), (4763, 4249), (4764, 3501), (4773, 1835), (4775, 4711), (4777, 3775)]

built = {e['id']: e for e in json.load(io.open('tmp/built_0820.json', encoding='utf-8'))}
h = io.open('index.html', encoding='utf-8').read()
EVENTS = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}

out = []
for nid, oid in PAIRS:
    n, o = built.get(nid), EVENTS.get(oid)
    out.append("=" * 100)
    for tag, e in (('新候補 %d' % nid, n), ('既存   %d' % oid, o)):
        if not e:
            out.append("%s: 見つからない" % tag)
            continue
        out.append("%s %s" % (tag, e.get('artist')))
        out.append("    会場: %s" % e.get('venue'))
        out.append("    県  : %s / 千秋楽: %s" % (e.get('prefecture'), e.get('date')))
        out.append("    pia : %s" % ((e.get('links') or {}).get('pia') or ''))
        for t in e.get('tickets') or []:
            out.append("      - %s | date=%s | start=%s | url=%s" % (
                t.get('type'), t.get('date'), t.get('startDate'), (t.get('url') or '')[:70]))
    out.append("")
io.open('tmp/mergecand_0820.txt', 'w', encoding='utf-8').write("\n".join(out))
print('ok', len(PAIRS))
