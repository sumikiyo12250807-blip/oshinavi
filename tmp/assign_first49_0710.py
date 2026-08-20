# -*- coding: utf-8 -*-
"""7/10 ユーザーがチェック済みの前半46件(id2299-2348)だけジャンル振り分け。
後半(2349-2399・カウントダウン優先で追加投入)は genre:new のまま残す。
下書き_genre はぴあカテゴリ由来なので原則そのまま([[project_vendor_genre_autoassign]])。
人が直すのは _piaSub 空 / 音楽その他 のフォールバック誤りだけ。"""
import re, json, sys, io
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
LO, HI = 2299, 2348

override = {
    # _piaSub 空 → engeki に誤フォールバックしていた6件（全部音楽）
    2309: 'fes',      # 白山一里野音楽祭2026＝白山一里野高原 特設会場(屋外)の音楽祭
    2311: 'jpop',     # flumpool
    2315: 'anime',    # Animelo Summer Live 2026＝幕張メッセ(屋内)のアニソン。fes定義(屋外)非該当
    2323: 'fes',      # TREASURE05X 2026＝蒲郡ラグーナビーチ(屋外)・複数組
    2326: 'yougaku',  # FISHBONE＝米国バンド
    2331: 'fes',      # nobinobi 2026＝長井海の手公園ソレイユの丘(屋外)・DAY1/DAY2 複数組
    # _piaSub「音楽その他」→ fes に誤フォールバックしていた3件
    2303: 'classic',  # ケーシーハシモト＝テノール歌手。1部は中学校吹奏楽部演奏。屋内ホール
    2322: 'jpop',     # E.L.L.50周年スペシャルトーク＝名古屋のライブハウス。屋内・トーク
    2335: 'enka',     # 元気が出るムード音楽 昭和歌謡ノスタルジーコンサート
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
tally = Counter(); n = 0
for e in EVENTS:
    i = e['id']
    if e.get('genre') != 'new' or not (LO <= i <= HI):
        continue
    g = override.get(i, e.get('_genre'))
    if not g or g == 'new':
        print('!! unresolved', i, e.get('_genre')); continue
    if i in override:
        print(f'  [補正] {i} {e["artist"][:26]}  {e.get("_genre")} -> {g}')
    e['genre'] = g
    for k in ('_genre', '_piaSub', '_extraGenres'):
        e.pop(k, None)
    tally[g] += 1; n += 1

print(f'\n=== assigned {n} 件 ===')
for k, v in sorted(tally.items(), key=lambda x: -x[1]):
    print(f'   {k}: {v}')

# NEW_ORDER から振り分け済みidを除去（後半は残す）
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', h)
cur = [x.strip() for x in mo.group(1).split(',') if x.strip()]
rest = [x for x in cur if not (LO <= int(x) <= HI)]
out = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
out = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\g<1>[' + ', '.join(rest) + r']\2', out, count=1)
print(f'NEW_ORDER {len(cur)} -> {len(rest)}件（後半のみ残す）')
if DRY:
    print('(DRY)')
else:
    open('index.html.bak_0710_assign_first', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(out)
    print('written (backup: index.html.bak_0710_assign_first)')
