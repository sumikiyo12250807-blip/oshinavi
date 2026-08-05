# -*- coding: utf-8 -*-
"""できあがった動画に、あとからローカルでテロップを焼く（2026-08-05 新設）。

なぜ要るか＝**H3(AI動画)には字幕を描かせない**（プロンプトで "No on-screen text" と指示している）。
AIに文字を描かせると崩れるからで、その代わり**焼くのはこちら**。ローカルのフォントで描くので
1文字も化けない。ユーザーは音声だけだと聞き取れなかった実績があり、**テロップは必須**
（memory: project_odoku_x_video）。

切り替えの時刻は `odoku_movie.py` と同じ流儀＝**音声の無音の切れ目**で決める。
音声は元動画のものをそのまま残す（映像だけ描き直して差し替える）。

使い方:
  python tools/burn_captions.py --mp4 tmp/video/h3_0805_straykids.mp4 \
      --wav tmp/voice/sk_int10.wav --lines-file tmp/voice/odoku_0805_sk_lines.txt \
      --out tmp/video/h3_0805_straykids_cap.mp4
"""
import argparse
import importlib.util
import os
import subprocess
import sys

import cv2
import numpy as np
import imageio_ffmpeg

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# odoku_movie の描画・区切り処理をそのまま借りる（二重実装しない）
_spec = importlib.util.spec_from_file_location(
    "odoku_movie", os.path.join(REPO, "tools", "odoku_movie.py"))
_om = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_om)     # odoku_movie は __main__ ガード済み＝読み込んでも走らない


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp4", required=True, help="テロップを焼く元の動画")
    ap.add_argument("--wav", required=True, help="切り替え位置を決めるための音声")
    ap.add_argument("--lines-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--font-size", type=int, default=0, help="0なら画面幅から自動")
    a = ap.parse_args()

    with open(a.lines_file, encoding="utf-8-sig") as f:
        lines = [l.strip() for l in f if l.strip()]
    if not lines:
        sys.exit("テロップが空")

    cap = cv2.VideoCapture(a.mp4)
    if not cap.isOpened():
        sys.exit("動画が開けない: %s" % a.mp4)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print("元動画 %dx%d / %.2ffps / %dフレーム (%.2f秒)" % (w, h, fps, n, n / fps))

    samples, sr = _om.read_wav(a.wav)
    levels = _om.frame_levels(samples, sr, n)
    picks = _om.split_points(levels, lines)
    print("字幕の切替フレーム: %s ／行数 %d" % (picks, len(lines)))

    size = a.font_size or max(34, int(w * 0.052))
    font = _om.load_font(size)

    exe = imageio_ffmpeg.get_ffmpeg_exe()
    tmp_v = a.out + ".video.mp4"
    p = subprocess.Popen(
        [exe, "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "%dx%d" % (w, h),
         "-r", "%.4f" % fps, "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "18", tmp_v],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        idx = 0
        for k, pt in enumerate(picks):
            if i >= pt:
                idx = k + 1
        # 🚨draw_caption は破壊的でなく【新しい配列を返す】＝戻り値を受けないと焼かれない
        frame = _om.draw_caption(frame, lines[min(idx, len(lines) - 1)], font)
        p.stdin.write(frame.tobytes())
        i += 1
    cap.release()
    p.stdin.close()
    p.wait()

    # 元動画の音声をそのまま載せ替える
    subprocess.run(
        [exe, "-y", "-i", tmp_v, "-i", a.mp4, "-map", "0:v:0", "-map", "1:a:0?",
         "-c:v", "copy", "-c:a", "aac", "-shortest", a.out],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    os.remove(tmp_v)
    print("%s  %d フレームに焼いた  %d bytes" % (a.out, i, os.path.getsize(a.out)))


main()
