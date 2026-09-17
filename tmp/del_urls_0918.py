# -*- coding: utf-8 -*-
# 削除候補の公演名＋確認用の直URLを index.html から機械抽出する（手書き禁止）
import re, json, io
IDS = [421,922,1111,1230,2105,3246,3276,3656,3708,3853,4157,4158,4263,4264,5036,6209,6250,
        6948,6957,7083,7185,7456,7458,7470,7507,7511,7593,7699,7780,8032,8153,8414,9506,
        9755,9382,9055,8829]
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
by = {e['id']: e for e in ev}
out = io.open('tmp/del_urls_0918.md', 'w', encoding='utf-8')
out.write('# 2026-09-18 朝 削除（公演が終わったエントリ）\n\n')
miss = []
for i in IDS:
    e = by.get(i)
    if not e:
        miss.append(i)
        continue
    L = e.get('links') or {}
    url = ''
    for k in ('pia', 'rakuten', 'lawson', 'eplus'):
        if L.get(k):
            url = L[k]
            break
    if not url:
        for t in e.get('tickets', []):
            if t.get('url'):
                url = t['url']
                break
    out.write(f"- id{i} {e.get('artist','')} @ {e.get('venue','')}（公演 {e.get('date','')}）\n")
    out.write(f"  - {url if url else '（URLなし）'}\n")
out.write(f"\n合計 {len(IDS)-len(miss)}件")
if miss:
    out.write(f" / index.htmlに無いid: {miss}")
out.write('\n')
out.close()
print('ok', len(IDS) - len(miss), 'miss', miss)
