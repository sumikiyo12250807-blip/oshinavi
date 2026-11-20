# -*- coding: utf-8 -*-
# 動きを入れた版の試し（26〜42 秒＝Furui Riho・め組・猪狩翔一・NETH PRIERE CAIN）→ clip_move.mp4 → 確認ページに足す
import os, shutil, subprocess, sys
import imageio_ffmpeg
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
r = subprocess.run([sys.executable, D + 'render.py', '--clip', '26.0,42.0'], capture_output=True, text=True, encoding='utf-8', errors='replace')
shutil.copyfile(D + 'clip.mp4', D + 'clip_move.mp4')
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'clip_move.mp4', '-vf', 'scale=432:768', '-c:v', 'libx264', '-crf', '30', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', D + 'clip_move_s.mp4'], check=True)
open(D + 'move_clip.done', 'w').write('rc %d' % r.returncode)
