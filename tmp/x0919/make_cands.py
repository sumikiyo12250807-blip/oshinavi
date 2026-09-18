# -*- coding: utf-8 -*-
"""pia_days_01_real.txt の「本当の抜け」から、ぴあ再導出の候補リストを2つ作る（2026-09-18 夜）。

  ① 足し込み用＝既存エントリのぴあURL（links.pia＋各ticket.url）で引き直す
  ② 新規用＝報告に出ている未登録URL（名前の一致も無い分だけ）

🚨 名前が一致する既存があるなら**新規にしない**＝ツアーは1エントリ（[[feedback_tour_consolidate]]）。
   その場合は既存のURLに、報告の未登録URLも足して引く（会場別URLを持つツアー）。

  python tmp/x0919/make_cands.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
EV = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))}

txt = io.open('tmp/x0919/pia_days_01_real.txt', encoding='utf-8').read()
txt = txt.split('=== 見かけ')[0]
blocks = re.findall(r'^(\d{4}-\d{2}-\d{2}) (.*?) \| .*?\n    (.*?)\n    (.*?)$', txt, re.M)

merge, new = {}, {}
for iso, artist, tail, note in blocks:
    m = re.search(r'id([\d,]+)', note)
    url = re.search(r'(https?://\S+)', tail)
    if m:
        ids = [int(x) for x in m.group(1).split(',')]
        tgt = ids[0]
        d = merge.setdefault(tgt, {'newid': tgt, 'artist': EV[tgt].get('artist') or artist, 'urls': []})
        for u in [(EV[tgt].get('links') or {}).get('pia') or ''] + \
                 [t.get('url') or '' for t in EV[tgt].get('tickets') or []]:
            if u and u not in d['urls']:
                d['urls'].append(u)
        if url and url.group(1) not in d['urls']:
            d['urls'].append(url.group(1))
    elif url:
        d = new.setdefault(artist, {'newid': 900000 + len(new), 'artist': artist, 'urls': []})
        if url.group(1) not in d['urls']:
            d['urls'].append(url.group(1))

io.open('tmp/x0919/cands_merge.json', 'w', encoding='utf-8').write(
    json.dumps(list(merge.values()), ensure_ascii=False, indent=1))
io.open('tmp/x0919/cands_new.json', 'w', encoding='utf-8').write(
    json.dumps(list(new.values()), ensure_ascii=False, indent=1))
print('足し込み %d件（URL計%d）／新規 %d件' % (
    len(merge), sum(len(v['urls']) for v in merge.values()), len(new)))
for v in new.values():
    print('  新規 %s | %s' % (v['artist'], v['urls'][0]))
