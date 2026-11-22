# -*- coding: utf-8 -*-
# 11/23 に上げる TikTok（11/26 発売 演歌と舞台のまとめ）の説明文 → コピーボタン付きページ tiktok_1123.html（x1121/mk_tiktok_page1122 の形）
import io
s = io.open('C:/Users/user/oshinavi/tmp/x1120/x/mk_tiktok_page1121.py', encoding='utf-8').read()
for a, b in (("tmp/x1120/x/", "tmp/x1122/x/"), ("tiktok_1121", "tiktok_1123"), ("TikTok 説明文 11/21", "TikTok 説明文 11/23"),
             ("TikTok 説明文（11/21 朝・夜の2本）", "TikTok 説明文（11/23・演歌と舞台）"),
             ("クラシックの動画は今書き出し中＝できたら Downloads に入るわ。", "動画は今書き出し中＝できたら Downloads に入るわ（入ったらお知らせするわね）。ポップスとロックの1本は、すちこの曲ができたら足すわ。")):
    assert a in s, a
    s = s.replace(a, b)
exec(compile(s, 'tp', 'exec'))
