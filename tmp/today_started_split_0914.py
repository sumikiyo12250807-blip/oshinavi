# -*- coding: utf-8 -*-
"""today_started_0914.py が拾った「〆切日に発売時刻がくっつく」枠を、売り場ごとに分ける（読むだけ）。
ぴあの枠＝heal_stale_deadlines --ids で取り直せる／e+の枠＝e+ の取り直しが要る（ぴあのヒールでは直らない）。
判定は「くっついている枠そのもの」の ticket.url（無ければエントリの links）で行う。
使い方: python tmp/today_started_split_0914.py
出力: tmp/today_started_pia_0914.txt ／ tmp/today_started_eplus_0914.txt ／ tmp/today_started_other_0914.txt（どれもidのカンマ区切り）
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

groups = {'pia': set(), 'eplus': set(), 'other': set()}
for e in ev:
    L = e.get('links') or {}
    for t in e.get('tickets') or []:
        sd = t.get('startDate') or ''
        if t.get('soldout') or not sd or sd > TODAY or not (t.get('date') or '') > TODAY:
            continue
        m = re.search(r'(\d{1,2}):(\d{2})発売$', t.get('type') or '')
        if not m:
            continue
        if sd == TODAY and (int(m.group(1)), int(m.group(2))) > (now.hour, now.minute):
            continue  # 今日の発売で時刻前＝まだ正しい
        u = t.get('url') or L.get('pia') or L.get('eplus') or L.get('rakuten') or L.get('lawson') or ''
        k = 'pia' if 'pia.jp' in u else 'eplus' if 'eplus.jp' in u else 'other'
        groups[k].add(e['id'])

for k, ids in groups.items():
    io.open('tmp/today_started_%s_0914.txt' % k, 'w', encoding='utf-8').write(','.join(str(i) for i in sorted(ids)))
    print('%-6s %d件: %s' % (k, len(ids), ','.join(str(i) for i in sorted(ids))))
