# -*- coding: utf-8 -*-
"""動画から等間隔でコマを抜いて1枚に並べる。
   「キャラの大きさが最後まで変わっていないか」は、並べて見るのがいちばん早い。"""
import io, os, subprocess, sys
import imageio_ffmpeg
from PIL import Image, ImageDraw

sys.stdout.reconfigure(encoding="utf-8")
SRC = "tmp/video/odoku_0908_dance.mp4"
OUT = "tmp/video/odoku_0908_frames.png"
TIMES = [0.2, 3, 6, 9, 12, 14.8]

ff = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs("tmp/video/frames", exist_ok=True)
paths = []
for i, t in enumerate(TIMES):
    p = "tmp/video/frames/f%d.png" % i
    r = subprocess.run([ff, "-y", "-ss", str(t), "-i", SRC, "-frames:v", "1", "-vf", "scale=360:-1", p],
                       capture_output=True)
    if r.returncode == 0 and os.path.exists(p):
        paths.append((t, p))

ims = [(t, Image.open(p).convert("RGB")) for t, p in paths]
w, h = ims[0][1].size
cols, rows = 3, 2
sheet = Image.new("RGB", (w * cols, h * rows), (16, 18, 28))
d = ImageDraw.Draw(sheet)
for i, (t, im) in enumerate(ims[:cols * rows]):
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(im, (x, y))
    d.rectangle([x + 4, y + 4, x + 74, y + 26], fill=(0, 0, 0))
    d.text((x + 10, y + 10), "%.1fs" % t, fill=(255, 255, 255))
sheet.save(OUT)
print("wrote %s (%dx%d) frames=%d" % (OUT, sheet.size[0], sheet.size[1], len(ims)))
