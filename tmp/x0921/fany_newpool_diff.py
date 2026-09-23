# -*- coding: utf-8 -*-
"""FANYの一覧（fany_harvest の出力）から、9/21夜の新着の名前が出る公演を全部出して index.html と突き合わせる（読むだけ）。
名前＝青木マッチョ／OWV／空前メテオ／ジョックロック／例えば炎、と会場「NMB48劇場」・名前に「NMB48」。
突き合わせは公演単位＝申込URL /reception/<sales_id>/<performance_id> の performance_id（inject_fany と同じ）。
使い方: python tmp/x0921/fany_newpool_diff.py tmp/x0921/fany_newpool.json
出力: tmp/x0921/fany_newpool_diff.txt（一覧）／tmp/x0921/fany_newpool_missing.json（抜けだけの harvest 形＝build_fany_entries にそのまま渡せる）
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
KWS = ['青木マッチョ', 'OWV', '空前メテオ', 'ジョックロック', '例えば炎', 'NMB48']


def n(s):
    return unicodedata.normalize('NFKC', re.sub(r'<[^>]+>', '', s or '')).lower()


src = json.load(io.open(sys.argv[1], encoding='utf-8'))
h = io.open('index.html', encoding='utf-8', newline='').read()
have_perf = set(re.findall(r'fany\.lol/reception/\d+/(\d+)', h))

hits = {}
for p in src['performances']:
    blob = n(' '.join(str(p.get(k) or '') for k in ('name', 'performer_detail', 'venue_name')))
    kws = [k for k in KWS if n(k) in blob]
    if kws:
        hits[str(p['id'])] = (p, kws)

o = io.open('tmp/x0921/fany_newpool_diff.txt', 'w', encoding='utf-8')
missing = []
by_kw = {k: [0, 0] for k in KWS}
for pid, (p, kws) in sorted(hits.items(), key=lambda x: (x[1][0].get('performance_date') or '', x[0])):
    reg = pid in have_perf
    for k in kws:
        by_kw[k][0] += 1
        by_kw[k][1] += reg
    if not reg:
        missing.append(p)
    st = sorted({s.get('display_sales_status') for s in p.get('performance_sales') or []})
    o.write('%s perf%s ｜%s ｜%s ｜%s ｜%s ｜枠%d ｜%s ｜%s\n' % (
        '済' if reg else '★抜け', pid, n(p.get('performance_date')), (p.get('name') or '')[:50], p.get('venue_name'),
        ','.join(kws), len(p.get('performance_sales') or []), '/'.join(x or '' for x in st),
        'https://ticket.fany.lol/event/detail/%s' % p.get('event_id')))
o.write('\n名前ごと（公演数／登録済み）\n')
for k, (a, b) in by_kw.items():
    o.write('  %s %d／%d\n' % (k, a, b))
o.write('合計 公演%d／登録済み%d／抜け%d\n' % (len(hits), len(hits) - len(missing), len(missing)))
o.close()
out = dict(src)
out['performances'] = missing
out['genre_map'] = {k: v for k, v in (src.get('genre_map') or {}).items() if k in {str(p['id']) for p in missing}}
io.open('tmp/x0921/fany_newpool_missing.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False))
print('公演%d 登録済み%d 抜け%d' % (len(hits), len(hits) - len(missing), len(missing)))
