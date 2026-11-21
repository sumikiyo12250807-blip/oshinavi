# -*- coding: utf-8 -*-
# 11/21 記事の独立FCで発覚：一富士茄子牛焦げルギー ぴあ 53900・e+ 54098 に 11/22 10:00 一般発売の枠が無い（終わった2次受付だけ）
#  ＝ぴあは heal_stale_deadlines --ids で作り直す（足し算の安全弁つき）→ 鍵の中で --apply → reconcile_pia --ids
#  ＝e+ はそのあと reconcile_eplus --ids 54098 で実頁の窓を出す（ぴあと e+ を同時に叩かない＝順番に）
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1121/art21/'
log = io.open(D + 'fix_hitofuji.txt', 'w', encoding='utf-8')
def run(a):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    log.write('=== %s rc=%d\n%s\n%s\n' % (' '.join(a), r.returncode, r.stdout[-4000:], r.stderr[-800:])); log.flush()
    return r
run(['tools/reconcile_pia.py', '--ids', '53900'])
run(['tools/heal_stale_deadlines.py', '--ids', '53900', '--build'])
LK = 'tmp/x1112/index.lock'
while True:
    try:
        fd = os.open(LK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'fix_hitofuji'); os.close(fd); break
    except FileExistsError:
        time.sleep(15)
try:
    run(['tools/heal_stale_deadlines.py', '--ids', '53900', '--apply'])
finally:
    os.remove(LK)
run(['tools/reconcile_pia.py', '--ids', '53900'])
run(['tools/reconcile_eplus.py', '--ids', '54098'])
log.write('おわり\n')
