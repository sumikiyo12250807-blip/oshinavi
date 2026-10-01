# -*- coding: utf-8 -*-
# 夜の livePocket 組み立て結果から、まだ登録していないページだけを抜き出す → tmp/x1001/eve/lp_new_eve.json
import io, json, re
root = 'C:/Users/user/oshinavi/'
src = io.open(root + 'index.html', encoding='utf-8').read()
reg = set(re.findall(r'livepocket\.jp/e/([\w-]+)', src))
B = json.load(io.open(root + 'tmp/x1001/eve/built_livepocket_eve.json', encoding='utf-8'))
items = B if isinstance(B, list) else B.get('entries') or B.get('events') or []
out = []
for e in items:
    codes = set(re.findall(r'livepocket\.jp/e/([\w-]+)', json.dumps(e, ensure_ascii=False)))
    if codes and not (codes & reg):
        out.append(e)
json.dump(out if isinstance(B, list) else dict(B, **{('entries' if 'entries' in B else 'events'): out}),
          io.open(root + 'tmp/x1001/eve/lp_new_eve.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('組み立て', len(items), '→ 未登録', len(out))
