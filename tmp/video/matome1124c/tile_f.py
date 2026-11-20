from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/frames/'
fs = ['h_002.0.png', 'h_118.0.png', 'h_138.5.png']
ims = [Image.open(D + f).resize((540, 960)) for f in fs]
o = Image.new('RGB', (540 * 3 + 20, 960), (30, 30, 30))
for i, im in enumerate(ims):
    o.paste(im, (i * 550, 0))
o.save(D + 'tile_f.png')
