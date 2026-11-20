# -*- coding: utf-8 -*-
# 11/20 締め：まん中（白い王冠 t8）と同じ子が下の段にもいた → 下の段の t8 を赤い王冠 t2 に替えて、締めのコマと試し動画 clip_b だけ作り直す → ページ
import io, os, shutil, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
r = io.open(D + 'render.py', encoding='utf-8').read()
x = "PARADE = [('s5', _R[0]), ('s4', _R[1]), ('t8', _R[2]), ('t1', _R[3])]   # 11/20 左2人は右向き（マイク・うさぎ）・右2人は左向き（白い王冠・黒白）"
assert x in r
r = r.replace(x, "PARADE = [('s5', _R[0]), ('s4', _R[1]), ('t2', _R[2]), ('t1', _R[3])]   # 11/20 左2人は右向き（マイク・うさぎ）・右2人は左向き（赤い王冠・黒白）＝まん中の白い王冠 t8 と重ねない")
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)
log = io.open(D + 'redo_parade.txt', 'w', encoding='utf-8')
for a in (['--frames', '92.5,104.0'], ['--clip', '76.0,108.02']):
    p = subprocess.run([sys.executable, D + 'render.py'] + a, capture_output=True, text=True, encoding='utf-8', errors='replace')
    log.write('%s rc=%d %s\n' % (a, p.returncode, (p.stdout + p.stderr)[-400:])); log.flush()
shutil.copyfile(D + 'clip.mp4', D + 'clip_b.mp4')
p = subprocess.run([sys.executable, D + 'mk_page_1120.py'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log.write('page rc=%d %s\n' % (p.returncode, (p.stdout + p.stderr)[-400:]))
