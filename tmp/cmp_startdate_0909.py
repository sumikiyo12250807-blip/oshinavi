# -*- coding: utf-8 -*-
"""3つの版で startDate を持つ枠の数を比べる。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

def load(p):
    h = io.open(p, encoding='utf-8', newline='').read()
    return {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}

for label, path in [('①適用前(prenoonheal)', 'index.html.bak_0909_prenoonheal'),
                    ('②1回目適用後(bak_heal_stale)', 'index.html.bak_0909_heal_stale'),
                    ('③いまの現物(2回目適用後)', 'index.html')]:
    d = load(path)
    n_sd = sum(1 for e in d.values() for t in e.get('tickets', []) if t.get('startDate'))
    n_tk = sum(len(e.get('tickets', [])) for e in d.values())
    print(f'{label:32} エントリ{len(d):5}  枠{n_tk:6}  startDate付き{n_sd:6}')
