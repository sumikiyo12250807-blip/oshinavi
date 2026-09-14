# -*- coding: utf-8 -*-
"""昼のヒールで「ぴあに買える枠ゼロ＝削除候補」になったエントリ（tmp/heal_stale.json の status=delete）のうち、
今日の日付の枠が画面に出ているもの（＝「本日発売」のまま出ていて押しても買えないかもしれない）を拾う（読むだけ・2026-09-14）。
画面に出ている＝soldout でなく、startDate<=今日 かつ date>=今日。
使い方: python tmp/heal_dels_today_0914.py
出力: tmp/heal_dels_today_0914.txt（idのカンマ区切り）
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
dels = [o['id'] for o in json.load(io.open('tmp/heal_stale.json', encoding='utf-8')) if o.get('status') == 'delete']
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
today_ids, old_ids = [], []
for i in dels:
    e = by.get(i)
    if not e:
        continue
    vis_today = [t for t in e.get('tickets') or []
                 if not t.get('soldout') and (t.get('startDate') or '') <= TODAY and (t.get('date') or '') >= TODAY
                 and 'pia.jp' in (t.get('url') or (e.get('links') or {}).get('pia') or '')]
    (today_ids if vis_today else old_ids).append(i)
    if vis_today:
        print('id%-5s %-30s ｜%s' % (i, (e.get('name') or '')[:30], ' ／ '.join(t['type'] for t in vis_today[:3])))
io.open('tmp/heal_dels_today_0914.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in today_ids))
print('削除候補 %d件 ＝ 画面に出ている枠あり %d件 ／ 画面にはもう出ていない %d件' % (len(dels), len(today_ids), len(old_ids)))
