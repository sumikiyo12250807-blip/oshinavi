import shutil, os
from PIL import Image
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
Image.open(D + 'board.png').convert('RGB').save(D + 'art/board.jpg', quality=82)
shutil.copyfile(D + 'clip.mp4', D + 'art/clip.mp4')
print(os.path.getsize(D + 'art/board.jpg') // 1024, os.path.getsize(D + 'art/clip.mp4') // 1024)
