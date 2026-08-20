import sys, json
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

ev = extract_events_array(r'C:\Users\user\oshinavi\index.html')
new = [e for e in ev if e.get('genre') == 'new']
lines = ['=== genre:new %d件 ===' % len(new)]
for e in new:
    lines.append('id=%d | %s | %s | %s | _genre=%s | _piaSub=%s' % (
        e['id'], e.get('name'), e.get('date'), e.get('venue'),
        e.get('_genre'), e.get('_piaSub')))
open(r'C:\Users\user\oshinavi\tmp\newpool_0802.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print(len(new))
