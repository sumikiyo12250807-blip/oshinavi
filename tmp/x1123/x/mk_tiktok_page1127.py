# -*- coding: utf-8 -*-
# TikTok（11/27 発売 J-POPとロックのまとめ）の説明文 → コピーボタン付きページ tiktok_1127.html（x1122/mk_tiktok_page1123 の形）
import io
s = io.open('C:/Users/user/oshinavi/tmp/x1120/x/mk_tiktok_page1121.py', encoding='utf-8').read()
for a, b in (("tmp/x1120/x/", "tmp/x1123/x/"), ("tiktok_1121", "tiktok_1127"), ("TikTok 説明文 11/21", "TikTok 説明文 11/27"),
             ("TikTok 説明文（11/21 朝・夜の2本）", "TikTok 説明文（11/27発売・J-POPとロック）"),
             ("クラシックの動画は今書き出し中＝できたら Downloads に入るわ。", "動画は Downloads の oshinavi_1127_jpoprock_matome.mp4（いまの登録の10行の版）よ。")):
    assert a in s, a
    s = s.replace(a, b)
exec(compile(s, 'tp', 'exec'))
