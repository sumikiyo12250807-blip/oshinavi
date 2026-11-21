# -*- coding: utf-8 -*-
# 11/26 発売のまとめの歌詞2本（演歌と舞台・ポップスとロック）を1枚に・各本にコピーボタン → lyrics_matome_1126.html（mk_lyrics_page1124 の形）
import io
s = io.open('C:/Users/user/oshinavi/tmp/x1120/x/mk_lyrics_page1124.py', encoding='utf-8').read()
s = s.replace("X = 'C:/Users/user/oshinavi/tmp/x1120/x/'", "X = 'C:/Users/user/oshinavi/tmp/x1122/x/'")
s = s.replace("S = [('suno_classic_1124.txt', '① 11/24(火) 発売 クラシックとおでかけ'), ('suno_live_1124.txt', '② 11/24(火) 発売 ライブ（J-POP・ロック・アイドル）')]",
              "S = [('suno_enka_1126.txt', '① 11/26(木) 発売 演歌と舞台'), ('suno_pops_1126.txt', '② 11/26(木) 発売 ポップスとロック')]")
a = s.index("note = ("); b = s.index("cards = []")
s = s[:a] + ("note = ('✅ 裏取り済み：名前・時刻・県（その日に発売になる受付の県）・先行かどうかを OSHINAVI の登録と1行ずつ機械で突き合わせて、食い違い0。別の係の突き合わせも通したわ。'\n"
             "        '読みは 川中美幸・山本譲二・辰巳ゆうと・梅棒・前進座・林部智史・サカグチアミ・defspiral・May J. を調べて確かめたわ。読みの出典が見つからない ラムネ商店街 と Dazzling BAD は外したの。'\n"
             "        '11/25 はお笑いとスポーツだったから、今回は初めての演歌（＋舞台）と、ポップス・ロックに回したの。歌詞だけをコピーしてね。')\n") + s[b:]
s = s.replace('まとめの歌詞 11/24', 'まとめの歌詞 11/26').replace('まとめの歌詞（11/24 発売）', 'まとめの歌詞（11/26 発売）').replace("'lyrics_matome_1124.html'", "'lyrics_matome_1126.html'")
assert 'suno_enka_1126' in s and 'lyrics_matome_1126.html' in s and 'suno_classic_1124' not in s
exec(compile(s, 'page1126', 'exec'))
