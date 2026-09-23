# -*- coding: utf-8 -*-
"""動画から等間隔にコマを抜いて1枚に並べる（大きさ・椅子・水・人数の確認用）。
  python tools/video_contact.py <mp4> <out.png> [--n 8]"""
import argparse
import os
import subprocess
import tempfile

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mp4')
    ap.add_argument('out')
    ap.add_argument('--n', type=int, default=8)
    ap.add_argument('--dur', type=float, default=15.0)
    a = ap.parse_args()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    tmp = tempfile.mkdtemp()
    frames = []
    for i in range(a.n):
        t = a.dur * (i + 0.5) / a.n
        p = os.path.join(tmp, '%02d.png' % i)
        subprocess.run([ff, '-y', '-ss', '%.2f' % t, '-i', a.mp4, '-frames:v', '1', '-vf', 'scale=360:-1', p],
                       capture_output=True)
        frames.append((t, Image.open(p).convert('RGB')))
    w, h = frames[0][1].size
    cols = 4
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * w, rows * (h + 40)), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(r'C:\Windows\Fonts\meiryob.ttc', 26)
    for i, (t, im) in enumerate(frames):
        x, y = (i % cols) * w, (i // cols) * (h + 40)
        sheet.paste(im, (x, y + 40))
        d.text((x + 8, y + 4), '%.1f秒' % t, font=f, fill=(255, 210, 90))
    sheet.save(a.out)
    print(a.out, sheet.size)


if __name__ == '__main__':
    main()
