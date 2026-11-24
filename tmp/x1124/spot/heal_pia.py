# -*- coding: utf-8 -*-
# 抜き打ち 🟠 5158 GOODWARP・48625 吉田山田＝ぴあで受付中の 2次/3次プレリザーブがカードに無い
#  → ぴあの実ページで取り直し（--build）→ 足し算で当てる（元の枠は置き換えられた分だけ外す）→ 照合し直す
import io, os, shutil, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1124/spot/'
IDS = '5158,48625'
LK = 'tmp/x1112/index.lock'
HOLD = 'tmp/heal_blocked_hold_1805.txt'
out = io.open(D + 'heal_pia.txt', 'w', encoding='utf-8')
def run(a):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('=== %s rc=%d\n%s\n%s\n' % (' '.join(a), r.returncode, r.stdout[-5000:], r.stderr[-1500:])); out.flush()
    return r
run(['tools/heal_stale_deadlines.py', '--ids', IDS, '--build'])
shutil.copy(HOLD, D + 'hold_backup.txt')
io.open(HOLD, 'w', encoding='utf-8').write(IDS)
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'spot_heal24'); os.close(fd); break
    except FileExistsError:
        time.sleep(10)
try:
    run(['tools/heal_union_stale.py', '--ids-src'])
    run(['tools/heal_union_stale.py', '--apply', '--ids-src'])
finally:
    os.remove(LK)
    shutil.copy(D + 'hold_backup.txt', HOLD)
run(['tools/reconcile_pia.py', '--ids', IDS])
out.close()
print('ok')
