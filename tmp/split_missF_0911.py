# -*- coding: utf-8 -*-
"""missF のビルド結果を分ける：
  9201 神韻 → 既存 5675 に足す／9202〜9207 BTTF ぴあシート2027年4〜9月 → 既存 96 に足す（飛び先を焼き込む）
  9301〜9304 → 新着（新しいidを振る）"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
MAP = {9201: 5675, 9202: 96, 9203: 96, 9204: 96, 9205: 96, 9206: 96, 9207: 96}
b = json.load(io.open('tmp/built_missF_0911.json', encoding='utf-8-sig'))
mb, mc, new = [], [], []
for e in b:
    u = e['links']['pia']
    if e['id'] in MAP:
        for t in e['tickets']:
            t['url'] = t.get('url') or u
        e['id'] = MAP[e['id']]
        mb.append(e)
        mc.append({'newid': e['id'], 'artist': e['artist'], 'urls': [u]})
    else:
        new.append(e)
src = open('index.html', encoding='utf-8').read()
maxid = max(int(x) for x in re.findall(r'"id": (\d+),', src))
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))
start = max(maxid, max(x.get('id_to') or 0 for x in lb['batches'])) + 1
for k, e in enumerate(new):
    e['id'] = start + k
json.dump(mb, io.open('tmp/built_mergeF_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mc, io.open('tmp/cand_mergeF_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(new, io.open('tmp/inject_missF_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('既存に足す %d件 ／ 新着 %d件（id %d〜）' % (len(mb), len(new), start))
