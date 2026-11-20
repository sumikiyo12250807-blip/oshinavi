# -*- coding: utf-8 -*-
# cut_ny.py（1枚目）を2枚目（歩く子・sheet2.png・上5人／下4人）用に写す → cut_ny2.py（poses/cw1〜cw9・cut_ny2.txt・compare_cw.png）
import io, re
s = io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/cut_ny.py', encoding='utf-8').read()
s = s.replace("K = 'n'", "K = 'w'")
s = s.replace("sheet = Image.open(D + 'sheet.png').convert('RGB')", "sheet = Image.open(D + 'sheet2.png').convert('RGB')")
a, b = s.index('BOXES = {'), s.index('FULLS = ')
s = s[:a] + """BOXES = {   # 11/10 boxes2.py：段の切れ目 481・上の列 302/618/922/1224・下の列 364/692/1102（となりと少し重ねる＝watershed で分ける）
    'w': {1: (0, 0, 318, 482), 2: (288, 0, 635, 482), 3: (600, 0, 940, 482), 4: (905, 0, 1245, 482), 5: (1208, 0, 1536, 482),
          6: (0, 482, 382, 1024), 7: (348, 482, 708, 1024), 8: (676, 482, 1120, 1024), 9: (1086, 482, 1536, 1024)},
}
""" + s[b:]
s = s.replace("FULLS = {'n': (1, 2, 3, 4, 5, 6, 7, 8, 9)}", "FULLS = {'w': (1, 2, 3, 4, 5, 6, 7, 8, 9)}")
s = s.replace("FILLALL = {'n': ()}", "FILLALL = {'w': ()}")
s = re.sub(r"NETBOX = \{.*?\}\n", "NETBOX = {}\n", s, count=1)
s = re.sub(r"FORCE = \{'n'.*?\n", "FORCE = {}\n", s, count=1)
s = re.sub(r"NOHOLE = \{.*?\}\n", "NOHOLE = {}\n", s, count=1)
s = re.sub(r"DROP = \{'n'.*?\n", "DROP = {}\n", s, count=1)
s = s.replace("log = open(D + 'cut_ny.txt'", "log = open(D + 'cut_ny2.txt'")
assert "'w': {1:" in s and "sheet2.png" in s and "cut_ny2.txt" in s and "NETBOX = {}" in s
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/cut_ny2.py', 'w', encoding='utf-8').write(s)
print('ok')
