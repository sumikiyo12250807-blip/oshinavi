"""既存エントリのジャンル値を集計（新着の下書きジャンルが実在するか確認する）"""
import sys, collections
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

ev = extract_events_array(r'C:\Users\user\oshinavi\index.html')
c = collections.Counter(e.get('genre') for e in ev)
for k, v in c.most_common():
    print('%-10s %d' % (k, v))
print('---- 新着の下書き _genre が既存に無いもの ----')
new = [e for e in ev if e.get('genre') == 'new']
for g in sorted(set(e.get('_genre') for e in new)):
    print('%-10s %s' % (g, 'あり' if c.get(g) else '🚨既存に無い'))
