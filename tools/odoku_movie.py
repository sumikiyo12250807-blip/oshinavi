# -*- coding: utf-8 -*-
"""お毒姐さんの朗読動画をローカルだけで作る（課金ゼロ）。

なぜ自前合成か＝Veo/MiniMaxのAPIは無料枠が無く、あたし(Claude)がコマンドから
毎日回せるのはローカル合成だけ（2026-08-04調査）。おまけに
  ・声を自分で選べる＝Hailuoの「見た目から声を決める」問題が消える
  ・尺の制限が無い＝X投稿の全文を読ませられる（AI動画は15秒＝75字が限界だった）

組み立て:
  音声(wav) → 24fpsごとの音量 → 口の開き量 → 口パク画像を選ぶ
  ＋ 字幕（無音の切れ目で行を切り替え）＋ ゆっくり上下に揺らす
  → ffmpeg に生フレームを流し込んで mp4

使い方:
  python tools/odoku_movie.py --wav tmp/voice/0805_final.wav \
      --lines-file tmp/voice/0805_final.txt --out tmp/video/0805_odoku.mp4
"""
import argparse
import math
import os
import subprocess
import wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import imageio_ffmpeg

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, os.path.join(REPO, "tools"))

FPS = 24
MAX_OPEN = 22          # 口の最大開き量(px)
OPEN_STEPS = [0, 6, 12, 18, 22]   # 事前に作る口の段階（毎フレーム作ると遅い）
SWAY_PX = 4            # 上下の揺れ幅
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("日本語フォントが見つからないわ")


def read_wav(path):
    with wave.open(path, "rb") as w:
        n, sr, ch, sw = w.getnframes(), w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(n)
    if sw != 2:
        raise SystemExit("16bitのwavしか扱えないわ（今: %dbit）" % (sw * 8))
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
    if ch == 2:
        a = a.reshape(-1, 2).mean(axis=1)
    return a, sr


def frame_levels(samples, sr, nframes):
    """フレームごとの音量(0〜1)。口の開き量のもと。"""
    step = sr / FPS
    out = []
    for i in range(nframes):
        s = int(i * step)
        e = int((i + 1) * step)
        seg = samples[s:e]
        rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
        out.append(rms)
    out = np.array(out)
    peak = out.max() if out.max() > 0 else 1.0
    return np.clip(out / (peak * 0.65), 0, 1)   # 0.65で割って口が開ききるように


def split_points(levels, lines):
    """無音の切れ目で字幕を切り替える時刻(フレーム番号)を決める。

    行数-1個の「いちばん長い無音」を探す。台詞と音がずれないようにするため、
    決め打ちの等分割はしない。
    """
    if len(lines) <= 1:
        return []
    quiet = levels < 0.08
    runs = []          # (開始, 長さ)
    i = 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            runs.append((i, j - i))
            i = j
        else:
            i += 1
    # 端の無音は無視（頭と尻）
    runs = [r for r in runs if r[0] > FPS // 2 and r[0] + r[1] < len(quiet) - FPS // 4]
    runs.sort(key=lambda r: -r[1])
    picks = sorted(r[0] + r[1] // 2 for r in runs[: len(lines) - 1])
    return picks


def draw_caption(img_bgr, text, font):
    """下部に字幕を焼く。読めることが最優先＝黒帯＋白文字＋縁取り。"""
    pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil, "RGBA")
    W, H = pil.size

    # 画面幅に収まるように折り返す
    max_w = int(W * 0.88)
    lines, cur = [], ""
    for ch in text:
        t = cur + ch
        if d.textlength(t, font=font) > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur = t
    if cur:
        lines.append(cur)

    lh = int(font.size * 1.35)
    box_h = lh * len(lines) + 40
    top = H - box_h - 90
    d.rectangle([0, top, W, top + box_h], fill=(0, 0, 0, 165))
    y = top + 20
    for ln in lines:
        x = (W - d.textlength(ln, font=font)) // 2
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=4, stroke_fill=(0, 0, 0, 255))
        y += lh
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def main():  # noqa: C901
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--lines-file", default="")
    ap.add_argument("--out", default=os.path.join(REPO, "tmp", "video", "odoku.mp4"))
    ap.add_argument("--no-caption", action="store_true")
    args = ap.parse_args()

    from odoku_mouth import open_mouth, SRC

    base = cv2.imread(SRC, cv2.IMREAD_UNCHANGED)
    if base.shape[2] == 4:
        base = cv2.cvtColor(base, cv2.COLOR_BGRA2BGR)
    H, W = base.shape[:2]

    samples, sr = read_wav(args.wav)
    dur = len(samples) / sr
    nframes = int(math.ceil(dur * FPS))
    levels = frame_levels(samples, sr, nframes)

    lines = []
    if args.lines_file and not args.no_caption:
        # VOICEVOXの書き出しtxtはBOM付き＝utf-8だと先頭に□が出る
        with open(args.lines_file, encoding="utf-8-sig") as f:
            lines = [l.strip() for l in f if l.strip()]
    cuts = split_points(levels, lines) if lines else []

    font = load_font(58)
    # 口の段階×字幕行 の絵を先に作っておく（毎フレーム合成すると遅い）
    cache = {}
    for d in OPEN_STEPS:
        face = open_mouth(base, d)
        if lines:
            for li, ln in enumerate(lines):
                cache[(d, li)] = draw_caption(face, ln, font)
        else:
            cache[(d, 0)] = face

    ff = imageio_ffmpeg.get_ffmpeg_exe()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    cmd = [
        ff, "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (W, H), "-r", str(FPS),
        "-i", "pipe:0",
        "-i", args.wav,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k", "-shortest", args.out,
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    li = 0
    for i in range(nframes):
        while li < len(cuts) and i >= cuts[li]:
            li += 1
        lvl = levels[i]
        d = min(OPEN_STEPS, key=lambda s: abs(s - lvl * MAX_OPEN))
        frame = cache[(d, min(li, max(len(lines) - 1, 0)))]
        # ゆっくり上下に揺らす（静止画に見えないように）
        dy = int(round(math.sin(i / FPS * 1.1) * SWAY_PX))
        if dy:
            frame = np.roll(frame, dy, axis=0)
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    p.wait()

    size = os.path.getsize(args.out) if os.path.exists(args.out) else 0
    print("%s  %.2f秒  %dフレーム  %d bytes" % (args.out, dur, nframes, size))
    print("字幕の切替フレーム:", cuts, "／行数", len(lines))


# 他のツール(burn_captions.py 等)から関数だけ借りられるよう、直接実行の時だけ走らせる
if __name__ == "__main__":
    main()
