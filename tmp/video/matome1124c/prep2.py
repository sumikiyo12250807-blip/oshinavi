# -*- coding: utf-8 -*-
# 切り抜きの道具を新しいシート用に直して回す・USLT を読みやすく書き出す・背景のコマ・テンポの当たり
import io, os, re, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
t = open(D + 'lyrics_tag.txt', 'rb').read()
for enc in ('utf-16', 'utf-8'):
    try:
        s = t.decode(enc); break
    except Exception:
        pass
io.open(D + 'uslt.txt', 'w', encoding='utf-8').write(s.replace('\x00', ''))
c = io.open(D + 'cut_sheet5.py', encoding='utf-8').read()
c = re.sub(r"BOX = \{.*?\}\n", """BOX = {1: (95, 0, 350, 452), 2: (510, 0, 810, 452), 3: (955, 15, 1265, 448),
       4: (85, 450, 370, 820), 5: (460, 462, 975, 805), 6: (1035, 438, 1250, 820),
       7: (50, 808, 395, 1195), 8: (455, 812, 945, 1195), 9: (970, 808, 1285, 1199)}
""", c, count=1, flags=re.S)
a = c.index('HEAD = {4:')
b = c.index('_hsv = cv2')
c = c[:a] + """HEAD = {6: [(1060, 445, 1200, 560)], 4: [(120, 458, 290, 580)], 7: [(150, 815, 310, 930)], 8: [(480, 818, 660, 960)], 9: [(1040, 815, 1195, 960)], 5: [(480, 470, 680, 620)]}
FOOT = {1: [(125, 405, 335, 440)], 2: [(530, 390, 770, 440)], 3: [(985, 400, 1255, 440)], 4: [(130, 770, 345, 812)], 5: [(815, 530, 965, 640)], 6: [(1045, 785, 1215, 815)]}
TOPCLIP = {}
""" + c[b:]
a = c.index('DROP = {4:')
b = c.index('_NEU2 = cv2')
c = c[:a] + 'DROP = {}\n' + c[b:]
c = c.replace('if k != 7:', 'if k not in (3, 8):')
io.open(D + 'cut_sheet6.py', 'w', encoding='utf-8').write(c)
out = io.open(D + 'prep2.txt', 'w', encoding='utf-8')
for f in ('cut_sheet6.py', 'bg_prep.py', 'tempo_check.py'):
    r = subprocess.run([sys.executable, D + f], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s rc %s\n%s\n%s\n' % (f, r.returncode, r.stdout[-1500:], r.stderr[-1200:]))
out.close()
