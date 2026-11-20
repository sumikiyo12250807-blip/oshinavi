# -*- coding: utf-8 -*-
# 11/7 すちこ「尺八吹いてるのと狐のお面がはじかれてたから使ってほしい」＝2枚を切り抜いて poses に足す
#   fx＝狐のお面（元の向き）／gx＝狐の反転／fl＝笛（尺八）／gl＝笛の反転。高さは九面の子（k*）のいちばん高い子にそろえる
import glob, io
import numpy as np
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
SRC = {'fx': 'C:/Users/user/Downloads/キツネ面で舞う祭りの踊り子.png',
       'fl': 'C:/Users/user/Downloads/祭り衣装の紫髪笛吹き少女.png'}
kh = [Image.open(f).height for f in glob.glob(D + 'poses/k[1-9].png')]
log = ['k heights %s' % kh]
H = max(kh)
for k, p in SRC.items():
    im = Image.open(p).convert('RGBA')
    a = np.asarray(im)[:, :, 3]
    log.append('%s mode alpha min=%d max=%d transparent=%.2f' % (k, a.min(), a.max(), (a < 20).mean()))
    if (a < 20).mean() < 0.05:   # 透明でない＝黒い地を抜く
        rgb = np.asarray(im)[:, :, :3].astype(int)
        dark = rgb.max(axis=2) < 18
        arr = np.asarray(im).copy()
        arr[dark, 3] = 0
        im = Image.fromarray(arr)
        log.append('%s black keyed' % k)
    im = im.crop(im.getbbox())
    im = im.resize((int(im.width * H / im.height), H), Image.LANCZOS)
    im.save(D + 'poses/%s.png' % k)
    im.transpose(Image.FLIP_LEFT_RIGHT).save(D + 'poses/%s.png' % ('g' + k[1]))
    log.append('%s -> %dx%d' % (k, im.width, im.height))
io.open(D + 'prep_fox.txt', 'w', encoding='utf-8').write('\n'.join(log))
