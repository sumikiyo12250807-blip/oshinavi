# -*- coding: utf-8 -*-
import re, json
def stats(path):
    try:
        h = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        return f"{path}: (無し)"
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
    E = json.loads(m.group(2)) if m else []
    mo = re.search(r'(  const NEW_ORDER = )(\[.*?\])(;)', h, re.S)
    N = json.loads(mo.group(2)) if mo else None
    haji = [e for e in E if e.get('artist') == '一凛']
    hid = sorted(e['id'] for e in haji)
    return (f"{path}:\n  EVENTS={len(E)} maxid={max((e['id'] for e in E), default=0)} "
            f"一凛={len(haji)}{hid}\n  NEW_ORDER={len(N) if N is not None else 'なし'} "
            f"末尾={N[-6:] if N else N}")

out = []
for p in ['index.html', 'index.html.bak_0716_rescue', 'index.html.bak_0716_heal_stale']:
    out.append(stats(p))
res = "\n".join(out)
open('tmp/compare_result.txt', 'w', encoding='utf-8').write(res)
print("done")
