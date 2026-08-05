# -*- coding: utf-8 -*-
"""新着プール(genre:new 48件)を正式ジャンルへ確定する（2026-07-29バッチ）。

方針＝[[project_vendor_genre_autoassign]]「ぴあカテゴリをそのまま適用・自分で再分類しない」。
_piaSub が空だった子は、ぴあ実ページの<title>からカテゴリを取り直して判断した（推測しない）。
迷う子は主ジャンル＋extraGenres の両方方式（[[feedback_genre_both_when_unclear]]）。

index.html は CRLF。newline='' 無しで読み書きすると全行LF化して sort_guard が誤ブロックする
（[[feedback_index_html_crlf_preserve]]）。
"""
import json, re, sys, datetime

sys.stdout.reconfigure(encoding='utf-8')

# ぴあ実カテゴリに基づく上書き（id: (主ジャンル, extraGenres)）。
# 右のコメントは根拠＝ぴあ実ページ<title>のカテゴリ。
OVERRIDE = {
    3370: ('yougaku', []),           # 音楽/民族音楽
    3372: ('yougaku', []),           # 音楽/海外ROCK・POPS
    3375: ('yougaku', []),           # 音楽/海外ROCK・POPS
    3391: ('idol', ['jpop']),        # イベント/ショー・ファンイベント（出演=田村芽実）
    3392: ('kids', ['idol']),        # イベント/講演会・トークショー（藤本美貴・ファミリー向け）
    3393: ('hanabi', []),            # イベント/祭り・花火大会
    3394: ('hanabi', []),            # イベント/祭り・花火大会
    3395: ('fes', []),               # イベント/スクール・レジャー（屋外の酒まつり）
    3396: ('fes', []),               # イベント/スクール・レジャー（屋外の酒まつり）
    3402: ('dento', ['engeki']),     # 演劇/バレエ・ダンス だが実体は沖縄芝居＝古典芸能
    3407: ('anime', ['fes']),        # イベント/イベントその他（コスプレイベント・屋外）
    3408: ('anime', ['fes']),        # イベント/イベントその他（コスプレイベント・屋外）
    3409: ('art', []),               # イベント/博覧会・展示会・見本市
    3410: ('art', []),               # イベント/博覧会・展示会・見本市
    3417: ('art', []),               # アート/アート
    3418: ('art', []),               # アート/アート
}

PATH = r'C:\Users\user\oshinavi\index.html'
h = open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
assert m, 'EVENTS配列が見つからない'
EVENTS = json.loads(m.group(2))

# 現存ジャンル（フィルタボタン）を実物から取る＝存在しないジャンルを付けない
VALID = set(re.findall(r'data-genre="([a-z0-9.]+)"', h)) - {'all', 'new'}

changed, report = 0, []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    eid = e['id']
    if eid in OVERRIDE:
        g, extra = OVERRIDE[eid]
        src = 'ぴあカテゴリ再取得'
    else:
        g, extra = e.get('_genre'), list(e.get('_extraGenres') or [])
        src = '_genre'
    assert g in VALID, f'id{eid}: 未定義ジャンル {g!r}（フィルタボタンに無い）'
    for x in extra:
        assert x in VALID, f'id{eid}: 未定義のextraGenres {x!r}'
    e['genre'] = g
    if extra:
        e['extraGenres'] = extra
    else:
        e.pop('extraGenres', None)
    for k in ('_genre', '_extraGenres', '_piaSub', '_srcgenre'):
        e.pop(k, None)
    changed += 1
    report.append((eid, g, extra, src, (e.get('artist') or '')[:34]))

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
# 🚨 json.dumps は LF を吐く。newline='' で書くと変換されないので、この配列だけ LF のまま残り
# ファイルが CRLF/LF 混在になって sort_guard が誤ブロックする（[[feedback_index_html_crlf_preserve]]）。
# 元ファイルの改行に合わせてから差し込む。
if '\r\n' in h:
    new_arr = new_arr.replace('\r\n', '\n').replace('\n', '\r\n')
h2 = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]
# NEW_ORDER は空に（振り分け済み＝新着タブは空）
h2 = re.sub(r'const NEW_ORDER = \[[^\]]*\];', 'const NEW_ORDER = [];', h2)

bak = PATH + f'.bak_{datetime.date.today():%m%d}_assign'
open(bak, 'w', encoding='utf-8', newline='').write(h)
open(PATH, 'w', encoding='utf-8', newline='').write(h2)

import collections
print(f'=== 振り分け確定 {changed}件 (backup: {bak}) ===')
for eid, g, extra, src, nm in report:
    print(f'  id{eid} {g:<8}{("+" + ",".join(extra)) if extra else "":<10} [{src}] {nm}')
print('\n内訳: ' + str(dict(collections.Counter(r[1] for r in report))))
print('残り genre:new = %d件' % len([e for e in EVENTS if e.get('genre') == 'new']))
