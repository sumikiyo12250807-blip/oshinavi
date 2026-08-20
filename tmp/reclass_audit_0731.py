# -*- coding: utf-8 -*-
"""保存済みの監査stateを、直した same_name() で分類し直してレポートを作り直す（通信なし）。
全角判定バグで「別名義/フェス」に紛れていた本人名義を拾い直せているか確認するため。"""
import os, sys, json, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)
_OUT = sys.__stdout__

s = importlib.util.spec_from_file_location('pma', os.path.join(TOOLS, 'pia_missing_audit.py'))
pma = importlib.util.module_from_spec(s); s.loader.exec_module(pma)

state_path = 'tmp/audit_new_0731_state.json'
st = json.load(open(state_path, encoding='utf-8'))
res = st['results']

before = after = 0
for kw, v in res.items():
    for mm in v['missing']:
        before += 1 if mm.get('own_name') else 0
        mm['own_name'] = pma.same_name(kw, mm['title'])
        after += 1 if mm['own_name'] else 0

json.dump(st, open(state_path, 'w', encoding='utf-8'), ensure_ascii=False)
pma.write_report(res, 'tmp/audit_new_0731_fixed.txt', len(res),
                 st.get('rls_from'), st.get('today'))
_OUT.write('本人名義 判定: %d件 → %d件 / report: tmp/audit_new_0731_fixed.txt\n' % (before, after))
