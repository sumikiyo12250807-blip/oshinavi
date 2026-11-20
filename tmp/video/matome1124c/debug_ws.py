# -*- coding: utf-8 -*-
# cut_sheet5 の途中（前景・watershed の割り当て）を色で塗って見る＝p3 の頭の上が消えた理由を探す
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
src = io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/cut_sheet5.py', encoding='utf-8').read()
src = src[:src.index('res = {}')]
G = {}
exec(compile(src, 'cs5', 'exec'), G)
import numpy as np
from PIL import Image
lab, FG, ALPHA, mk = G['lab_ws'], G['FG'], G['ALPHA'], G['mk']
pal = np.array([[0, 0, 0], [255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0], [255, 0, 255], [0, 255, 255], [255, 128, 0], [128, 0, 255], [0, 128, 128], [80, 80, 80]], np.uint8)
v = pal[np.clip(lab, 0, 10)]
v[lab == -1] = 255
v = (v * 0.5 + np.asarray(G['big']) * 0.5).astype(np.uint8)
v[~FG] = (v[~FG] * 0.3).astype(np.uint8)
Image.fromarray(v).crop((1700, 0, 2508, 400)).save('C:/Users/user/oshinavi/tmp/video/matome1124c/poses/debug_p3.png')
a = Image.fromarray(ALPHA).crop((1700, 0, 2508, 400)).save('C:/Users/user/oshinavi/tmp/video/matome1124c/poses/debug_p3a.png')
