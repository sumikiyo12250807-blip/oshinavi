from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = Image.open(D + 'sheet_k.png').convert('RGBA')
flat = Image.alpha_composite(Image.new('RGBA', s.size, (0, 160, 0, 255)), s).convert('RGB')
c = flat.crop((420, 360, 790, 480)).resize((370 * 3, 120 * 3), Image.NEAREST)
d = ImageDraw.Draw(c)
for y in range(360, 481, 10):
    d.line([(0, (y - 360) * 3), (8, (y - 360) * 3)], fill=(255, 255, 0))
    d.text((10, (y - 360) * 3 - 6), str(y), fill=(255, 255, 0))
for x in range(420, 791, 20):
    d.line([((x - 420) * 3, 0), ((x - 420) * 3, 8)], fill=(255, 255, 0))
    d.text(((x - 420) * 3 + 2, 10), str(x), fill=(255, 255, 0))
c.save(D + 'k5_peek.png')
