# -*- coding: utf-8 -*-
"""締切がまだ先なのにぴあで買えない枠のうち、1枠ずつ読んで「予定枚数終了」だった枠に売り切れの印を付ける（2026-09-15 昼）。
根拠＝tmp/stale13_slotstatus_0915.md（heal_blocked_slotstatus_1805.py の出力）の「[売り切れ]」の行＝
      券種の頭の言葉・県・公演日で合わせたぴあの行が全部「予定枚数終了」だった枠。
消さない（memory feedback_soldout_keep_visible）。券種名は1文字も変えない。すでに印のある枠は触らない。
「[買える行あり]」「[該当行なし]」の枠は触らない。改行は CRLF を保つ。
使い方: python tmp/mark_sold_stale13_0915.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv

want = {}
cur = None
for line in io.open('tmp/stale13_slotstatus_0915.md', encoding='utf-8').read().splitlines():
    m = re.match(r'^## id(\d+) ', line)
    if m:
        cur = int(m.group(1))
        continue
    m = re.match(r'^- \[売り切れ\] (.*?) ｜締切 (\S+)｜', line)
    if m and cur:
        want.setdefault(cur, []).append((m.group(1), m.group(2)))

src = io.open('index.html', encoding='utf-8', newline='').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(mm.group(2))
by = {e['id']: e for e in events}
done, miss = 0, []
for i, rows in sorted(want.items()):
    e = by.get(i)
    for ty, d in rows:
        hit = [t for t in (e.get('tickets') if e else []) or [] if t.get('type') == ty and (t.get('date') or '') == d]
        if len(hit) != 1:
            miss.append((i, ty, len(hit)))
            continue
        t = hit[0]
        if t.get('soldout'):
            continue
        t['soldout'] = True
        t['soldoutSince'] = TODAY
        done += 1
        print('  印 id%-5s %s' % (i, ty))
for i, ty, n in miss:
    print('  ⚠️ 合う枠が %d個＝触らない id%s %s' % (n, i, ty))
print('売り切れの印 %d枠 ／ 合わず %d枠' % (done, len(miss)))
if not APPLY:
    print('（--apply で書き込み）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:mm.start()] + mm.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + mm.group(3) + src[mm.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
