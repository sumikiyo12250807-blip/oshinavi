# -*- coding: utf-8 -*-
# 頭の「明日 10/26(月) 発売 スポーツ」と後半の「oshinavi.jp」を画面の下に出す（道具の title / url の場面は上 330〜600 に書く＝DJの顔に掛かる）
#   spec の場面名 'shot:dj_title' / 'shot:dj_url' を shot_scene で受ける（badge_tap の後に install）。文字・光り方は道具の title / url と同じ
from PIL import ImageDraw
import oshimade_mv as M

Y_WHEN, Y_KIND = 1560, 1700   # 11/1 下のかぼちゃの列（1730〜）に掛けない
Y_URL, Y_TAG = 1560, 1700


def install(render_fn):
    G = render_fn.__globals__
    orig = G['shot_scene']
    fit = G['fit']

    def shot_scene(im, key, t, u, L, S):
        W = M.W
        if key in ('dj_title', 'dj_url') and S.get('char_pos'):     # 第2版：切り抜いたキャラを右下に（文字と歌詞より奥）
            M.paste_char(im, t, W / 2, 830, 570)   # 10/27 妖精＝下の文字（1640〜）に顔が掛からない高さ・歌詞の塊の下半分の後ろ
        if key == 'dj_title':
            M.glow_text(im, (W / 2, Y_WHEN), S['when'], fit(S['when'], int(40 + 50 * M.ease(u / 0.8)), 1000))
            M.glow_text(im, (W / 2, Y_KIND), S['kind'], int(60 + 60 * M.ease((u - 0.4) / 0.8)), grad=(M.GOLD, M.PINK), glow=M.PINK)
            return
        if key == 'dj_url':
            M.glow_text(im, (W / 2, Y_URL), 'oshinavi.jp', int(80 + 40 * M.ease(u / 0.5)), fill=M.WHITE, glow=M.WHITE)   # URLは光る白
            ImageDraw.Draw(im).text((W / 2, Y_TAG), '推しのチケット発売日、見逃さない', font=M.font(52), fill=M.WHITE, anchor='mm', stroke_width=6, stroke_fill=(90, 0, 140))
            return
        return orig(im, key, t, u, L, S)

    G['shot_scene'] = shot_scene
