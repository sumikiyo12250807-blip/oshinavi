# -*- coding: utf-8 -*-
# 作り直した391件を TIGET の番人に通す → tmp/x1001/tiget_gate_timed.txt
import io, json, subprocess
root = 'C:/Users/user/oshinavi/'
ids = ','.join(str(i) for i in json.load(io.open(root + 'tmp/x1001/tiget_timed_ids.json')))
p = subprocess.run(['python', 'tools/gate_tiget_slots.py', '--ids', ids], cwd=root, capture_output=True)
io.open(root + 'tmp/x1001/tiget_gate_timed.txt', 'wb').write(p.stdout + p.stderr + ('\nexit %d\n' % p.returncode).encode())
