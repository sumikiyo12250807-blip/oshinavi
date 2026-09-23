# -*- coding: utf-8 -*-
"""9/20号の主役5組＋深掘りの名前でぴあを総ざらいして、登録に無い eventCd を出す（取りこぼしチェック①）。
tools/pia_missing_audit の関数を借りる（tmp/x0914/audit_posts.py と同じ形）。"""
import datetime
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
spec = importlib.util.spec_from_file_location('pma', os.path.join(ROOT, 'tools', 'pia_missing_audit.py'))
pma = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(pma)

TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
kws = ['アイカツスターズ', '角野隼斗', '矢野顕子', '反田恭平', '斉藤和義', 'ドラゴンクエスト']
pma.audit(kws, reg, excl, 5, 'tmp/pickup0920/audit_state.json', 'tmp/pickup0920/audit_main.txt',
          prior=None, rls_from=None, today=TODAY)
print('-> tmp/pickup0920/audit_main.txt')
