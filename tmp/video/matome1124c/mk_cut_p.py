# -*- coding: utf-8 -*-
# cut_ny2.py → cut_p.py（パリコレの子・sheet.png・記号 p・箱は boxes_p.txt から上下 35 重ね）
import io, re
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'cut_ny2.py', encoding='utf-8').read()
a = s.index('BOXES = {')
b = s.index('BOX = BOXES[K]')
s = s[:a] + """BOXES = {   # 11/11 boxes_p.py：段の切れ目 365・666／列 上 454・940・中 470・938・下 461・954（上下は 35 重ねる＝髪と靴が重なる所は watershed で分ける）
    'p': {1: (0, 0, 470, 400), 2: (440, 0, 955, 400), 3: (925, 0, 1536, 400),
          4: (0, 330, 485, 701), 5: (455, 330, 953, 701), 6: (923, 330, 1536, 701),
          7: (0, 631, 476, 1024), 8: (446, 631, 969, 1024), 9: (939, 631, 1536, 1024)},
}
FULLS = {'p': (1, 2, 3, 4, 5, 6, 7, 8, 9)}
FILLALL = {'p': ()}
FORCE = {}
NETBOX = {}
NOHOLE = {}
DROP = {}
""" + s[b:]
s = s.replace("K = 'w'", "K = 'p'").replace("sheet2.png", "sheet.png").replace("cut_ny2.txt", "cut_p.txt")
s = s.replace("# 11/9 主役：冬の服のシート2枚", "# 11/11 パリコレの子（cut_ny2 の写し）／元：11/9 主役：冬の服のシート2枚")
assert "K = 'p'" in s and "'sheet.png'" in s
io.open(D + 'cut_p.py', 'w', encoding='utf-8').write(s)
print('ok')
