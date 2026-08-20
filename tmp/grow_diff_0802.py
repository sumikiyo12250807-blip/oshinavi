"""育成の前後で枠がどう動いたかを機械で突き合わせる（適用前バックアップとの差分）"""
import sys
sys.path.insert(0, r'C:\Users\user\oshinavi\tools')
from check_expired import extract_events_array

BEF = r'C:\Users\user\oshinavi\index.html.bak_0802_pre_grow'
AFT = r'C:\Users\user\oshinavi\index.html'

b = {e['id']: e for e in extract_events_array(BEF)}
a = {e['id']: e for e in extract_events_array(AFT)}

gain, loss, samecnt = [], [], 0
for eid, ea in a.items():
    eb = b.get(eid)
    if not eb:
        continue
    nb, na = len(eb.get('tickets') or []), len(ea.get('tickets') or [])
    if na > nb:
        gain.append((eid, ea.get('artist'), nb, na, eb.get('date'), ea.get('date')))
    elif na < nb:
        loss.append((eid, ea.get('artist'), nb, na))
    else:
        samecnt += 1

tb = sum(len(e.get('tickets') or []) for e in b.values())
ta = sum(len(e.get('tickets') or []) for e in a.values())

L = ['育成 前後差分  エントリ %d / 総枠 %d → %d (+%d)' % (len(a), tb, ta, ta - tb),
     '枠が増えたエントリ %d / 減った %d / 変化なし %d' % (len(gain), len(loss), samecnt), '']
L.append('=== 増えた（多い順）===')
for r in sorted(gain, key=lambda x: -(x[3] - x[2])):
    L.append('id=%d %s  %d→%d (+%d)  千秋楽 %s→%s' % (r[0], r[1], r[2], r[3], r[3] - r[2], r[4], r[5]))
L.append('')
L.append('=== 🚨減った（あってはいけない）===')
for r in loss:
    L.append('id=%d %s  %d→%d' % r)

open(r'C:\Users\user\oshinavi\tmp\grow_diff_0802.txt', 'w', encoding='utf-8').write('\n'.join(L))
print('総枠 %d -> %d (+%d) / 増%d 減%d' % (tb, ta, ta - tb, len(gain), len(loss)))
