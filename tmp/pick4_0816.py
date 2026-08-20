# -*- coding: utf-8 -*-
"""2バッチ目の不足分。①混雑ページで取り込めなかった2件を拾い直す ②演劇の受付中から足す。
出力は build にかける候補（cand形式）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

src = open('index.html', 'rb').read().decode('utf-8')
have = set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', src))
# 既に build 済みで最終50件に入る予定のもの
final = json.load(open('tmp/built_final2_0816.json', encoding='utf-8'))
used = set(re.findall(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', json.dumps(final, ensure_ascii=False)))

def cd(u):
    m = re.search(r'event(?:Bundle)?Cd=([0-9a-zA-Z]+)', u or '')
    return m.group(1) if m else ''

out = []
# ① 混雑で落ちた大物2件
for artist, url in [("ずっと真夜中でいいのに。", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670292"),
                    ("sumika×瑠東東一郎 CINEMA&LIVE", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668774")]:
    if cd(url) not in have and cd(url) not in used:
        out.append({'newid': 0, 'artist': artist, 'urls': [url], '_grp': 'retry'})
        used.add(cd(url))

# ② 演劇の受付中
rows = json.load(open('tmp/onsale_engeki_0816.json', encoding='utf-8'))['new']
order, groups = [], {}
for r in rows:
    a = r['artist']
    if a not in groups:
        groups[a] = []; order.append(a)
    groups[a].append(r)
for a in order:
    if len(out) >= 14:      # 多めに取って締切で落とす
        break
    urls = [x['url'] for x in groups[a]]
    codes = [cd(u) for u in urls]
    if any(x and (x in have or x in used) for x in codes):
        continue
    used.update(x for x in codes if x)
    out.append({'newid': 0, 'artist': a, 'urls': urls, '_grp': 'engeki_onsale'})

for i, c in enumerate(out):
    c['newid'] = 4500 + i
json.dump(out, open('tmp/cand_pick3_0816.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("追加候補 %d件" % len(out))
for c in out:
    print("  %d [%s] %s" % (c['newid'], c['_grp'], c['artist'][:40]))
