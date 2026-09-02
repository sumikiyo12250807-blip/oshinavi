# -*- coding: utf-8 -*-
"""e+新着のジャンルを、別エージェントの判定で確定する。

機械の下書き（名前fallback）は engeki 90件＝「判定できなかったものの受け皿」に落ちていて
下書きとして使えなかった。エージェントは会場と名前を1件ずつ見て、必要な分は実際に調べている
ので、そちらを採る。**判定できなかった `?` は振り分けずプールに残す**
（feedback_new_pool_ok_before_assign／feedback_genre_both_when_unclear）。

  python tmp/apply_eplus_genre_0902.py [--apply]
"""
import re, json, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
SRC = 'tmp/eplus_genre_agent_0902.md'

VALID = {'jpop', 'classic', 'rock', 'jazz', 'enka', 'yougaku', 'anime', 'idol', 'kpop',
         'hiphop', 'chanson', 'hougaku', 'musicetc', 'engeki', 'musical', 'dento',
         'seiyuu', '2.5ji', 'circus', 'owarai', 'kaidan', 'dinnershow', 'aisatsu',
         'youtuber', 'vtuber', 'fanevent', 'magic', 'sports', 'art', 'kids', 'fes',
         'hanabi', 'gourmet', 'gakusai'}

judged, unknown, bad = {}, [], []
for ln in open(SRC, encoding='utf-8'):
    m = re.match(r'^\|\s*(\d{3,5})\s*\|(.*?)\|\s*([^|]+?)\s*\|', ln)
    if not m:
        continue
    i, name, g = int(m.group(1)), m.group(2).strip(), m.group(3).strip().strip('`')
    if g == '?':
        unknown.append((i, name[:40]))
    elif g in VALID:
        judged[i] = g
    else:
        bad.append((i, name[:40], g))

print(f'判定 {len(judged)}件 / 保留(?) {len(unknown)}件 / 未知のジャンル {len(bad)}件')
if bad:
    for x in bad[:10]:
        print('  🚨知らないジャンル:', x)
c = collections.Counter(judged.values())
print('  内訳:', dict(c.most_common()))
print('  保留:', [f'{i} {n}' for i, n in unknown])

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
EV = json.loads(m.group(2))
pool = {e['id'] for e in EV if e.get('genre') == 'new'}
miss = [i for i in judged if i not in pool]
if miss:
    print('🚨プールに無いid（無視する）:', miss[:10])
n = 0
for e in EV:
    if e['id'] in judged and e.get('genre') == 'new':
        e['_genre'] = judged[e['id']]
        n += 1
print(f'\n_genre を当てる件数 {n}  APPLY={APPLY}')
if not APPLY:
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', nl)
open('index.html.bak_0902_epgenre2', 'w', encoding='utf-8', newline='').write(src)
open('index.html', 'w', encoding='utf-8', newline='').write(
    src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
open('tmp/eplus_hold_ids_0902.txt', 'w', encoding='utf-8').write(
    ','.join(str(i) for i, _ in unknown))
print('applied（backup: index.html.bak_0902_epgenre2）')
print('保留idを tmp/eplus_hold_ids_0902.txt に出した')
