# -*- coding: utf-8 -*-
# 11/7：①背景 127888 は緑の合成用の地（和傘）＝緑を抜いて濃い紫紺の地に重ねる ②k2 の足元の細い線（k5 の髪）は体とつながっていた＝細い所を削って大きい塊だけ残す → n2 も作り直す
#   → 絵コンテ → 試し動画（24〜38 秒＝10時 ミキ → ジョイマン・令和ロマン、着替え 1 回）
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
import numpy as np, cv2
from PIL import Image, ImageOps
import imageio_ffmpeg
out = io.open(D + 'prep1107e.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-1500:], r.stderr[-1500:]))
    out.flush()


# ② k2
im = Image.open(D + 'poses/k2.png').convert('RGBA')
a = np.asarray(im).copy()
m = (a[:, :, 3] > 20).astype(np.uint8)
op = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
n, lab, st, _ = cv2.connectedComponentsWithStats(op, 8)
big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
keep = cv2.dilate((lab == big).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))) > 0
a[:, :, 3] = np.where(keep, a[:, :, 3], 0)
ys, xs = np.where(a[:, :, 3] > 20)
k2 = Image.fromarray(a).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
k2.save(D + 'poses/k2.png')
ImageOps.mirror(k2).save(D + 'poses/n2.png')
g = Image.new('RGB', (k2.width + 40, k2.height + 40), (120, 120, 120)); g.paste(k2, (20, 20), k2); g.save(D + 'poses/look_k2_clean.png')
out.write('k2 → %s\n' % (k2.size,))
# ① 背景
B = D + 'bgf/'
for f in os.listdir(B):
    os.remove(B + f)
ff = imageio_ffmpeg.get_ffmpeg_exe()
fc = ('[0:v]fps=30,scale=-2:1920:flags=lanczos,crop=1080:1920,colorkey=0x00FF00:0.32:0.12,despill=type=green[fg];'
      'color=c=0x1c1030:s=1080x1920:r=30[bg];[bg][fg]overlay=shortest=1,gblur=sigma=2,eq=brightness=-0.08:saturation=0.9')
r = subprocess.run([ff, '-y', '-v', 'error', '-i', D + 'bg_src.mp4', '-filter_complex', fc, '-q:v', '3', B + '%04d.jpg'], capture_output=True, text=True, errors='replace')
out.write('bg rc %s %s frames %d\n' % (r.returncode, r.stderr[-400:], len(os.listdir(B))))
run('board.py')
run('render.py', '--clip', '24,38')
out.close()
open(D + 'prep1107e.done', 'w').close()
