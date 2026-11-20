# -*- coding: utf-8 -*-
# 11/10 9:31 にすちこが Downloads に入れた2枚目のシート（ニューヨーク…ちびキャラ9人…）を sheet2.png に写す
import glob, os, shutil, io
from PIL import Image
fs = [f for f in glob.glob('C:/Users/user/Downloads/*.png') if 'ニューヨーク' in os.path.basename(f) and '9人' in os.path.basename(f) and 'シティガール' not in os.path.basename(f)]
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
out = [os.path.basename(f) for f in fs]
if len(fs) == 1:
    shutil.copyfile(fs[0], D + 'sheet2.png')
    im = Image.open(D + 'sheet2.png')
    out.append('%s %s' % (im.size, im.mode))
    im.convert('RGB').resize((im.width // 2, im.height // 2)).save(D + 'sheet2_small.png')
io.open(D + 'get_sheet2.txt', 'w', encoding='utf-8').write('\n'.join(out))
