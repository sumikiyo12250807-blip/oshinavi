"""削除候補の確認用URLを index.html から機械抽出（捏造禁止）"""
import sys, json
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

IDS = [172, 298, 389, 458, 670, 718, 1243, 1577, 2757, 3232]
events = {e['id']: e for e in extract_events_array(r'C:\Users\user\oshinavi\index.html')}

lines = []
for i in IDS:
    e = events[i]
    links = e.get('links') or {}
    url = links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('lawson') or '(URL無し)'
    vendor = ('ぴあ' if links.get('pia') else '楽天' if links.get('rakuten')
              else 'e+' if links.get('eplus') else 'ローチケ' if links.get('lawson') else '-')
    lines.append('%s | %s | %s | %s | %s | %s' % (i, e['name'], e.get('venue'), e.get('date'), vendor, url))

open(r'C:\Users\user\oshinavi\tmp\dellist_0802.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote', len(IDS))
