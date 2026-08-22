# -*- coding: utf-8 -*-
"""新着プール(id4943-5042)の振り分け（2026-08-22）。

方針＝[[project_vendor_genre_autoassign]]の決定版：
  harvest時にぴあカテゴリから記憶した `_genre` を `genre` にそのまま移すだけ。
  **自分の音楽知識で再分類しない**（J-POP・ROCK は jpop 固定・rock/idol に細分しない）。
  人が判断するのは `_piaSub` が空 or 「その他」のものだけ → それは**振り分けずプールに残して相談**
  （[[feedback_new_pool_ok_before_assign]]／[[feedback_consultation_mark]]）。

適用後は `_genre`/`_extraGenres`/`_piaSub` を削除して genre を確定させる。
並び順・id は動かさない（[[feedback_new_list_order_lock]]）。
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ぴあの実カテゴリで上書きするもの（あたしの下書きは _piaSub が空で名前fallbackだった＝
# [[project_vendor_genre_autoassign]]の「人が確認するのは _piaSub 空/その他だけ」の対象）。
# 検証エージェントがぴあの詳細検索(sgフィルタ)で実カテゴリを特定してくれた。
OVERRIDE = {
    4960: ('jpop', 'ぴあ 音楽/J-POP・ROCK（bundleでサブが出ずsgフィルタで確定）'),
    5016: ('sports', 'ぴあ スポーツ/ゴルフ（同上）'),
}
# 花澤香菜は既存の前例（4242 神谷浩史・3582 水瀬いのり）に揃えて seiyuu を副で持たせる
EXTRA = {5021: ['seiyuu']}

HOLD = set()          # 相談に回す id（実行時に --hold で渡す）
args = sys.argv[1:]
if '--hold' in args:
    HOLD = {int(x) for x in args[args.index('--hold') + 1].split(',') if x.strip()}
APPLY = '--apply' in args

path = 'index.html'
# 🚨バイナリで読んで（＝\r\n をそのまま持ったまま）テキストモードで書き戻すと、
#   \n が \r\n に変換されて **\r\r\n** になる（2026-08-22 に5,508か所やらかして sort_guard に捕まった）。
#   テキストモードで読めば \r\n → \n に畳まれ、書き戻しで \r\n に戻るので釣り合う。
h = open(path, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

rows = []
moved = 0
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    if e['id'] in HOLD:
        rows.append((e['id'], e.get('name', ''), 'HOLD(相談)', e.get('_genre'), e.get('_piaSub'),
                     (e.get('links') or {}).get('pia', '')))
        continue
    ov = OVERRIDE.get(e['id'])
    g = ov[0] if ov else e.get('_genre')
    if not g:
        rows.append((e['id'], e.get('name', ''), 'HOLD(_genre無し)', None, e.get('_piaSub'),
                     (e.get('links') or {}).get('pia', '')))
        continue
    e['genre'] = g
    extra = list(e.get('_extraGenres') or []) + EXTRA.get(e['id'], [])
    extra = [x for x in dict.fromkeys(extra) if x != g]
    if extra:
        e['extraGenres'] = extra
    for k in ('_genre', '_extraGenres', '_piaSub'):
        e.pop(k, None)
    moved += 1
    rows.append((e['id'], e.get('name', ''), g, g, None, (e.get('links') or {}).get('pia', '')))

out = io.open('tmp/assign_result_0822.txt', 'w', encoding='utf-8')
out.write('振り分け %d件 / 相談に残す %d件\n\n' % (moved, len(rows) - moved))
for r in rows:
    out.write('%s | %s | %s | %s\n' % (r[0], r[1], r[2], r[5]))
out.close()
print('振り分け %d件 / 相談に残す %d件' % (moved, len(rows) - moved))

if APPLY:
    shutil.copyfile(path, path + '.bak_0822_assign')
    # 🚨 Windows のテキストモード 'w' で書くと \n が \r\n になる＝CRLF が保たれる
    #    （[[feedback_index_html_crlf_preserve]]。8/21 の assign2 と同じ書き戻し方）
    open(path, 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2)
        + m.group(3) + h[m.end():])
    print('適用した（backup: index.html.bak_0822_assign）')
else:
    print('（判定のみ。適用は --apply）')
