# -*- coding: utf-8 -*-
"""新規候補 → build_pia_entries の入力を作る。
🚨同じアーティストが複数URLで出てきたら**1エントリにまとめる**（ツアーは1エントリ＝feedback_tour_consolidate）。
   ただしスポーツは対戦カードごとに別売り場なので、まとめない（feedback_sports_home_away_never_merge）。"""
import json, io, re, sys, unicodedata, collections
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('tmp/batch_cand_0828.json', encoding='utf-8'))
cand = d['cand']

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　・･/／「」『』【】（）()\[\]～~ー-]', '', s).lower()

def pia_norm(u):
    return u.replace('http://', 'https://').replace('ticket.pia.jp/pia/event.do', 't.pia.jp/pia/event/event.do')

# 既存の最大idの次から採番
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
nextid = max(e['id'] for e in EV) + 1

groups = collections.OrderedDict()
for it in cand:
    k = (it['_lg'], norm(it['artist'])) if it['_lg'] != 'スポーツ' else ('スポーツ', it['url'])
    groups.setdefault(k, []).append(it)

out = []
for k, items in groups.items():
    urls = []
    for it in items:
        u = pia_norm(it['url'])
        if u not in urls:
            urls.append(u)
    out.append({'newid': nextid, 'artist': items[0]['artist'], 'urls': urls,
                '_lg': items[0]['_lg'], '_rls': items[0]['_rls'], '_perf': items[0].get('perfdate')})
    nextid += 1
io.open('tmp/build_in_0828.json', 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
multi = [o for o in out if len(o['urls']) > 1]
print('候補 %d件 → %dエントリ（複数URLを束ねたもの %d件）' % (len(cand), len(out), len(multi)))
for o in multi:
    print('   %s ← %d本' % (o['artist'][:40], len(o['urls'])))
print('id は %d から' % out[0]['newid'])
