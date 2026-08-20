# -*- coding: utf-8 -*-
"""7/6 変換36件の二段構え再照合ラッパー。"""
import subprocess, sys
idstr = open('tmp/conv_ids_0706.txt', encoding='utf-8').read().strip()
subprocess.run([sys.executable, 'tools/reconcile_pia.py', '--ids', idstr])
