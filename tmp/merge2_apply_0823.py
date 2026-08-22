# -*- coding: utf-8 -*-
"""reconcile が見つけた取りこぼし8枠を id3798 / id309 に取り込む（足すだけ）。
・3798 東京ホラー特区 … bundle 側にあった券種7つ（ギズモ／ジョー・ダンテ／ザック・ギャリガンほか）
・309  しまじろう     … 宮崎10/25公演。あわせて「その他11会場」の手作りバッジを
                        ぴあ実データ由来の正確な文言（〜12/27 17:00・対象県を明記）へ差し替える
"""
import re, json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

RB = {e['id']: e for e in json.load(io.open('tmp/rebuilt_0823.json', encoding='utf-8'))}
h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
BY = {e['id']: e for e in EVENTS}

log = []

# ── 3798 東京ホラー特区: bundle由来の券種を足す（url=None＝エントリのbundleに飛ぶ＝正しい売り場）
t = BY[3798]
have = {x.get('type') for x in t['tickets']}
add = 0
for x in RB[90001]['tickets']:
    if x.get('type') in have:
        continue
    t['tickets'].append(dict(x))
    have.add(x.get('type'))
    add += 1
log.append('id3798 枠+%d → 計%d' % (add, len(t['tickets'])))

# ── 309 しまじろう: 手作りバッジ「一般発売 その他11会場（5/23〜12/27公演）」を実データ版へ
t = BY[309]
OLD_GENERIC = '一般発売 その他11会場（5/23〜12/27公演）'
t['tickets'] = [x for x in t['tickets'] if x.get('type') != OLD_GENERIC]
have = {x.get('type') for x in t['tickets']}
add = 0
for x in RB[90002]['tickets']:
    if x.get('type') in have:
        continue
    t['tickets'].append(dict(x))
    have.add(x.get('type'))
    add += 1
log.append('id309  枠+%d（手作りバッジ1つを実データ版に差し替え） → 計%d' % (add, len(t['tickets'])))

for tid in (3798, 309):
    types = [x.get('type') for x in BY[tid]['tickets']]
    dup = [x for x in set(types) if types.count(x) > 1]
    if dup:
        print('🚨 SAME-BADGE id%d: %s' % (tid, dup))
        sys.exit(2)

NL = '\r\n' if '\r\n' in h else '\n'
io.open('index.html.bak_0823_merge2', 'w', encoding='utf-8', newline='').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('\n'.join(log))
print('OK')
