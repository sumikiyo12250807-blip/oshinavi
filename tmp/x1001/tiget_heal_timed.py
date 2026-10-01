# -*- coding: utf-8 -*-
# 開場→開演の直し：対象391件を heal_tiget で作り直す（引数 --apply で書く）→ 標準出力は tmp/x1001/tiget_heal_timed.txt
import io, json, subprocess, sys
root = 'C:/Users/user/oshinavi/'
ids = ','.join(str(i) for i in json.load(io.open(root + 'tmp/x1001/tiget_timed_ids.json')))
cmd = ['python', 'tools/heal_tiget.py', '--ids', ids] + (['--apply'] if '--apply' in sys.argv else [])
p = subprocess.run(cmd, cwd=root, capture_output=True)
io.open(root + 'tmp/x1001/tiget_heal_timed.txt', 'wb').write(p.stdout + p.stderr)
