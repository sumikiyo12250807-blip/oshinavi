# -*- coding: utf-8 -*-
"""id6972 ハナレグミ の完全重複1枠を畳む（type・締切・飛び先URLが全部同じ2枚）。

🚨 `dedup_badges.py` は流さない＝今日は統合とURL焼き込みをした直後なので、
   常設ツールを全体にかけると直した内容を壊すことがある（[[feedback_dedup_badges_keeps_urls]]）。
   ここは対象を id6972 に限って、**完全一致（type・date・startDate・url すべて同じ）**のときだけ落とす。

🚨 index.html は newline='' で読み書き＋json.dumps の改行を元の改行コードへ置換（CRLFを壊さない）。
"""
import json, io, re

PATH = 'index.html'
h = io.open(PATH, encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

e = by[6972]
before = len(e['tickets'])
seen, keep = set(), []
for t in e['tickets']:
    k = (t.get('type'), t.get('date'), t.get('startDate'), t.get('url'), t.get('soldout'))
    if k in seen:
        continue
    seen.add(k)
    keep.append(t)
e['tickets'] = keep
assert before - len(keep) == 1, (before, len(keep))

bak = 'index.html.bak_0905_fold6972'
io.open(bak, 'w', encoding='utf-8', newline='').write(h)
NL = '\r\n' if '\r\n' in h else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(PATH, 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print('id6972 tickets %d -> %d (backup %s)' % (before, len(keep), bak))
