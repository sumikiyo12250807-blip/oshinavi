# -*- coding: utf-8 -*-
# 歌詞の出し方（matome1026s/kara_style.py の塊の入れ替え＋matome1021o/kara_style.py の明るい背景の色）
#   ・歌詞を2〜4行の塊（spec の chunks＝make_spec.py）にまとめ、小節の頭で塊ごと 0.25 秒のクロスフェードで入れ替える
#   ・塊が出ている間は動かさない。歌った所から色が変わる「なぞり」だけ
#   ・背景が明るい黄色（クローバーの動画）＝黒い帯なし・字を暗く：まだ＝濃紺（20,10,40）／歌った＝えんじ（170,0,40）・縁は白の太め＋うっすら影
#     （10/20 すちこ「字を暗くすればいいんじゃないの？」）
#   ・タップの場面（'low'）だけは下の暗い帯の中＝白／黄・縁は濃紺（matome1026s と同じ）
#   tools/shuyaku_video.karaoke を render の globals で差し替える（道具は書き換えない）
from PIL import Image, ImageDraw, ImageFilter
import oshimade_mv as M

SIZE, MAXW, GAP = 96, 960, 1.55
XF = 0.25
CY_NORMAL, CY_LOW = 1185, 1640   # 11/13 すちこ：5行の塊の上の端がキャラの足もとにかかる＝塊を 1120→1185 に下げる（5行の時は行の間を 1.55→1.35 に詰める・字の大きさは同じ）
NAVY, ENJI, WHITE = (20, 10, 40), (170, 0, 40), (255, 255, 255)
YEL = (255, 228, 0)


def install(render_fn, S):
    G = render_fn.__globals__
    CH = S['chunks']

    def draw_chunk(im, t, c, alpha):
        d = ImageDraw.Draw(im)
        low = c.get('low')
        if low:   # タップの場面は下の暗い帯の中＝白／黄・縁は濃紺
            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)
        else:     # 11/20 背景 242696 は黒×えんじのダイヤ柄（暗い）＝白／黄・縁は濃紺（11/17 J-POP と同じ）
            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)
        rows = []
        for toks in c['lines']:     # toks＝[言葉, 歌う時刻, 後ろに空白を置くか]
            txt = ''.join(w + (' ' if s else '') for w, _, s in toks)
            rows.append((toks, G['fit'](txt, SIZE, MAXW)))
        lh = int(SIZE * (1.35 if len(rows) >= 5 else GAP))
        cy = c.get('cy') or (CY_LOW if low else CY_NORMAL)   # 11/13 締めの塊は cy を持つ（下の段に下りてくる4人の頭に重ねない）
        y0 = cy - (len(rows) - 1) * lh / 2
        if low:   # 11/13 タップの場面の3行（売り場まで／案内するのは／おしなび）が「発売日のバッジをタップ」（帯 1400＋60）に重なった＝1行目は 1545 より下から
            y0 = max(y0, 1565)
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
        sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
        dl, ds = ImageDraw.Draw(lay), ImageDraw.Draw(sh)
        for r, (toks, sz) in enumerate(rows):
            f = M.font(sz)
            sp = d.textlength(' ', font=f)
            ws = [d.textlength(w, font=f) for w, _, _ in toks]
            tw = sum(ws) + sp * sum(1 for _, _, s in toks[:-1] if s)
            x = M.W / 2 - tw / 2
            y = y0 + r * lh
            stw = max(12, sz // 6)
            for (w, ta, s), wd in zip(toks, ws):
                col = done if t >= ta else todo
                ds.text((x + 6, y + 7), w, font=f, fill=shadow, anchor='lm', stroke_width=stw, stroke_fill=shadow)
                dl.text((x, y), w, font=f, fill=col + (255,), anchor='lm', stroke_width=stw, stroke_fill=stroke + (255,))
                x += wd + (sp if s else 0)
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        for L in (sh, lay):
            if alpha < 1.0:
                L.putalpha(L.getchannel('A').point(lambda v: int(v * alpha)))
            im.paste(L, (0, 0), L)

    def karaoke(im, t, segs):
        for c in CH:
            if c['show'] - XF / 2 <= t < c['hide'] + XF / 2:
                a = min(1.0, (t - (c['show'] - XF / 2)) / XF, ((c['hide'] + XF / 2) - t) / XF)
                if a > 0:
                    draw_chunk(im, t, c, max(0.0, min(1.0, a)))

    G['karaoke'] = karaoke
