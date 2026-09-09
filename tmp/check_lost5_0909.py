# -*- coding: utf-8 -*-
"""「消えた」と出た5件が、本当に消えたのか（URLが変わっただけか）を骨格で確かめる。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [571, 950, 1772, 4103, 5573]
TODAY = '2026-09-09'


def load(p):
    h = io.open(p, encoding='utf-8', newline='').read()
    return {e['id']: e for e in json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))}


def head(ty):
    m = re.match(r'^(.*?（[^（）]*公演）)', ty or '')
    return m.group(1) if m else (ty or '')


A = load('index.html.bak_0909_prenoonheal')
B = load('index.html')
for i in IDS:
    ea, eb = A[i], B[i]
    ka = {head(t.get('type')) for t in ea.get('tickets', [])}
    kb = {head(t.get('type')) for t in eb.get('tickets', [])}
    gone = ka - kb
    print('id%-6d %s  骨格 %d → %d  / 骨格ごと消えた: %s'
          % (i, ea.get('name', '')[:24], len(ka), len(kb), sorted(gone) or 'なし'))
    for t in eb.get('tickets', []):
        if head(t.get('type')) in (ka - kb) or head(t.get('type')) in ka:
            pass
    # 該当の骨格が今どうなっているかを出す
    for t in eb.get('tickets', []):
        h2 = head(t.get('type'))
        if h2 in ka:
            continue
    print()
