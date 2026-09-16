# -*- coding: utf-8 -*-
"""受付中バッチを「投入」と「既存に足す」に分ける（2026-09-11）。
  8021 未唯mie Celebration（ぴあ）→ 既存 6239（e+のみ登録・同じ9/19 国際フォーラムC）に足す
  7998 日乃まそら 9/26 duo は dedup で「既存に無い窓あり」として fresh から外れている＝保留
出力: tmp/inject_uk_0911.json ／ tmp/built_mergeU_0911.json ／ tmp/cand_mergeU_0911.json
"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
fresh = json.load(io.open('tmp/built_uk_0911_fresh.json', encoding='utf-8-sig'))
MERGE = {8021: 6239}
inj, mb, mc = [], [], []
for e in fresh:
    if e['id'] in MERGE:
        e = json.loads(json.dumps(e))
        url = (e.get('links') or {}).get('pia')
        for t in e['tickets']:
            t['url'] = t.get('url') or url
        e['id'] = MERGE[e['id']]
        mb.append(e)
        mc.append({'newid': e['id'], 'artist': e['artist'], 'urls': [url]})
    else:
        inj.append(e)
json.dump(inj, io.open('tmp/inject_uk_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mb, io.open('tmp/built_mergeU_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mc, io.open('tmp/cand_mergeU_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('投入 %d件 ／ 既存に足す %d件' % (len(inj), len(mb)))
