"""指定idの会場/日付/バッジをUTF-8ファイルに出して目視判断に使う。"""
import json
import re

IDS = [3426, 3435, 3436, 3441, 3454, 3455, 3464, 3465, 3466, 3467, 3468]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

out = []
for i in IDS:
    e = byid.get(i)
    if not e:
        out.append(f'id={i} 見つからない')
        continue
    out.append(f"id={i}  {e.get('artist')}")
    out.append(f"    genre={e.get('genre')} _genre={e.get('_genre')} _extra={e.get('_extraGenres')} _piaSub={e.get('_piaSub')}")
    out.append(f"    venue={e.get('venue')}  date={e.get('date')}  dateLabel={e.get('dateLabel')}")
    for t in e.get('tickets') or []:
        out.append(f"      枠: {t.get('type')}")
    out.append('')
open('tmp/peek_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/peek_0730.txt')
