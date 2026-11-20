# -*- coding: utf-8 -*-
# 11/10：背景 104570 の3コマ・シートの縮小・タップ候補（M-1 50254 ほか）の券の文字を見る → peek1110.txt
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
subprocess.run([sys.executable, D + 'bg_peek9.py'])
from PIL import Image
im = Image.open(D + 'sheet.png')
im.resize((768, 512)).save(D + 'sheet_small.png')
s = io.open('index.html', encoding='utf-8').read()
i = s.index('const EVENTS = [') + len('const EVENTS = ')
E, _ = json.JSONDecoder().raw_decode(s[i:])
by = {e['id']: e for e in E}
out = [io.open(D + 'bg_peek9.txt', encoding='utf-8').read()]
for x in (50254, 50255, 50256, 50289, 50292, 19986, 46884):
    e = by[x]
    out.append('id%d %s｜%s｜%s' % (x, e.get('name'), e.get('artist'), e.get('prefecture')))
    for t in e['tickets']:
        out.append('   %s %s %s %s' % (t.get('startDate'), t.get('date'), t.get('type'), t.get('soldout')))
io.open(D + 'peek1110.txt', 'w', encoding='utf-8').write('\n'.join(out))
