# -*- coding: utf-8 -*-
"""「〆切日に発売時刻がくっつく」型を探す（読むだけ・2026-09-12 昼）。
条件＝ startDate == 今日 かつ date > 今日 かつ 券種名が「M/D HH:MM発売」で終わる（かつ売り切れでない）。
画面は券種名の時刻と date を合成して「〜締切日 発売時刻」と嘘の表示をする（memory feedback_harvest_today_sale_enddate 2026-08-16項）。
隠れ枠ヒールは startDate == date の枠しか見ないので拾えない → 見つかったエントリに heal_stale_deadlines --ids を当てる。
🚨発売時刻がまだ来ていない枠は、ぴあもまだ発売前＝取り直しても変わらない（夜の分は夜に回す）。
使い方: python tmp/today_started_0912.py
出力: tmp/today_started_ids_0912.txt（発売時刻を過ぎた枠を持つid）
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
past, later = {}, {}
for e in ev:
    for t in e.get('tickets') or []:
        if t.get('soldout') or t.get('startDate') != TODAY or not (t.get('date') or '') > TODAY:
            continue
        m = re.search(r'(\d{1,2}):(\d{2})発売$', t.get('type') or '')
        if not m:
            continue
        hhmm = (int(m.group(1)), int(m.group(2)))
        bucket = past if hhmm <= (now.hour, now.minute) else later
        bucket.setdefault(e['id'], []).append('%s（締切 %s）' % (t.get('type'), t.get('date')))
print('発売時刻を過ぎた枠を持つエントリ %d件 ／ 発売時刻がまだ先のエントリ %d件' % (len(past), len(later)))
for i, ts in sorted(past.items()):
    print('  id%s: %s' % (i, ' ／ '.join(ts[:3]) + (' ほか%d枠' % (len(ts) - 3) if len(ts) > 3 else '')))
io.open('tmp/today_started_ids_0912.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in sorted(past)))
