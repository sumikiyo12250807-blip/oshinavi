# -*- coding: utf-8 -*-
"""削除から外した2件の公演日を事実の会期に直す（ぴあ実ページで確認済み・9/22朝）。
  id3757 くるま蓮見ペア＝配信の販売が 9/30 21:00 まで（配信期間 〜9/30 23:59）
  id7009 文豪LETTERS＝10月公演 10/7〜10/9 北とぴあ ドームホール（〜10/4 23:59 販売期間中）
"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

e = by[3757]
e['date'] = '2026-09-30'
e['dateLabel'] = '2026年8月3日(月)〜2026年9月30日(水) 東京'

e = by[7009]
e['date'] = '2026-10-09'
e['dateLabel'] = '2026年9月21日(月)〜2026年10月9日(金) 東京 北とぴあ ドームホール'
for t in e['tickets']:
    if not t.get('url'):
        t['url'] = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670721'
if not (e.get('links') or {}).get('pia'):
    e['links']['pia'] = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670721'

for i in (3757, 7009):
    print(i, by[i]['date'], by[i]['dateLabel'], [t.get('url') for t in by[i]['tickets']])
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
