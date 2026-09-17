# -*- coding: utf-8 -*-
# 新着プール（genre=="new"）の一覧を出す（振り分けの下見）
import re, json, io
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
new = [e for e in ev if e.get('genre') == 'new']
out = io.open('tmp/newpool_0918.txt', 'w', encoding='utf-8')
out.write(f"新着プール {len(new)}件\n")
cnt = {}
for e in sorted(new, key=lambda x: x['id']):
    L = e.get('links') or {}
    vends = [k for k in ('pia', 'rakuten', 'lawson', 'eplus') if L.get(k)]
    vend = '+'.join(vends) if vends else 'なし'
    g = e.get('_genre') or '-'
    cnt[vend] = cnt.get(vend, 0) + 1
    out.write(f"id{e['id']}\t{vend}\t{g}\t{e.get('_piaSub','-')}\t{e.get('artist','')[:38]}\t{e.get('date','')}\n")
out.write('\n=== 販売元の内訳 ===\n')
for k, v in sorted(cnt.items(), key=lambda x: -x[1]):
    out.write(f"{k}\t{v}件\n")
out.close()
print('ok', len(new))
