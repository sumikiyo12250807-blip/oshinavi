import os
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/frames/'
fs = sorted(f for f in os.listdir(D) if f.startswith('h_'))
ims = [Image.open(D + f).resize((360, 640)) for f in fs]
out = Image.new('RGB', (360 * len(ims) + 10 * (len(ims) - 1), 640), (40, 40, 40))
for i, im in enumerate(ims):
    out.paste(im, (i * 370, 0))
out.save(D + '../contact.png')
print(fs)
