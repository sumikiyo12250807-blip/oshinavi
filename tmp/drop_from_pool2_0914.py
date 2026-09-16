# -*- coding: utf-8 -*-
"""今朝投入した新着のうち、ぴあで今は売っていないと分かった3件を新着プールから外す（まだサイトに出していない分・2026-09-14）。
EVENTS から消し、NEW_ORDER からも外し、logs/removed_2026-09-14.md に残す。改行は CRLF を保つ。
  9316 トヨタ産業技術記念館・あいち航空ミュージアム共通観覧券＝ぴあ「現在、お取り扱いしておりません。」
  9318 トヨタ博物館・あいち航空ミュージアム共通入館券＝ぴあ「現在、お取り扱いしておりません。」
  9350 名古屋港水族館とポートビル3施設共通入館券＝ぴあ「この公演は現在販売を見合わせています」
  3件とも通年券（4/1〜3/31）で、組み立て道具が状態欄の文言を読めず「4/1発売」の発売前にしていた（道具は直した）。
使い方: python tmp/drop_from_pool2_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DROP = {
    9316: 'ぴあ「現在、お取り扱いしておりません。」＝今は売っていない',
    9318: 'ぴあ「現在、お取り扱いしておりません。」＝今は売っていない',
    9350: 'ぴあ「この公演は現在販売を見合わせています」＝今は売っていない',
}
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}
rows = []
for i, why in DROP.items():
    e = by.get(i)
    assert e, 'id%s が無い' % i
    assert e.get('genre') == 'new', 'id%s は新着プールに居ない（振り分け済み）＝ここでは消さない' % i
    rows.append((i, e.get('name') or '', (e.get('links') or {}).get('pia') or '', why))
    print('外す id%s %s | %s' % (i, (e.get('name') or '')[:40], why))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
left = [e for e in events if e['id'] not in DROP]
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(left, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
order = [int(x) for x in mo.group(1).split(',') if x.strip()]
out = out[:mo.start()] + 'const NEW_ORDER = [%s];' % ', '.join(str(x) for x in order if x not in DROP) + out[mo.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
with io.open('logs/removed_%s.md' % datetime.date.today().isoformat(), 'a', encoding='utf-8') as f:
    f.write('\n## 新着プールから外した（ぴあで今は売っていない通年券・まだサイトに出していない分）\n\n')
    f.write('| id | 公演名 | 理由 | 確認用URL |\n|---|---|---|---|\n')
    for i, n, u, why in rows:
        f.write('| %s | %s | %s | %s |\n' % (i, n, why, u))
print('外した %d件（NEW_ORDER からも外した）' % len(rows))
