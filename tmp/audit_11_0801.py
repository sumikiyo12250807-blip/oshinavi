# -*- coding: utf-8 -*-
"""今夜のX投稿11組だけを対象に、ぴあのキーワード検索でツアー取りこぼしを監査する。

pia_missing_audit.audit() をそのまま使う（全2363件を回すと重いので、キーワードを11個に絞る）。
出力の state ファイルは grow_from_audit.py --state で育成にそのまま使える形。
🚨ぴあ429対策でキーワード間5秒待つ（reference_pia_rate_limit_429）。
"""
import importlib.util
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)


def load(name, fname):
    s = importlib.util.spec_from_file_location(name, os.path.join(TOOLS, fname))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


pma = load('pma', 'pia_missing_audit.py')

IDS = [1637, 2151, 2153, 2159, 2178, 2185, 2188, 2311, 2900, 3118, 3191]
STATE = os.path.join(HERE, 'audit_11_state.json')
OUT = os.path.join(HERE, 'audit_11_report.txt')

from check_expired import extract_events_array  # noqa: E402

evs = extract_events_array('index.html')
byid = {e['id']: e for e in evs}
kws = []
for i in IDS:
    a = (byid.get(i) or {}).get('artist')
    if a and a not in kws:
        kws.append(a)

reg = pma.registered_cds(evs)
excl = pma.load_excluded()

print('keywords=%d registered_codes=%d' % (len(kws), len(reg)))
prior = {}
if os.path.exists(STATE):
    prior = json.load(open(STATE, encoding='utf-8'))

pma.audit(kws, reg, excl, 5, STATE, OUT, prior=prior, rls_from=None, today=None)
print('done ->', OUT)
