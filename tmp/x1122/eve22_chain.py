# -*- coding: utf-8 -*-
# 11/22 夕方の鎖＝1本ずつ順に：morning_local22 → eve22 → assign22n
import io, os, subprocess, sys, time
os.chdir('C:/Users/user/oshinavi')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
D = 'tmp/x1122/'
log = io.open(D + 'eve22_chain.txt', 'a', encoding='utf-8')
for f in ('morning_local22.py', 'eve22.py', 'assign22n.py'):
    log.write(time.strftime('%H:%M:%S ') + f + ' 開始\n'); log.flush()
    r = subprocess.run([sys.executable, D + f], env=env)
    log.write(time.strftime('%H:%M:%S ') + f + ' rc=%d\n' % r.returncode); log.flush()
open(D + 'eve22_chain.done', 'w').write('done')
