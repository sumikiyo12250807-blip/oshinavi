# -*- coding: utf-8 -*-
"""動画から指定秒のフレームを静止画で抜き出す（出来ばえの目視確認用）。
  python tools/grab_frames.py --mp4 tmp/video/x.mp4 --at 1,3,6 --outdir tmp/video/frames
"""
import argparse
import os
import subprocess

import imageio_ffmpeg

ap = argparse.ArgumentParser()
ap.add_argument('--mp4', required=True)
ap.add_argument('--at', default='1,3,6', help='秒をカンマ区切りで')
ap.add_argument('--outdir', default='tmp/video/frames')
a = ap.parse_args()

os.makedirs(a.outdir, exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
for s in [x.strip() for x in a.at.split(',') if x.strip()]:
    out = os.path.join(a.outdir, 'f%s.png' % s.replace('.', '_'))
    subprocess.run([ff, '-y', '-ss', s, '-i', a.mp4, '-frames:v', '1', out],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    print(('OK  ' if os.path.exists(out) else 'NG  ') + out)
