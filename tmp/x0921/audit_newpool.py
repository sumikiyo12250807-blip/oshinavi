# -*- coding: utf-8 -*-
"""9/21夜のX投稿に足した新着（FANY/ZAIKO）の名前でぴあを総ざらい（読むだけ）。audit_posts2.py の写し。
使い方: python tmp/x0921/audit_newpool.py
出力: tmp/x0921/audit_newpool.txt
"""
import datetime
import importlib.util
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.getcwd()
spec = importlib.util.spec_from_file_location('pma', os.path.join(ROOT, 'tools', 'pia_missing_audit.py'))
pma = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(pma)

KWS = ["OWV", "青木マッチョ", "空前メテオ", "ジョックロック", "例えば炎", "NMB48"]
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
print('引く名前 %d' % len(KWS))
pma.audit(KWS, reg, excl, 5, 'tmp/x0921/audit_state_newpool.json', 'tmp/x0921/audit_newpool.txt', prior=None, rls_from=None, today=TODAY)
print('→ tmp/x0921/audit_newpool.txt')
