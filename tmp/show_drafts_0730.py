"""genre:new の下書きジャンル(_genre/_extraGenres/_piaSub)を一覧化してUTF-8ファイルに出す。
コンソールは文字化けするので必ずファイル経由で読む（feedback_no_mojibake_japanese_read）。"""
import json
import re
import sys

sys.path.insert(0, 'tools')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
if not m:
    raise SystemExit('EVENTS 配列が見つからない')
EVENTS = json.loads(m.group(2))

news = [e for e in EVENTS if e.get('genre') == 'new']
news.sort(key=lambda e: e['id'])

lines = []
lines.append(f'genre:new 件数 = {len(news)}')
tally = {}
for e in news:
    g = e.get('_genre') or ''
    tally[g or '(空)'] = tally.get(g or '(空)', 0) + 1
lines.append('下書き集計: ' + ' / '.join(f'{k}{v}' for k, v in sorted(tally.items(), key=lambda x: -x[1])))
lines.append('')
lines.append('id    | _genre        | _extraGenres | _piaSub                | name')
lines.append('-' * 110)
for e in news:
    lines.append('{:<5} | {:<13} | {:<12} | {:<22} | {}'.format(
        e['id'],
        e.get('_genre') or '(空)',
        ','.join(e.get('_extraGenres') or []) or '-',
        e.get('_piaSub') or '(空)',
        (e.get('artist') or '')[:46],
    ))

# NEW_ORDER の中身も確認（並び順配列）
mo = re.search(r'const\s+NEW_ORDER\s*=\s*(\[[^\]]*\])', h)
if mo:
    order = json.loads(mo.group(1))
    lines.append('')
    lines.append(f'NEW_ORDER 件数 = {len(order)}')
    ids = [e['id'] for e in news]
    lines.append('NEW_ORDER == id昇順か: ' + ('YES' if order == sorted(ids) else f'NO (差分あり) order先頭5={order[:5]}'))
else:
    lines.append('')
    lines.append('NEW_ORDER が見つからない')

open('tmp/drafts_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote tmp/drafts_0730.txt  lines=%d' % len(lines))
