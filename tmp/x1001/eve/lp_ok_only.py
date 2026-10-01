# -*- coding: utf-8 -*-
# 独立の番人で食い違った livePocket を外し、一致した分だけ lp_ok_eve.json に書く
import io, json, re
root = 'C:/Users/user/oshinavi/'
log = io.open(root + 'tmp/x1001/eve/lp_gate.txt', encoding='utf-8', errors='replace').read()
bad = set(re.findall(r'^\[\d+/\d+\] (?:id \d+ )?([\w-]+) .*?… 🚨', log, re.M))
B = json.load(io.open(root + 'tmp/x1001/eve/lp_new_eve.json', encoding='utf-8'))
items = B['entries'] if isinstance(B, dict) else B
ok, ng = [], []
for e in items:
    codes = set(re.findall(r'livepocket\.jp/e/([\w-]+)', json.dumps(e, ensure_ascii=False)))
    (ng if codes & bad else ok).append(e)
json.dump({'entries': ok}, io.open(root + 'tmp/x1001/eve/lp_ok_eve.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open(root + 'tmp/x1001/eve/lp_ng.txt', 'w', encoding='utf-8').write(
    '食い違いで外した %d件\n' % len(ng) + '\n'.join('%s | %s' % (e.get('name', '')[:50], ','.join(sorted(set(re.findall(r'livepocket\.jp/e/([\w-]+)', json.dumps(e)))))) for e in ng) + '\n')
print('bad', len(bad), 'ok', len(ok), 'ng', len(ng))
