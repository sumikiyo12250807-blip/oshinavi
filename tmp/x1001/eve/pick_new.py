import os
os.chdir('C:/Users/user/oshinavi')
# -*- coding: utf-8 -*-
"""pia_built_new.json から既存へ足し込む分（merge_add.NAME_MERGE）を外し、新規投入用 pia_inject.json を作る。
id は index.html の今の最大id+1 から振り直す（別セッションの投入とぶつからないように）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
NAME_MERGE = set()
src = open('index.html', encoding='utf-8').read()
_i = src.index('const EVENTS = [') + len('const EVENTS = ')
ev, _ = json.JSONDecoder().raw_decode(src[_i:])
mx = max(e['id'] for e in ev)
cds = set()
for e in ev:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        cds.update(re.findall(r'event(?:Bundle)?Cd=(\w+)', u))
out = []
nid = mx + 1
for b in json.load(open('tmp/x1001/eve/pia_built_new.json', encoding='utf-8')):
    if b['id'] in NAME_MERGE:
        continue
    c = re.search(r'event(?:Bundle)?Cd=(\w+)', (b.get('links') or {}).get('pia') or '').group(1)
    if c in cds:
        print('!! 既に登録にある eventCd=%s（%s）＝外す' % (c, b.get('artist')))
        continue
    b = dict(b, id=nid)
    out.append(b)
    nid += 1
json.dump(out, io.open('tmp/x1001/eve/pia_inject.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('最大id %d → 新規 %d件 id%d〜%d / 枠 %d' % (mx, len(out), out[0]['id'], out[-1]['id'], sum(len(e['tickets']) for e in out)))
