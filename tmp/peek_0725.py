import json, re, sys, collections

TODAY = '2026-07-25'
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

def stale(t):
    sd, d = t.get('startDate'), t.get('date')
    return bool(sd and sd == d and d <= TODAY and not t.get('saleUntilSoldOut'))

# 1) 残り隠れ枠の startDate 分布（いつ発売の子が残っているか）
cnt = collections.Counter()
for e in EV:
    for t in e.get('tickets', []):
        if stale(t):
            cnt[t.get('startDate')] += 1
print('=== 残り隠れ枠の発売日分布 ===')
for k in sorted(cnt):
    print(' ', k, cnt[k], '枠')

# 2) サンプル3件の現物
print('\n=== サンプル ===')
for eid in (2082, 1357, 2805):
    e = next((x for x in EV if x.get('id') == eid), None)
    if not e:
        continue
    print(f"\nid={eid} {e.get('artist')} / {e.get('name')} date={e.get('date')}")
    print('  pia:', (e.get('links') or {}).get('pia'))
    for t in e.get('tickets', []):
        flag = 'HIDDEN' if stale(t) else '      '
        print(f"  [{flag}] {t.get('type')} | date={t.get('date')} start={t.get('startDate')} url={t.get('url')}")
