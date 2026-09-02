# -*- coding: utf-8 -*-
"""取りこぼし監査で出た未登録45件を build_pia_entries の入力形にする。
URLは監査の出力（機械抽出）からそのまま拾う＝手で書かない。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

TXT = 'tmp/x_leftover_0902.txt'
TODAY = datetime.date.today()
rows, cur_kw = [], None
lines = open(TXT, encoding='utf-8').read().split('\n')
for i, ln in enumerate(lines):
    m = re.match(r'\[\d+/\d+\] 🚨 (.+?) … 未登録', ln)
    if m:
        cur_kw = m.group(1)
        continue
    m = re.match(r'^      (.+?) \| 公演(.*?) \| 発売(.*?) \| (.*)$', ln)
    if m and cur_kw:
        title, perf, rls, venue = [x.strip() for x in m.groups()]
        url = lines[i + 1].strip() if i + 1 < len(lines) else ''
        if not url.startswith('http'):
            continue
        # 公演日が過ぎているものは載せない
        pm = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', perf)
        if pm:
            d = datetime.date(int(pm.group(1)), int(pm.group(2)), int(pm.group(3)))
            if d < TODAY:
                continue
        rows.append({'kw': cur_kw, 'title': title, 'perf': perf, 'venue': venue, 'url': url})

# 同じURLが複数キーワードで出ることがある
seen, uniq = set(), []
for r in rows:
    if r['url'] in seen:
        continue
    seen.add(r['url'])
    uniq.append(r)

h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
nid = max(e['id'] for e in EV) + 1
cands = []
for r in uniq:
    cands.append({'newid': nid, 'artist': r['title'], 'urls': [r['url']]})
    nid += 1
json.dump(cands, open('tmp/leftover_in_0902.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'未登録 {len(rows)}件 → URL重複除去 {len(uniq)}件（公演日が過去のものは除外済み）')
print(f'採番 id {cands[0]["newid"]}-{cands[-1]["newid"]}' if cands else '候補なし')
import collections
c = collections.Counter(r['kw'] for r in uniq)
for k, v in c.most_common():
    print(f'  {k[:40]} … {v}件')
