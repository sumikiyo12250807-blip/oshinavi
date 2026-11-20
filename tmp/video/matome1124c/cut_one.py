# -*- coding: utf-8 -*-
# 11/4：冬のシート1枚（1254×1254・3×3）を cut_two.py の切り方で 9 着に切る → poses/a1〜a9.png・compare_a.png・cut_two.txt
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
A = np.asarray(Image.open(D + 'sheet_a.png').convert('RGBA'))[:, :, 3]
print('alpha 0 の割合 %.2f / 255 の割合 %.2f' % ((A == 0).mean(), (A == 255).mean()))
pr = (A >= 128).sum(axis=1)
print('行の投影の谷（380〜460・800〜880）:', 380 + int(pr[380:460].argmin()), 800 + int(pr[800:880].argmin()))
s = io.open(D + 'cut_two.py', encoding='utf-8').read()
s = s.replace("ROWB = {'a': [425, 840], 'b': [426, 850]}", "ROWB = {'a': [%d, %d]}" % (380 + int(pr[380:460].argmin()), 800 + int(pr[800:880].argmin())))
s = s.replace('h / 425.0', 'h / 418.0')
s = s.replace("cut('a')\ncut('b')", "cut('a')")
exec(compile(s, 'cut_two', 'exec'))
