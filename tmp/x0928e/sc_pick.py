import sys, random, json, re
sys.stdout.reconfigure(encoding='utf-8')
R = 'C:/Users/user/oshinavi/'
rows = [l.rstrip('\n').split('\t') for l in open(R + 'tmp/x0928e/sc_list.txt', encoding='utf-8')]
random.seed(928)
must_idx = ['24635', '24877', '24921']
pick = [r for r in rows if r[0] == 'IDX' and r[1] in must_idx]
pick += [r for r in rows if 'cluemetic-popup_ebisu' in r[2]]
def cat(r):
    f = r[9]; multi = int(r[7][2:]) > 1
    return (r[0], 'S' in f, 'X' in f, '-' in f, multi)
buckets = {}
for r in rows:
    if r in pick: continue
    buckets.setdefault(cat(r), []).append(r)
# one from each bucket first
for k in sorted(buckets):
    random.shuffle(buckets[k])
    pick.append(buckets[k].pop())
rest = [r for k in buckets for r in buckets[k]]
random.shuffle(rest)
# 配信 must: search name for 配信
haisin = [r for r in rest if '配信' in r[10] or 'オンライン' in r[10] or '配信' in r[5]]
if haisin: pick.append(haisin[0]); rest.remove(haisin[0])
multi_day = [r for r in rest if '〜' in (r[4] or '')]
pick += multi_day[:2]
for r in multi_day[:2]: rest.remove(r)
while len(pick) < 30: pick.append(rest.pop())
pick = pick[:30]
for r in pick: print('\t'.join(r[:10]), r[10][:50])
json.dump([{'src': r[0], 'id': r[1], 'url': r[2]} for r in pick], open(R + 'tmp/x0928e/sc_pick.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
