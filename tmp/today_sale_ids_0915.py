# -*- coding: utf-8 -*-
"""今日発売の枠（startDate が今日・券種名が「M/D HH:MM発売」で終わる・売り切れでない）を持つぴあのエントリの id を出す（読むだけ・2026-09-15 昼）。
全体ヒール（157件）でなく、今日発売で締切が出た分だけを取り直すため。発売時刻を過ぎた枠だけ数える。
追加で、今朝さわった171件の照合（tmp/recon_touched_0915.txt）で MISSING／STALE／❌ が出た id も足す。
使い方: python tmp/today_sale_ids_0915.py
出力: tmp/today_sale_ids_0915.txt（カンマ区切り）
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
now = datetime.datetime.now()
TODAY = now.date().isoformat()
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
ids, later = set(), set()
for e in ev:
    for t in e.get('tickets') or []:
        if t.get('soldout') or (t.get('startDate') or '') != TODAY:
            continue
        m = re.search(r'(\d{1,2}):(\d{2})発売$', t.get('type') or '')
        if not m:
            continue
        url = t.get('url') or (e.get('links') or {}).get('pia') or ''
        if 'pia.jp' not in url:
            continue
        (ids if (int(m.group(1)), int(m.group(2))) <= (now.hour, now.minute) else later).add(e['id'])
flag = set()
try:
    txt = io.open('tmp/recon_touched_0915.txt', encoding='utf-8').read()
    flag = {int(x) for x in re.findall(r'^(?:❌|🚨|💤) id=(\d+)', txt, re.M)}
except OSError:
    pass
flag.discard(4272)  # 後日販売の見かけ（手で直した）
alls = sorted(ids | flag)
io.open('tmp/today_sale_ids_0915.txt', 'w', encoding='utf-8').write(','.join(map(str, alls)))
print('今日発売で時刻を過ぎた枠を持つ %d件 ／ まだ時刻前 %d件 ／ 照合で引っかかった %d件 ／ 合わせて %d件 → tmp/today_sale_ids_0915.txt' % (
    len(ids), len(later - ids), len(flag), len(alls)))
