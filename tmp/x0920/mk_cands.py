# -*- coding: utf-8 -*-
"""ぴあの発売前ハーベスタの「新候補」を build_pia_entries の入力に整える（2026-09-20 朝）。

🚨投入前に**既存の同名エントリ**を必ず見る＝ツアーが分裂して二重登録になる
  （2026-08-18に39件が分裂していた／[[feedback_check_duplicates]]／[[feedback_tour_individual_url_dup]]）。
  ここでは「同名あり」を別立てにして、統合先の候補を添えるだけ（自動では畳まない）。
出力: tmp/x0920/cands.json（新規）／tmp/x0920/cands_samename.md（同名あり＝人が見る）
"""
import io, json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
maxid = max(e['id'] for e in EVENTS)


def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s　\[\]［］（）()【】「」｜|/・,、.]+', '', s).lower()


by_name = {}
for e in EVENTS:
    by_name.setdefault(norm(e.get('artist') or e.get('name')), []).append(e)

rows = []
for f in ('tmp/x0920/presale_01.json', 'tmp/x0920/presale_02.json', 'tmp/x0920/presale_07.json'):
    try:
        rows += json.load(io.open(f, encoding='utf-8')).get('new') or []
    except Exception as e:
        print('読めない %s (%s)' % (f, e))

seen, cands, same = set(), [], []
nid = maxid
for r in rows:
    u = r['url']
    if u in seen or u in h:
        continue
    seen.add(u)
    hit = by_name.get(norm(r['artist']))
    nid += 1
    rec = {'newid': nid, 'artist': r['artist'], 'urls': [u]}
    if hit:
        same.append((r, [e['id'] for e in hit]))
    else:
        cands.append(rec)

io.open('tmp/x0920/cands.json', 'w', encoding='utf-8').write(json.dumps(cands, ensure_ascii=False))
with io.open('tmp/x0920/cands_samename.md', 'w', encoding='utf-8') as f:
    f.write('# 同名の既存エントリがある新候補 %d件（自動では畳まない）\n\n' % len(same))
    for r, ids in same:
        f.write('- %s（%s 発売 / 公演 %s / %s）既存 id%s\n  - %s\n'
                % (r['artist'][:46], r.get('rlsdate'), r.get('perfdate'), r.get('pref'), ids, r['url']))
print('新候補 %d件 → tmp/x0920/cands.json（id %d〜）／同名あり %d件'
      % (len(cands), maxid + 1, len(same)))
