# -*- coding: utf-8 -*-
"""7/6 ⚠️要再確認89件をreconcileで機械照合するラッパー。
tmp/warn_ids_0706.txt のidを読んで reconcile_pia.py --ids に渡す。"""
import subprocess, sys
ids = open('tmp/warn_ids_0706.txt', encoding='utf-8').read().split()
idstr = ','.join(ids)
sys.stderr.write(f"reconcile対象 {len(ids)}件\n")
subprocess.run([sys.executable, 'tools/reconcile_pia.py', '--ids', idstr])
