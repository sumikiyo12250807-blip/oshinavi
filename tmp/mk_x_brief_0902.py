# -*- coding: utf-8 -*-
"""Fableに渡す「その日の素材」を1枚にまとめる（2026-09-02 夜の便）。
渡すのは X_SCRIPT.md とこのファイルだけ（memoryは貼らない＝文章が痩せるので）。
名前は index.html から機械で写す（手で打ち直さない）。"""
import collections, re, sys
sys.stdout.reconfigure(encoding='utf-8')

BUCKETS = ['音楽', 'クラシック', 'エンタメ', 'おでかけ']
LEAD_ID = '5719'          # 主役枠＝ヒコロヒー
txt = open('tmp/x_material_0902.txt', encoding='utf-8').read()

cur_day = cur_b = None
rows = collections.defaultdict(list)
for ln in txt.split('\n'):
    m = re.match(r'# (.+) に発売開始', ln)
    if m:
        cur_day = m.group(1); continue
    m = re.match(r'【(.+?)】(\d+)組', ln)
    if m:
        cur_b = m.group(1); continue
    m = re.match(r'  (\d{1,2}:\d{2}) (.+?)／(.*?)(（先行）)?   \[id(\d+) / 公演(\S+) / (.*)\]$', ln)
    if m and cur_day and cur_b:
        t, name, pref, senko, i, show, venue = m.groups()
        rows[(cur_day, cur_b)].append(
            {'t': t, 'name': name, 'pref': pref, 'senko': bool(senko),
             'id': i, 'show': show, 'venue': venue})

RANK = [(100, r'ドーム|スタジアム|甲子園|神宮球場|さいたまスーパーアリーナ|横浜アリーナ|日本武道館'),
        (90, r'アリーナ|パシフィコ横浜|幕張メッセ|インテックス大阪'),
        (80, r'東京国際フォーラム|NHKホール|サントリーホール|東京文化会館|オーチャードホール|Bunkamura|'
             r'フェスティバルホール|東京芸術劇場|LINE CUBE|中野サンプラザ|東京オペラシティ|'
             r'すみだトリフォニーホール|ミューザ川崎'),
        (70, r'大ホール|コンサートホール|メインホール|市民会館|文化会館|県民ホール|芸術劇場|市民ホール|公会堂|会館'),
        (60, r'Zepp|Billboard Live|よみうりホール|ヒューリックホール|シアター|劇場'),
        (40, r'ホール'), (20, r'.')]


def sc(v):
    for s, p in RANK:
        if re.search(p, v or ''):
            return s
    return 0


def line(r):
    return '%s %s／%s%s' % (r['t'], r['name'], r['pref'], '（先行）' if r['senko'] else '')


L = ['# 今夜のX投稿の素材（2026-09-02 夜）', '',
     '予約は **20:01 から15分おき**（20:01 / 20:16 / 20:31 / 20:46 / 21:01）。', '',
     '## 書いてほしい本数と順番', '',
     '| # | 時刻 | 中身 |', '|---|---|---|',
     '| 1 | 20:01 | **主役枠＝ヒコロヒー**（明日発売の中でXフォロワー1位・19.8万） |',
     '| 2 | 20:16 | まとめ＝**音楽** |',
     '| 3 | 20:31 | まとめ＝**クラシック** |',
     '| 4 | 20:46 | まとめ＝**エンタメ**（落語・お笑い） |',
     '| 5 | 21:01 | まとめ＝**おでかけ**（スポーツ・アート） |', '',
     '「このあとの投稿では◯◯を並べるわね」の予告は、上の順番でつなぐこと（時刻は書かない）。', '']

# 主役枠
lead = None
for (d, b), lst in rows.items():
    for r in lst:
        if r['id'] == LEAD_ID and d.startswith('明日'):
            lead = r
if lead:
    L += ['---', '', '## 1本目：主役枠（ヒコロヒー）', '',
          '```', line(lead), f"公演 {lead['show']}／会場 {lead['venue']}", '```', '',
          '- Xのフォロワーは19.8万で、明日発売の顔ぶれの中でいちばん多い（これは選ぶための材料。本文には書かない）',
          '- **この枠は「先行」**。誰でも買えるようには書かない。',
          '- 単独公演のチケットだという事実だけを書く。芸風や人物の説明はしない（裏取りしていないので）。', '']

for b in BUCKETS:
    L += ['---', '', f'## まとめ枠：{b}', '', f'### 明日9/3(木)発売（この{len(rows[("明日9/3(木)", b)])}組を1件も落とさず全部並べる）', '', '```']
    for r in sorted(rows[('明日9/3(木)', b)], key=lambda x: (x['t'], x['name'])):
        L.append(line(r))
    L += ['```', '']
    for day in ('9/4(金)', '9/5(土)'):
        lst = sorted(rows[(day, b)], key=lambda x: (-sc(x['venue']), x['t']))
        if not lst:
            continue
        top = lst[:5]
        rest = len(lst) - len(top)
        L += [f'### {day}発売（全{len(lst)}組のうち、箱の大きい5件だけ出す。残り{rest}組は丸めて書く）', '', '```']
        for r in sorted(top, key=lambda x: (x['t'], x['name'])):
            L.append(line(r))
        L += ['```', '']

L += ['---', '', '## 数の丸め方（実数は書かない）', '',
      '「他にも◯組」と書くときは台本の丸め方に従うこと。10未満はそのままの数でよい。', '',
      '## 念のため', '',
      '- 名前はこのファイルから1文字も変えずに写すこと（読み仮名や別表記に置き換えない）',
      '- （先行）が付いている枠は、本文でも「先行」と分かるように書くこと',
      '- ここに無いイベントを足さない。ここにある名前を減らさない',
      ]
open('tmp/x_brief_0902.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('wrote tmp/x_brief_0902.md')
for b in BUCKETS:
    print('  %s … 明日 %d組 / 9/4 %d組 / 9/5 %d組'
          % (b, len(rows[('明日9/3(木)', b)]), len(rows[('9/4(金)', b)]), len(rows[('9/5(土)', b)])))
