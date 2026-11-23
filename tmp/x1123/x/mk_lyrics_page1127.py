# -*- coding: utf-8 -*-
# 11/27 発売のまとめの歌詞2本（クラシック・J-POPとロック）→ lyrics_matome_1127.html（mk_lyrics_page1126 の形）
import io
s = io.open('C:/Users/user/oshinavi/tmp/x1120/x/mk_lyrics_page1124.py', encoding='utf-8').read()
s = s.replace("X = 'C:/Users/user/oshinavi/tmp/x1120/x/'", "X = 'C:/Users/user/oshinavi/tmp/x1123/x/'")
s = s.replace("S = [('suno_classic_1124.txt', '① 11/24(火) 発売 クラシックとおでかけ'), ('suno_live_1124.txt', '② 11/24(火) 発売 ライブ（J-POP・ロック・アイドル）')]",
              "S = [('suno_classic_1127.txt', '① 11/27(金) 発売 クラシック'), ('suno_live_1127.txt', '② 11/27(金) 発売 J-POPとロック')]")
a = s.index("note = ("); b = s.index("cards = []")
s = s[:a] + ("note = ('✅ 裏取り済み：名前・時刻・県（その日に発売になる受付の県）・先行かどうかを OSHINAVI の登録と1行ずつ機械で突き合わせて、食い違い0。LOSTAGE と Reol はその日に3県まとめて発売なので「ほか」にしたわ。'\n"
             "        '読みは Reol（れをる）・金子三勇士（かねこ みゆじ）を調べて確かめたわ。読みの出典が見つからない GOTCHAROCKA と 0.1gの誤算 は外したの。'\n"
             "        '11/25 はお笑いとスポーツ、11/26 は演歌と舞台・ポップスとロックだったから、今回はクラシックと J-POP・ロックにしたわ。歌詞だけをコピーしてね。')\n") + s[b:]
s = s.replace('まとめの歌詞 11/24', 'まとめの歌詞 11/27').replace('まとめの歌詞（11/24 発売）', 'まとめの歌詞（11/27 発売）').replace("'lyrics_matome_1124.html'", "'lyrics_matome_1127.html'")
assert 'suno_classic_1127' in s and 'lyrics_matome_1127.html' in s and 'suno_classic_1124' not in s
exec(compile(s, 'page1127', 'exec'))
