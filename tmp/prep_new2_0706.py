# -*- coding: utf-8 -*-
"""7/6 新着候補 batch2 選定。batch1(2036-2086)投入後の現index.htmlからhave/maxidを再取得し、
音楽(01)/演劇(02)/クラシック(07)の発売前候補から rlsdate昇順で次の50件を採る。
eventCd重複除外・新id採番。出力 tmp/cand_new2_0706.json。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def eventcd(url):
    m = re.search(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', url or '')
    return m.group(1) if m else None

h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
have, maxid = set(), 0
for e in EVENTS:
    maxid = max(maxid, e.get('id', 0))
    for k, v in (e.get('links') or {}).items():
        c = eventcd(v)
        if c: have.add(c)
    for t in e.get('tickets', []):
        c = eventcd(t.get('url'))
        if c: have.add(c)

cands = []
for lg in ('01', '02', '07'):
    d = json.load(open(f'tmp/presale_{lg}_0706.json', encoding='utf-8'))
    for c in d['new']:
        if c.get('in_db'):
            continue
        cd = eventcd(c['url'])
        if cd and cd in have:
            continue
        cands.append(c)

def rlskey(c):
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', c.get('rlsdate', '') or '9999/12/31')
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else (9999, 12, 31)

cands.sort(key=rlskey)

seen, picked = set(), []
for c in cands:
    cd = eventcd(c['url'])
    if cd in seen:
        continue
    seen.add(cd)
    picked.append(c)
    if len(picked) >= 50:
        break

out, nid = [], maxid
for c in picked:
    nid += 1
    out.append({'newid': nid, 'artist': c['artist'], 'urls': [c['url']]})

json.dump(out, open('tmp/cand_new2_0706.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f"既存eventCd {len(have)} / 未投入プール {len(cands)} / 選定 {len(out)}件")
print(f"新id範囲: {maxid+1} 〜 {nid}")
if picked:
    print(f"発売日レンジ: {picked[0].get('rlsdate')} 〜 {picked[-1].get('rlsdate')}")
