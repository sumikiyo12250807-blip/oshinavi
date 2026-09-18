# -*- coding: utf-8 -*-
"""背景の上でキャラを**踊らせる**縦動画を作る（1コマずつ描く・課金ゼロ）。

  python tools/chara_dance_video.py --bg tmp/mv/bg_oshinavi.png --chara tmp/mv/chara.png \
      --audio "<mp3>" --start 29.8 --dur 20 --out tmp/mv/dance.mp4

## 🚨これを作った理由（2026-09-18 ユーザー指摘）

はじめに作ったものは**止まった絵をsin波で滑らせただけ**で、ユーザーに
「ひどいわね　私が言った言葉半分も聞いてないわね」と言われた。**滑るのは踊るではない。**

ユーザーの指示（そのまま）＝
  「キャラは小さめに表示でアップにしないように」
  「画面を動き回ってもいいけどカメラに近づかないように　小さいまま」
  「おどるの　かわいく」「画面全体に動き回って」

## 踊りの作り（1枚の絵でも「踊っている」と見える要素を重ねる）

1. **跳ねる**＝拍に合わせて上下（放物線。着地で止まる）
2. **潰れ・伸び**＝着地で縦に潰して横に広げる／跳ぶ時は縦に伸ばす
   🚨**面積は変えない**（横×縦を打ち消す）＝**寄って見えない**＝「アップにしない」を守る
3. **傾く**＝拍ごとに左右へ振る（軸は足元。頭を振るように見える）
4. **向きを変える**＝進む方向に合わせて左右反転（踊りながら向きを変える感じ）
5. **画面全体を回る**＝四隅を含む道しるべ（waypoint）を順に回る。移動はイーズインアウト

⚠️大きさ（基準の高さ）は**最初から最後まで一定**。拡大の処理は1つも入れていない。
"""
import argparse
import io
import math
import os
import subprocess
import sys

import cv2
import imageio_ffmpeg
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
FF = imageio_ffmpeg.get_ffmpeg_exe()


def imread_any(path, flags=cv2.IMREAD_UNCHANGED):
    """🚨cv2.imread は日本語パスを開けない（Windows）＝bytesで読んで imdecode する。"""
    return cv2.imdecode(np.frombuffer(open(path, 'rb').read(), np.uint8), flags)


def ease(t):
    """0→1 をなめらかに（イーズインアウト）。"""
    return t * t * (3 - 2 * t)


def overlay(bg, fg, x, y):
    """透過PNGを背景に置く（はみ出しは切る）。"""
    H, W = bg.shape[:2]
    h, w = fg.shape[:2]
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    sub = fg[y0 - y:y1 - y, x0 - x:x1 - x]
    a = sub[..., 3:4].astype(np.float32) / 255.0
    bg[y0:y1, x0:x1] = (bg[y0:y1, x0:x1] * (1 - a) + sub[..., :3] * a).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bg', required=True)
    ap.add_argument('--chara', required=True)
    ap.add_argument('--audio', required=True)
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--dur', type=float, default=20)
    ap.add_argument('--out', default='tmp/mv/dance.mp4')
    ap.add_argument('--h', type=int, default=400, help='キャラの高さ(px)＝ずっとこの大きさ')
    ap.add_argument('--fps', type=int, default=25)
    ap.add_argument('--bpm', type=float, default=112, help='1分の拍数＝跳ねる速さ')
    a = ap.parse_args()

    bg0 = imread_any(a.bg, cv2.IMREAD_COLOR)
    H, W = bg0.shape[:2]
    ch0 = imread_any(a.chara)
    if ch0.shape[2] != 4:
        print('キャラは透過PNGで渡して'); return 2
    sc = a.h / ch0.shape[0]
    ch0 = cv2.resize(ch0, (max(1, int(ch0.shape[1] * sc)), a.h), interpolation=cv2.INTER_AREA)
    cw, chh = ch0.shape[1], ch0.shape[0]

    beat = 60.0 / a.bpm
    n = int(round(a.dur * a.fps))
    # 画面全体を回る道しるべ（四隅と真ん中・キャラが収まる範囲で）
    mx, my = 40, 120
    pts = [(mx, H - chh - my), (W - cw - mx, H - chh - my - 260), (W // 2 - cw // 2, my),
           (mx, my + 220), (W - cw - mx, H - chh - my), (W // 2 - cw // 2, H // 2 - chh // 2),
           (mx, H // 2 - chh // 2), (W - cw - mx, my)]
    seg = a.dur / len(pts)

    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    tmpv = a.out + '.silent.mp4'
    w = imageio_ffmpeg.write_frames(tmpv, (W, H), fps=a.fps, codec='libx264',
                                    quality=None, output_params=['-crf', '20', '-pix_fmt', 'yuv420p'],
                                    macro_block_size=1)
    w.send(None)
    for i in range(n):
        t = i / a.fps
        # ① どこへ向かうか（四隅を順に回る・イーズインアウト）
        k = int(t / seg) % len(pts)
        f = ease(min(1.0, (t - k * seg) / seg))
        x0, y0 = pts[k]
        x1, y1 = pts[(k + 1) % len(pts)]
        px = x0 + (x1 - x0) * f
        py = y0 + (y1 - y0) * f
        # ② 跳ねる（放物線・着地でいったん止まる）
        ph = (t % beat) / beat
        hop = -math.sin(math.pi * ph) ** 0.7 * (chh * 0.16)
        # ③ 潰れ・伸び（面積は変えない＝寄って見えない）
        land = max(0.0, math.cos(math.pi * ph))
        sy = 1.0 - 0.10 * land + 0.05 * math.sin(math.pi * ph)
        sx = 1.0 / sy
        # ④ 傾く（2拍で左右に振る）
        ang = 13.0 * math.sin(2 * math.pi * t / (beat * 2))
        # ⑤ 進む向きに合わせて左右反転
        flip = (x1 - x0) < 0

        img = ch0[:, ::-1] if flip else ch0
        nw, nh = max(1, int(cw * sx)), max(1, int(chh * sy))
        img = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_LINEAR)
        pad = int(max(nw, nh) * 0.35)
        img = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0))
        # 足元を軸に回す
        cy = img.shape[0] - pad - int(nh * 0.06)
        M = cv2.getRotationMatrix2D((img.shape[1] / 2, cy), ang, 1.0)
        img = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]),
                             flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))
        frame = bg0.copy()
        # 足元の影（跳ぶと小さく薄くなる＝跳んでいるのが分かる）
        sh = 1.0 - 0.45 * (abs(hop) / (chh * 0.16))
        ow = int(nw * 0.42 * sh)
        oh = max(3, int(nw * 0.10 * sh))
        ox = int(px + nw / 2)
        oy = int(y0 + (y1 - y0) * f + chh - 6)
        if 0 < ox < W and 0 < oy < H:
            ov = frame.copy()
            cv2.ellipse(ov, (ox, oy), (max(4, ow), oh), 0, 0, 360, (0, 0, 0), -1)
            cv2.addWeighted(ov, 0.30 * sh, frame, 0.70 + 0.30 * (1 - sh), 0, frame)
        overlay(frame, img, int(px - pad + (cw - nw) / 2), int(py + hop - pad + (chh - nh)))
        w.send(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    w.close()

    cmd = [FF, '-y', '-hide_banner', '-loglevel', 'error', '-i', tmpv,
           '-ss', '%.3f' % a.start, '-t', '%.3f' % a.dur, '-i', a.audio,
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest',
           '-movflags', '+faststart', a.out]
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode != 0:
        print('音を付けるところで落ちた:\n' + r.stderr.decode('utf-8', 'replace')[-800:])
        return 2
    os.remove(tmpv)
    print('できた: %s （%.1fMB・%.0f秒・キャラの高さ%dpx固定）'
          % (a.out, os.path.getsize(a.out) / 1e6, a.dur, a.h))
    return 0


if __name__ == '__main__':
    sys.exit(main())
