# -*- coding: utf-8 -*-
"""今日（9/15）の 12:00 より後に発売の枠を、エントリごとに並べる（読むだけ・2026-09-15夕）。
シフトの見張り（shift_guard）が「今日の最遅の当日発売は 21:00」と言ったので、どの枠かを確かめる。
使い方: python tmp/x0916/today_late_sales_0915.py
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
for e in ev:
    for t in e.get('tickets') or []:
        if t.get('startDate') != TODAY:
            continue
        m = re.search(r'(\d{1,2}):(\d{2})発売', t.get('type') or '')
        if not m or int(m.group(1)) * 60 + int(m.group(2)) <= 12 * 60:
            continue
        print('id%s ｜%s ｜%s ｜ genre=%s ｜ date=%s ｜ soldout=%s ｜ %s' % (
            e['id'], (e.get('name') or '')[:30], t.get('type'), e.get('genre'), t.get('date'),
            bool(t.get('soldout')), (t.get('url') or e.get('url') or '')[:70]))
