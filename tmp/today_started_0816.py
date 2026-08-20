# -*- coding: utf-8 -*-
"""「今日発売開始して、もう受付中になっているはずの枠」を洗い出す。
条件＝startDate == today かつ date > today（＝発売日と締切日が別＝隠れ枠ヒールの対象外）。
このtypeは「M/D HH:MM発売」形のまま残るので、画面が締切日に発売時刻をくっつけて
「〜8/23 10:00」のように出してしまう（2026-08-16 ユーザーのスクショで発覚）。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TODAY = datetime.date.today().isoformat()
raw = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))

rows = []
for e in EVENTS:
    hit = []
    for t in e.get('tickets') or []:
        sd, d = t.get('startDate'), t.get('date') or ''
        if sd == TODAY and d > TODAY and not t.get('soldout'):
            hit.append(t)
    if hit:
        rows.append((e, hit))

print("=== 今日(%s)発売開始・締切は先 の枠を持つエントリ %d件 / %d枠 ===" % (
    TODAY, len(rows), sum(len(h) for _, h in rows)))
for e, hit in rows:
    print("id%-5s %-30s %s" % (e['id'], (e.get('artist') or '')[:28], e['links'].get('pia') or ''))
    for t in hit:
        print("      - %s | date=%s" % (t.get('type'), t.get('date')))
print()
print("ids=" + ",".join(str(e['id']) for e, _ in rows))
