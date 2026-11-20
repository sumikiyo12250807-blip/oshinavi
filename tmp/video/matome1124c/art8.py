# -*- coding: utf-8 -*-
# 後奏の直しを確かめる（62.3 秒のコマ）→ 見せるページの材料（絵コンテ・試し動画）を art/ に
import os, shutil, subprocess, sys
from PIL import Image
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
r = subprocess.run([sys.executable, D + 'render.py', '--frames', '62.3'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print('frames rc', r.returncode, r.stderr[-500:])
r = subprocess.run([sys.executable, D + 'board.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print('board rc', r.returncode, r.stderr[-500:])
os.makedirs(D + 'art', exist_ok=True)
for f in os.listdir(D + 'art'):
    os.remove(D + 'art/' + f)
Image.open(D + 'board.png').convert('RGB').save(D + 'art/board.jpg', quality=82)
shutil.copyfile(D + 'clip.mp4', D + 'art/clip.mp4')
print(os.path.getsize(D + 'art/board.jpg') // 1024, os.path.getsize(D + 'art/clip.mp4') // 1024, os.path.getmtime(D + 'clip.mp4'))
