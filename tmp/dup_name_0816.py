# -*- coding: utf-8 -*-
"""新着50件(id4326-4375)が既存エントリと同じ公演を重複登録していないかを、
eventCdでなく「正規化アーティスト名＋公演日/会場」で突き合わせる（表記ゆれですり抜ける型の検出）。"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

raw = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))
new = [e for e in EVENTS if 4326 <= e['id'] <= 4375]
old = [e for e in EVENTS if not (4326 <= e['id'] <= 4375)]

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\s　]', '', s)
    s = re.sub(r'[「」『』（）\(\)【】\[\]~〜～\-–—・,、.。!！?？"\'’”]', '', s)
    return s.lower()

def key_words(e):
    """アーティスト名の頭16文字（記号除去）"""
    return norm(e.get('artist') or e.get('name') or '')[:16]

idx = {}
for e in old:
    idx.setdefault(key_words(e), []).append(e)

hits = 0
for e in new:
    k = key_words(e)
    if not k:
        continue
    cands = []
    for ok, lst in idx.items():
        if not ok:
            continue
        if k == ok or (len(k) >= 6 and (k in ok or ok in k)):
            cands.extend(lst)
    for c in cands:
        same_venue = norm(c.get('venue'))[:10] and norm(c.get('venue'))[:10] == norm(e.get('venue'))[:10]
        same_date = c.get('date') == e.get('date')
        flag = "🚨同会場かつ同千秋楽" if (same_venue and same_date) else ("⚠️同名" )
        print("%s  新id%-5s %s / %s / %s" % (flag, e['id'], (e.get('artist') or '')[:26], e.get('venue', '')[:22], e.get('date')))
        print("            既存id%-5s %s / %s / %s" % (c['id'], (c.get('artist') or '')[:26], c.get('venue', '')[:22], c.get('date')))
        hits += 1

print()
print("=== 同名の当たり %d 件（🚨は要統合の可能性・⚠️は別公演なら問題なし）===" % hits)
