# -*- coding: utf-8 -*-
"""id3483 の ❌（内訳なし）を切り分ける。reconcileが数えている「ぴあ買える枠」の券種名を全部出す。
reference_reconcile_pia_qc_gate の限界4番(同締切の別券種が本当に抜けている)と
6番(bundle行と会場別行の二重計上＝偽陽性)を券種名で見分けるため。"""
import os, sys, re, json, io, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, 'tools')
sys.path.insert(0, TOOLS)
_OUT = sys.__stdout__

s = importlib.util.spec_from_file_location('rp', os.path.join(TOOLS, 'reconcile_pia.py'))
rp = importlib.util.module_from_spec(s); s.loader.exec_module(rp)

h = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
ev = next(e for e in json.loads(m.group(2)) if e['id'] == 3483)

urls = rp.pia_urls(ev)
buy, drops, errs, tries = rp.fetch_buyable(urls, expect=len(ev.get('tickets') or []))

o = io.open('tmp/peek_3483.txt', 'w', encoding='utf-8')
o.write('URL %d本\n' % len(urls))
for u in urls:
    o.write('  %s\n' % u)
o.write('\n--- ぴあ買える枠 %d ---\n' % len(buy))
for b in buy:
    o.write('  %s\n' % json.dumps(b, ensure_ascii=False))
o.write('\n--- DROP %d ---\n' % len(drops))
for d in drops:
    o.write('  %s\n' % json.dumps(d, ensure_ascii=False))
o.write('\n--- ERR %d ---\n' % len(errs))
for e in errs:
    o.write('  %s\n' % json.dumps(e, ensure_ascii=False))
o.write('\n--- 登録 %d ---\n' % len(ev.get('tickets') or []))
for t in ev.get('tickets') or []:
    o.write('  %s | date=%s start=%s\n' % (t.get('type'), t.get('date'), t.get('startDate')))
o.close()
_OUT.write('wrote tmp/peek_3483.txt  buyable=%d reg=%d\n' % (len(buy), len(ev.get('tickets') or [])))
