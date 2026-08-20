# -*- coding: utf-8 -*-
"""音楽グループに受け皿ジャンル「その他」(musicetc) を追加する。
ユーザー指示 2026-08-17「じゃ音楽というジャンル作る？何にも引っかからないジャンルをそこに収める」
→「音楽のところに その他 の方がいいね」。

きっかけ＝ぴあの「音楽/音楽その他」は名前ベースfallbackに落ち、fes や engeki に化けていた
（4427 サックス侍デュオ／4456 AGLEE／4485 荒川夏蓮）。受け皿があれば嘘のジャンルを付けずに済む。

⚠️キーを "music" にしないのは GENRE_GROUPS.music（音楽グループの定義）と紛らわしいため。
   グループ側は data-group 属性から引くので衝突はしないが、読む人が混乱する。
🚨 CRLF保持（[[feedback_index_html_crlf_preserve]]）／ボタンは .filter-btn[data-genre] 形（[[feedback_filter_selector]]）。

  python tmp/add_genre_musicetc_0817.py [--apply]
"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv
src = io.open('index.html', encoding='utf-8', newline='').read()
before_crlf = src.count('\r\n')
done, skip = [], []

EDITS = [
    ('CSS .genre-musicetc',
     '    .genre-chanson    { background: rgba(197,109,167,0.15); color: #c56da7;       border: 1px solid rgba(197,109,167,0.35); }\r\n',
     '    .genre-chanson    { background: rgba(197,109,167,0.15); color: #c56da7;       border: 1px solid rgba(197,109,167,0.35); }\r\n'
     '    .genre-musicetc   { background: rgba(150,158,170,0.15); color: #96a1aa;       border: 1px solid rgba(150,158,170,0.35); }\r\n'),

    # 受け皿なので音楽グループの最後に置く
    ('フィルターボタン',
     '        <button class="filter-btn" data-genre="hiphop">ヒップホップ</button>\r\n',
     '        <button class="filter-btn" data-genre="hiphop">ヒップホップ</button>\r\n'
     '        <button class="filter-btn" data-genre="musicetc">その他</button>\r\n'),

    ('GENRE_LABEL',
     '    chanson: "シャンソン",\r\n',
     '    chanson: "シャンソン", musicetc: "その他",\r\n'),

    ('GENRE_GROUPS.music',
     '"kpop","hiphop","chanson"],\r\n',
     '"kpop","hiphop","chanson","musicetc"],\r\n'),

    ('GENRE_AMAZON_LINKS',
     '      chanson:  CONCERT_AMAZON,\r\n',
     '      chanson:  CONCERT_AMAZON,\r\n'
     '      musicetc: CONCERT_AMAZON,\r\n'),
]

for name, old, new in EDITS:
    if src.count(old) != 1:
        skip.append((name, 'アンカーが %d 箇所（1でない）' % src.count(old)))
        continue
    src = src.replace(old, new, 1)
    done.append(name)

print('=== ジャンル musicetc（表示「その他」・音楽グループ）の追加 ===')
for d in done:
    print('  ✅ %s' % d)
for n, why in skip:
    print('  ⚠️ %s … %s' % (n, why))

checks = {
    'CSS': '.genre-musicetc',
    'ボタン': 'class="filter-btn" data-genre="musicetc"',
    'ラベル': 'musicetc: "その他"',
    'グループ': '"chanson","musicetc"',
    'Amazon': 'musicetc: CONCERT_AMAZON',
}
print()
for k, v in checks.items():
    print('  %-7s %s' % (k, '入った' if v in src else '❌入っていない'))
print()
print('CRLF %d → %d ／ LF単独 %d' % (before_crlf, src.count('\r\n'), src.count('\n') - src.count('\r\n')))

if APPLY and len(done) == 5:
    io.open('index.html.bak_0817_add_musicetc', 'w', encoding='utf-8', newline='').write(
        io.open('index.html', encoding='utf-8', newline='').read())
    io.open('index.html', 'w', encoding='utf-8', newline='').write(src)
    print('適用しました（backup: index.html.bak_0817_add_musicetc）')
elif APPLY:
    print('❌ 5か所そろっていないので適用しない')
else:
    print('（判定のみ。適用するなら --apply）')
