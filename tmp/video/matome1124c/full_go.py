# -*- coding: utf-8 -*-
# 11/10 お笑いまとめ：すちこの OK の後に回す → render.py（1本の流れ）→ out_x.mp4 → Downloads/oshinavi_1110_owarai_matome.mp4
import io, os, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
t0 = time.time()
r = subprocess.run([sys.executable, D + 'render.py'], capture_output=True, text=True, encoding='utf-8', errors='replace',
                   env=dict(os.environ, PYTHONIOENCODING='utf-8'))
log = ['render rc %d %.0f秒' % (r.returncode, time.time() - t0), r.stdout[-800:], r.stderr[-1500:]]
src = D + 'out_x.mp4'
if r.returncode == 0 and os.path.exists(src):
    dst = 'C:/Users/user/Downloads/oshinavi_1110_owarai_matome.mp4'
    shutil.copy2(src, dst)
    log.append('copied %s %.2fMB' % (dst, os.path.getsize(dst) / 1048576))
io.open(D + 'full_go.txt', 'w', encoding='utf-8').write('\n'.join(log))
