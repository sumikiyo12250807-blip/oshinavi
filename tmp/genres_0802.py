import sys, collections, json
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

ev = extract_events_array(r'C:\Users\user\oshinavi\index.html')
c = collections.Counter(e.get('genre') for e in ev)
x = collections.Counter(g for e in ev for g in (e.get('extraGenres') or []))
out = ['=== genre ===']
out += ['%s: %d' % (k, v) for k, v in c.most_common()]
out += ['=== extraGenres ===']
out += ['%s: %d' % (k, v) for k, v in x.most_common()]
open(r'C:\Users\user\oshinavi\tmp\genres_0802.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok', len(ev))
