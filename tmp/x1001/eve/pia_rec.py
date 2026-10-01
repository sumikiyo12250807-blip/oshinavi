# -*- coding: utf-8 -*-
# 夜のぴあ新規61件（27268〜27328）＋足し込み13件を reconcile_pia で照合 → tmp/x1001/eve/pia_rec.txt
import subprocess
root = 'C:/Users/user/oshinavi/'
ids = [str(i) for i in range(27268, 27329)] + open(root + 'tmp/x1001/eve/merge_ids.txt').read().strip().split(',')
p = subprocess.run(['python', 'tools/reconcile_pia.py', '--ids', ','.join(ids)], cwd=root, capture_output=True)
open(root + 'tmp/x1001/eve/pia_rec.txt', 'wb').write(p.stdout + p.stderr + ('\nexit %d\n' % p.returncode).encode())
