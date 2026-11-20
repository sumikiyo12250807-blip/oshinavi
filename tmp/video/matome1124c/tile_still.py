from PIL import Image
import numpy as np
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/frames/'
rows = []
for p, box in (('still_', (250, 150, 830, 900)), ('stillt_', (250, 150, 830, 900))):
    ims = [Image.open(D + '%s%d.jpg' % (p, k)).crop(box) for k in range(6)]
    a = [np.asarray(i.convert('L'), dtype=np.float32) for i in ims]
    print(p, ['%.1f' % np.abs(a[k] - a[0]).mean() for k in range(6)])
    r = Image.new('RGB', (6 * 200, 260))
    for k, im in enumerate(ims):
        r.paste(im.resize((200, 260)), (k * 200, 0))
    rows.append(r)
o = Image.new('RGB', (1200, 520))
o.paste(rows[0], (0, 0)); o.paste(rows[1], (0, 260))
o.save(D + 'tile_still.png')
