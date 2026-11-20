# -*- coding: utf-8 -*-
# par_full.py の写しで、後半（raw2）だけ書き出し直す＝タップの場面の歌詞とタップの文字の重なりを直した（前半 raw1 は 12:17 の書き出しのまま）
import io
s = io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/par_full.py', encoding='utf-8').read()
a = "for k in range(2):\n    if k:\n        time.sleep(30)\n"
assert a in s
s = s.replace(a, "for k in (1,):\n")
s = s.replace("for k, p in enumerate(ps):\n    o, e = p.communicate()\n    log.write('raw%d rc", "for k, p in zip((1,), ps):\n    o, e = p.communicate()\n    log.write('raw%d rc")
s = s.replace("log = open(D + 'par_full.txt'", "log = open(D + 'par_half2.txt'")
assert 'for k in (1,):' in s and "zip((1,), ps)" in s
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/par_half2.py', 'w', encoding='utf-8').write(s)
w = io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/wait_then_full.py', encoding='utf-8').read()
w = w.replace("D + 'run_full.py'", "D + 'run_half2.py'")
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/wait_then_half2.py', 'w', encoding='utf-8').write(w)
r = io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/run_full.py', encoding='utf-8').read()
r = r.replace("D + 'par_full.py'", "D + 'par_half2.py'").replace("全編の書き出し中", "後半の書き出し直し中")
io.open('C:/Users/user/oshinavi/tmp/video/matome1124c/run_half2.py', 'w', encoding='utf-8').write(r)
print('ok')
