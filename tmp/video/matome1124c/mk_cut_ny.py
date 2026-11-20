# -*- coding: utf-8 -*-
# shuyaku1110/cut_city.py を今日のシート（ニューヨーク・ちびガールズ・白と薄い市松の地）用に写す → cut_ny.py
import io, re
src = io.open('C:/Users/user/oshinavi/tmp/video/shuyaku1110/cut_city.py', encoding='utf-8').read()
s = src.replace("D = 'C:/Users/user/oshinavi/tmp/video/shuyaku1110/'", "D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'")
s = s.replace("K = sys.argv[1]", "K = 'n'")
s = s.replace("sheet = Image.open(D + 'sheet_%s.png' % K).convert('RGB')", "sheet = Image.open(D + 'sheet.png').convert('RGB')")
a = s.index('BOXES = {')
b = s.index('FULLS = ')
s = s[:a] + """BOXES = {   # 11/10 boxes.py で測った列（80-464／536-992／1000-1440）と段の切れ目（348・691）＋少し重ねる
    'n': {1: (80, 0, 464, 352), 2: (536, 0, 992, 352), 3: (1000, 0, 1440, 352),
          4: (80, 338, 464, 698), 5: (536, 340, 992, 702), 6: (1000, 338, 1440, 698),
          7: (80, 684, 464, 1024), 8: (536, 680, 992, 1024), 9: (1000, 680, 1440, 1024)},
}
""" + s[b:]
s = s.replace("FULLS = {'a': (4, 5, 6, 7, 9), 'b': (2, 3, 4, 5, 6, 7)}", "FULLS = {'n': (1, 2, 3, 4, 5, 6, 7, 8, 9)}")
s = s.replace("FILLALL = {'a': (), 'b': ()}", "FILLALL = {'n': ()}")
s = s.replace("log = open(D + 'cut_city_%s.txt' % K", "log = open(D + 'cut_ny.txt'")
assert "'n': {1:" in s and "FULLS = {'n'" in s and 'matome1124c' in s
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/cut_ny.py', 'w', encoding='utf-8').write(s)
print('ok')
