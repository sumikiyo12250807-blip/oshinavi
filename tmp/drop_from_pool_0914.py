# -*- coding: utf-8 -*-
"""今朝投入した新着のうち、買えないと分かったものを新着プールから外す（まだサイトに出していない分・2026-09-14）。
EVENTS から消し、NEW_ORDER からも外し、logs/removed_2026-09-14.md に残す。改行は CRLF を保つ。
  8514 市川猿四郎さんに学ぶ 歌舞伎のみかた楽しみ方スーパー講座 横須賀＝ぴあ「この公演は延期になりました」（延期後の日程なし）
  9663 北九州聖楽研究会定期演奏会＝ぴあ「販売を終了致しました」（公演9/20）
  どちらも組み立て道具が状態の文言を読み損ねて「発売前」にしていた（道具は直した）。
使い方: python tmp/drop_from_pool_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
DROP = {
    8514: 'ぴあ「この公演は延期になりました」＝延期後の日程が出ていない',
    9663: 'ぴあ「販売を終了致しました」＝公演9/20・もう買えない',
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
    f.write('\n## 新着プールから外した（買えないと分かった・まだサイトに出していない分）\n\n')
    f.write('| id | 公演名 | 理由 | 確認用URL |\n|---|---|---|---|\n')
    for i, n, u, why in rows:
        f.write('| %s | %s | %s | %s |\n' % (i, n, why, u))
print('外した %d件（NEW_ORDER からも外した）' % len(rows))
