"""index.html から指定idのエントリを UTF-8 でファイルに書き出す（コンソール文字化け回避）"""
import json, re, sys

sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

SRC = r'C:\Users\user\oshinavi\index.html'
OUT = r'C:\Users\user\oshinavi\tmp\peek_0802.txt'

events = extract_events_array(SRC)
byid = {e['id']: e for e in events}

ids = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else [1477, 966]
lines = []
for i in ids:
    lines.append(json.dumps(byid.get(i), ensure_ascii=False, indent=2))
    lines.append('-' * 60)

lines.append('=== 群馬の単独公演サンプル ===')
n = 0
for e in events:
    if e.get('prefecture') == '群馬' and 'ツアー' not in (e.get('venue') or ''):
        lines.append('id=%d | %s | %s | %s' % (e['id'], e.get('date'), e.get('dateLabel'), e.get('venue')))
        n += 1
        if n >= 8:
            break

open(OUT, 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote', OUT, 'ids', len(ids))
