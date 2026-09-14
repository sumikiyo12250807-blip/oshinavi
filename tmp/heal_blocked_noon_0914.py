# -*- coding: utf-8 -*-
"""昼の「〆切日に発売時刻」ヒール（--ids）で安全弁が止めた6件について、登録の枠（今日以降）と
取り直した枠（tmp/heal_ids.json）を並べる（読むだけ・2026-09-14）。
消えるはずだった枠が「券種名の書き方が変わっただけ」か「ぴあで本当に無い」かを見分けるため。
使い方: python tmp/heal_blocked_noon_0914.py
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
IDS = [549, 5155, 5332, 5411, 7326, 8405]
src = io.open('index.html', encoding='utf-8').read()
by = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
built = {o['id']: o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))}
for i in IDS:
    e, o = by[i], built.get(i) or {}
    print('=== id%s %s' % (i, (e.get('name') or '')[:40]))
    for t in e.get('tickets') or []:
        if (t.get('date') or '') >= TODAY:
            print('  登録  %s ｜date %s start %s%s ｜%s' % (t.get('type'), t.get('date'), t.get('startDate') or '-',
                                                       ' 売切' if t.get('soldout') else '', (t.get('url') or '')[-40:]))
    for t in o.get('tickets') or []:
        print('  取直  %s ｜date %s start %s ｜%s' % (t.get('type'), t.get('date'), t.get('startDate') or '-', (t.get('url') or '')[-40:]))
