# -*- coding: utf-8 -*-
# 夜に入れたTIGET 27158〜27267 を番人に通す → tmp/x1001/eve/tiget_gate.txt
import subprocess
root = 'C:/Users/user/oshinavi/'
ids = ','.join(str(i) for i in range(27158, 27268))
p = subprocess.run(['python', 'tools/gate_tiget_slots.py', '--ids', ids], cwd=root, capture_output=True)
open(root + 'tmp/x1001/eve/tiget_gate.txt', 'wb').write(p.stdout + p.stderr + ('\nexit %d\n' % p.returncode).encode())
