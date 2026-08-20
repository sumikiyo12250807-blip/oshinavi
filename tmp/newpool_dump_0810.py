"""新着プール(genre:new)の下書きジャンルを一覧化（振り分け相談用）"""
import sys, json, collections
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

ev = extract_events_array(r'C:\Users\user\oshinavi\index.html')
new = [e for e in ev if e.get('genre') == 'new']
lines = ['=== genre:new %d件 ===' % len(new)]
need = []
for e in new:
    sub = e.get('_piaSub') or ''
    mark = ''
    if not sub or 'その他' in sub:
        mark = '  ⚠️人の判断'
        need.append(e)
    lines.append('id=%d | _genre=%s | extra=%s | _piaSub=%s%s\n    %s / %s / %s / %s' % (
        e['id'], e.get('_genre'), e.get('_extraGenres'), sub or '(空)', mark,
        e.get('artist'), e.get('name'), e.get('venue'), e.get('date')))

lines.append('')
lines.append('=== 下書きジャンル分布 ===')
for k, v in collections.Counter(e.get('_genre') for e in new).most_common():
    lines.append('%s: %d' % (k, v))
lines.append('')
lines.append('=== 人の判断が要る %d件 ===' % len(need))
for e in need:
    lines.append('id=%d | %s | %s' % (e['id'], e.get('name'), e.get('venue')))

open(r'C:\Users\user\oshinavi\tmp\newpool_dump_0810.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('new', len(new), 'need-human', len(need))
