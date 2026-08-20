# -*- coding: utf-8 -*-
"""ジャンル「シャンソン(chanson)」を追加する（ユーザー指示 2026-08-17「ジャンル足す」）。

きっかけ＝ぴあカテゴリ「音楽/シャンソン」に対応先が無く、id4448/4476「愛の讃歌 ミュゼットで
散りばめる秋のシャンソンと映画音楽」を振り分けられなかった。
ジャンル追加はユーザー許可済みの作業（[[project_vendor_genre_autoassign]]）。
必要な対応は5か所（同memory）＝CSS / フィルターボタン / GENRE_LABEL / GENRE_GROUPS / GENRE_AMAZON_LINKS。
ボタンは必ず `.filter-btn[data-genre]` の形（[[feedback_filter_selector]]）。

🚨 CRLF保持（[[feedback_index_html_crlf_preserve]]）。

  python tmp/add_genre_chanson_0817.py [--apply]
"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
done, skip = [], []

EDITS = [
    # ①バッジの色。洋楽(#8c9eff)・ジャズ(#26a69a)の隣に置くので、かぶらない薔薇色にする
    ('CSS .genre-chanson',
     '    .genre-gourmet    { background: rgba(232,163,61,0.15);  color: #e8a33d;       border: 1px solid rgba(232,163,61,0.35); }\r\n',
     '    .genre-gourmet    { background: rgba(232,163,61,0.15);  color: #e8a33d;       border: 1px solid rgba(232,163,61,0.35); }\r\n'
     '    .genre-chanson    { background: rgba(197,109,167,0.15); color: #c56da7;       border: 1px solid rgba(197,109,167,0.35); }\r\n'),

    # ②フィルターボタン（音楽グループ・洋楽の隣）
    ('フィルターボタン',
     '        <button class="filter-btn" data-genre="yougaku">洋楽</button>\r\n',
     '        <button class="filter-btn" data-genre="yougaku">洋楽</button>\r\n'
     '        <button class="filter-btn" data-genre="chanson">シャンソン</button>\r\n'),

    # ③表示名
    ('GENRE_LABEL',
     '    classic: "クラシック", jazz: "ジャズ", enka: "演歌", dento: "伝統",\r\n',
     '    classic: "クラシック", jazz: "ジャズ", enka: "演歌", dento: "伝統",\r\n'
     '    chanson: "シャンソン",\r\n'),

    # ④「音楽すべて」で拾われるようにグループへ入れる（入れ忘れると音楽タブから消える）
    ('GENRE_GROUPS.music',
     '    music:   ["jpop","classic","rock","jazz","enka","yougaku","anime","idol","kpop","hiphop"],\r\n',
     '    music:   ["jpop","classic","rock","jazz","enka","yougaku","anime","idol","kpop","hiphop","chanson"],\r\n'),

    # ⑤グッズリンク（クラシック等と同じコンサート物）
    ('GENRE_AMAZON_LINKS',
     '      fanevent: PENLIGHT_AMAZON,\r\n',
     '      fanevent: PENLIGHT_AMAZON,\r\n'
     '      chanson:  CONCERT_AMAZON,\r\n'),
]

for name, old, new in EDITS:
    if 'chanson' in src and old.replace('\r\n', '') and new.split('\r\n')[-2] in src:
        skip.append((name, '既に入っている'))
        continue
    if src.count(old) != 1:
        skip.append((name, 'アンカーが %d 箇所（1でない）' % src.count(old)))
        continue
    src = src.replace(old, new, 1)
    done.append(name)

print('=== ジャンル chanson（シャンソン）の追加 ===')
for d in done:
    print('  ✅ %s' % d)
for n, why in skip:
    print('  ⚠️ %s … %s' % (n, why))

# 検算
checks = {
    'CSS': '.genre-chanson',
    'ボタン': 'class="filter-btn" data-genre="chanson"',
    'ラベル': 'chanson: "シャンソン"',
    'グループ': '"hiphop","chanson"',
    'Amazon': 'chanson:  CONCERT_AMAZON',
}
print()
for k, v in checks.items():
    print('  %-7s %s' % (k, '入った' if v in src else '❌入っていない'))
print()
print('CRLF %d → %d ／ LF単独 %d' % (before_crlf, src.count('\r\n'), src.count('\n') - src.count('\r\n')))

if APPLY and len(done) == 5:
    io.open('index.html.bak_0817_add_chanson', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました（backup: index.html.bak_0817_add_chanson）')
elif APPLY:
    print('❌ 5か所そろっていないので適用しない')
else:
    print('（判定のみ。適用するなら --apply）')
