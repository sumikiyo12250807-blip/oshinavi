# -*- coding: utf-8 -*-
"""ジャンル「映画」(movie) を新設する（2026-09-13・ユーザー「⑤映画ジャンル作って」）。

なぜ＝ぴあの「映画/邦画」「映画/洋画」「映画祭」が engeki（演劇タブ）に落ちていて、
上映会が演劇を探しに来た人のノイズになっていた（memory feedback_genre_pia_asis_and_other）。
ぴあの区分に行き先が無いならジャンルを作る、が2026-08-27のユーザー決定。

🚨ジャンルを1つ増やすときに触る5か所（全部やらないと画面に出ない）＋ぴあの対応表
  ① index.html GENRE_LABEL      ② index.html GENRE_GROUPS（ento）
  ③ index.html フィルターボタン   ④ index.html CSS .genre-movie
  ⑤ tools/build_ai_page.py GENRE_LABEL
  ⑥ tools/build_pia_entries.py PIA_GENRE_MAP（邦画・洋画・映画祭・映画その他 → movie）

使い方: python tmp/add_movie_genre_0913.py [--apply]
"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

# 🚨同じファイルを何度も直すので、読み込みは1回だけにして「いまの中身」を持ち回る。
#   patch のたびに読み直すと、最後の1個しか反映されない（書き戻しで上書きされる）。
orig, cur = {}, {}


def patch(path, old, new, note, newline=''):
    if path not in cur:
        orig[path] = cur[path] = io.open(path, encoding='utf-8', newline=newline).read()
    n = cur[path].count(old)
    if n != 1:
        print('❌ %s: 目印が %d 箇所（1でないと危ない）… %s' % (path, n, note))
        sys.exit(1)
    cur[path] = cur[path].replace(old, new, 1)
    print('✅ %s … %s' % (note, path))


# ① GENRE_LABEL（舞台挨拶の行に足す）
patch('index.html',
      '    aisatsu: "舞台挨拶", dinnershow: "ディナーショー", art: "イベントアート",',
      '    aisatsu: "舞台挨拶", dinnershow: "ディナーショー", art: "イベントアート",\n'
      '    /* 2026-09-13 ユーザー「映画ジャンル作って」＝ぴあの「映画/邦画・洋画・映画祭・映画その他」が\n'
      '       engeki(演劇)に落ちていて、上映会が演劇タブのノイズになっていた。舞台挨拶(aisatsu)はそのまま。 */\n'
      '    movie: "映画",',
      '① GENRE_LABEL に movie を足す')

# ② GENRE_GROUPS の ento（舞台挨拶のとなり）
patch('index.html',
      'ento:    ["owarai","kaidan","dinnershow","aisatsu","youtuber","vtuber","fanevent","magic","talkshow"],',
      'ento:    ["owarai","kaidan","dinnershow","movie","aisatsu","youtuber","vtuber","fanevent","magic","talkshow"],',
      '② GENRE_GROUPS(ento) に movie を足す')

# ③ フィルターボタン（舞台挨拶の前）
patch('index.html',
      '        <button class="filter-btn" data-genre="aisatsu">舞台挨拶</button>',
      '        <button class="filter-btn" data-genre="movie">映画</button>\n'
      '        <button class="filter-btn" data-genre="aisatsu">舞台挨拶</button>',
      '③ フィルターボタンを足す')

# ④ CSS（舞台挨拶の次の行に）
patch('index.html',
      '    .genre-aisatsu    { background: rgba(220,100,180,0.15); color: #e066b4;       border: 1px solid rgba(220,100,180,0.35); }',
      '    .genre-aisatsu    { background: rgba(220,100,180,0.15); color: #e066b4;       border: 1px solid rgba(220,100,180,0.35); }\n'
      '    .genre-movie      { background: rgba(126,87,194,0.15);  color: #9575cd;       border: 1px solid rgba(126,87,194,0.35); }',
      '④ CSS .genre-movie を足す')

# ⑤ SSR 側（無いと ai.html に生の movie が出る）
patch('tools/build_ai_page.py',
      '    "owarai": "お笑い", "musical": "ミュージカル", "aisatsu": "舞台挨拶",',
      '    "owarai": "お笑い", "musical": "ミュージカル", "aisatsu": "舞台挨拶",\n'
      '    # 2026-09-13 新設＝ぴあの「映画/邦画・洋画・映画祭・映画その他」の行き先（index.html と必ず一致させる）\n'
      '    "movie": "映画",',
      '⑤ build_ai_page の GENRE_LABEL に足す')

# ⑥ ぴあの対応表（4つとも engeki / musicetc から movie へ）
#    ⏭「ライブビューイング」は engeki のまま＝中継元が舞台のことが多い（ユーザーに確認してから動かす）
patch('tools/build_pia_entries.py',
      "    '邦画': ('engeki', None),                   # 上映イベント。既存「舞台映像上映」(997/2839)と揃える",
      "    '邦画': ('movie', None),                    # 2026-09-13 ユーザー「映画ジャンル作って」＝演劇タブから独立",
      '⑥ PIA_GENRE_MAP 邦画 → movie')
patch('tools/build_pia_entries.py',
      "    '映画その他': ('musicetc', None),",
      "    '映画その他': ('movie', None),               # 2026-09-13 映画タブができたのでそちらへ（大分類のタブがあるものはそこへ）",
      '⑥ PIA_GENRE_MAP 映画その他 → movie')
patch('tools/build_pia_entries.py',
      "    '映画祭': ('engeki', None),",
      "    '映画祭': ('movie', None),",
      '⑥ PIA_GENRE_MAP 映画祭 → movie')
patch('tools/build_pia_entries.py',
      "    '洋画': ('engeki', None),                   # わたしは、ダニエル・ブレイクで確認（「邦画」と揃える）",
      "    '洋画': ('movie', None),                    # 「邦画」と揃える",
      '⑥ PIA_GENRE_MAP 洋画 → movie')

# ⑦ 回帰テストの期待値も一緒に直す（直さないと --selftest が落ちる）
patch('tools/build_pia_entries.py',
      "    assert genre_from_subcat('映画', '映画その他', 'なにかの上映') == ('musicetc', None)",
      "    assert genre_from_subcat('映画', '映画その他', 'なにかの上映') == ('movie', None)",
      '⑦ selftest 映画その他 の期待値')
patch('tools/build_pia_entries.py',
      "    assert genre_from_subcat('映画', '洋画', 'わたしは、ダニエル・ブレイク') == ('engeki', None)",
      "    assert genre_from_subcat('映画', '洋画', 'わたしは、ダニエル・ブレイク') == ('movie', None)",
      '⑦ selftest 洋画 の期待値')

if not APPLY:
    print('\n（--apply で適用）')
    sys.exit(0)

for path in cur:
    io.open(path + '.bak_0913_movie', 'w', encoding='utf-8', newline='').write(orig[path])
    io.open(path, 'w', encoding='utf-8', newline='').write(cur[path])
    print('書き戻した:', path)
print('\n✅ 全部書き換えたわ（それぞれ .bak_0913_movie を残した）')
