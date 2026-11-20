# -*- coding: utf-8 -*-
# すちこ「野球の時は同じ子出しても良いよ　前に使った子たちはどこにいるの？」＝にしかわはるきと まつもとごうの とーくしょー の行は
#   前のスポーツの姐さん（shuyaku1113/sheetB.png）の「R」の帽子の野球の子 a2 にする（ペンライトのファンはやめる）
#   ペンライトのファン w9 は締めの下の段へ（左＝右向き）。下の段＝ファン・サッカー（左・右向き）／ラグビー・相撲（右・左向き）
#   a2 にも、ほかの子と同じうすい紫のふちを付ける（halo.py の形・a2 だけ）
import io
from PIL import Image, ImageFilter
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
P = D + 'poses/'
im = Image.open(P + 'a2.png').convert('RGBA')
pad = 16
big = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
big.paste(im, (pad, pad), im)
ring = big.getchannel('A').point(lambda v: 255 if v > 60 else 0).filter(ImageFilter.MaxFilter(13))
edge = Image.new('RGBA', big.size, (110, 40, 130, 0)); edge.putalpha(ring.filter(ImageFilter.GaussianBlur(2.5)).point(lambda v: int(v * 0.75)))
sh = Image.new('RGBA', big.size, (60, 20, 80, 0)); sh.putalpha(ring.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.45)))
out = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(Image.new('RGBA', big.size, (0, 0, 0, 0)), sh), edge), big)
out.save(P + 'a2.png')
r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + "ORDER = ['w7', 'w1', 'w4', 'm4', 'w2', 'w5', 'm3', 'a2', 'w8', 'w6']   # 11/16 歌う行と衣装を合わせる・トークショーの行は前の絵の「R」の帽子の野球の子 a2・締めはチア w6" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('w9', _R[0]), ('w2', _R[1]), ('m3', _R[2]), ('m1', _R[3])]   # 11/16 左2人は右向き（ペンライトのファン・サッカー）・右2人は左向き（ラグビー・相撲）＝真ん中を向く" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)
print('ok')
