#!/usr/bin/env python3
"""投入前の重複チェック（eventCd＋NFKC正規化名）。build済47件 vs 既存DB。
[[feedback_harvest_dedup_check]]＝harvestのDB照合はすり抜けるので投入前に必ず。"""
import json
import re
import sys
import unicodedata
sys.path.insert(0, 'tools')
from check_expired import extract_events_array  # noqa

EVENTS = extract_events_array('index.html')
BUILT = json.load(open('tmp/built_0715pm.json', encoding='utf-8'))


def ecds(e):
    out = set()
    u = (e.get('links') or {}).get('pia') or ''
    for t in [u] + [t.get('url', '') for t in (e.get('tickets') or [])]:
        m = re.search(r'event(?:Bundle)?Cd=(\w+)', t or '')
        if m:
            out.add(m.group(1))
    return out


def nn(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・／/＜＞<>「」『』（）()【】’\'"!！\-—~〜ー]', '', s).lower()


old_ecd = {}
old_name = {}
for e in EVENTS:
    for c in ecds(e):
        old_ecd.setdefault(c, e)
    old_name.setdefault(nn(e.get('name')), e)

hits = 0
for b in BUILT:
    dup_e = None
    for c in ecds(b):
        if c in old_ecd:
            dup_e = old_ecd[c]; kind = f'eventCd {c}'; break
    if not dup_e:
        k = nn(b.get('name'))
        if k in old_name:
            dup_e = old_name[k]; kind = '正規化名'
    if dup_e:
        hits += 1
        print(f"🚨 重複 id={b['id']} {b.get('name')}")
        print(f"    ({kind}) → 既存 id={dup_e.get('id')} {dup_e.get('name')} / genre={dup_e.get('genre')}")

print(f"\n=== 重複 {hits}件 / build {len(BUILT)}件 ===" + ('' if hits else ' クリーン'))
