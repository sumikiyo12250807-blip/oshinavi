# -*- coding: utf-8 -*-
"""2〜3日後（9/4・9/5）の発売から「箱の大きさ」で上位を選ぶ材料を作る。

台本ルール＝2〜3日後は5件くらいに絞って「他にも◯件以上あるわ」と丸める。
選び方は**箱の大きさ（会場のキャパ）**（2026-09-01 ユーザー指定）。
収容人数の辞書は持っていないので、会場名の型でスコアを付けて並べるだけ。
🚨最後に選ぶのは人（あたし）。このスクリプトは並べ替えの材料を出すだけ。
"""
import collections, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

RANK = [
    (100, r'ドーム|スタジアム|甲子園|神宮球場|さいたまスーパーアリーナ|横浜アリーナ|日本武道館'),
    (90,  r'アリーナ|ぴあアリーナ|パシフィコ横浜|幕張メッセ|インテックス大阪'),
    (80,  r'東京国際フォーラム|NHKホール|サントリーホール|東京文化会館|オーチャードホール|'
          r'Bunkamura|フェスティバルホール|東京芸術劇場|渋谷公会堂|LINE CUBE|中野サンプラザ|'
          r'昭和女子大学人見記念講堂|東京オペラシティ|すみだトリフォニーホール|ミューザ川崎'),
    (70,  r'大ホール|コンサートホール|メインホール|市民会館|文化会館|文化центр|県民ホール|'
          r'芸術劇場|市民ホール|公会堂|会館'),
    (60,  r'Zepp|ゼップ|Billboard Live|ビルボード|よみうりホール|イズミティ|'
          r'ヒューリックホール|シアター|劇場'),
    (40,  r'小ホール|ホール'),
    (20,  r'.'),
]


def score(v):
    for s, pat in RANK:
        if re.search(pat, v or ''):
            return s
    return 0


txt = open('tmp/x_material_0902.txt', encoding='utf-8').read()
cur_day = cur_b = None
rows = collections.defaultdict(list)
for ln in txt.split('\n'):
    m = re.match(r'# (.+) に発売開始', ln)
    if m:
        cur_day = m.group(1)
        continue
    m = re.match(r'【(.+?)】(\d+)組', ln)
    if m:
        cur_b = m.group(1)
        continue
    m = re.match(r'  (\d{1,2}:\d{2}) (.+?)／(.*?)(（先行）)?   \[id(\d+) / 公演(\S+) / (.*)\]$', ln)
    if m and cur_day and cur_b:
        t, name, pref, senko, i, show, venue = m.groups()
        rows[(cur_day, cur_b)].append(
            {'t': t, 'name': name, 'pref': pref, 'senko': bool(senko), 'id': i,
             'venue': venue, 'sc': score(venue)})

out = []
for (day, b), lst in rows.items():
    if day.startswith('明日'):
        continue
    out.append(f'\n=== {day} 【{b}】{len(lst)}組 … 箱の大きい順（上5件が候補）')
    for r in sorted(lst, key=lambda x: (-x['sc'], x['t']))[:8]:
        out.append(f"  [{r['sc']:>3}] {r['t']} {r['name']}／{r['pref']}"
                   f"{'（先行）' if r['senko'] else ''}  ＠{r['venue']}")
open('tmp/x_bighall_0902.txt', 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
print('wrote tmp/x_bighall_0902.txt')
for (day, b), lst in sorted(rows.items()):
    print(f'  {day} {b} … {len(lst)}組')
