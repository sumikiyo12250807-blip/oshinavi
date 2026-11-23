# -*- coding: utf-8 -*-
# 宿のボタンの絵を軽くする（256色にして透明は残す）・index.html の大きさを前の commit とくらべる
import io, os, subprocess
from PIL import Image
R = 'C:/Users/user/oshinavi/'
p = R + 'img/btn_hotel_wide.png'
before = os.path.getsize(p)
im = Image.open(p).convert('RGBA')
q = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
q.save(p, optimize=True)
after = os.path.getsize(p)
head = subprocess.run(['git', '-C', R, 'show', 'HEAD~12:index.html'], capture_output=True).stdout
idx = os.path.getsize(R + 'index.html')
others = [os.path.getsize(R + 'img/' + f) for f in os.listdir(R + 'img') if f.startswith('btn2_')]
io.open(R + 'tmp/x1123/btn_size.txt', 'w', encoding='utf-8').write(
    'ボタンの絵 %dKB → %dKB\nindex.html いま %.2fMB（12 commit 前 %.2fMB）\nほかのボタンの絵 %d枚 平均 %dKB\n' % (
        before // 1024, after // 1024, idx / 1e6, len(head) / 1e6, len(others), (sum(others) // max(len(others), 1)) // 1024))
