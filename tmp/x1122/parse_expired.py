import re, json, collections, io, sys
D = 'C:/Users/user/oshinavi/tmp/x1122/'
txt = io.open(D + 'expired.txt', encoding='utf-8', errors='replace').read()
out = io.open(D + 'expired_headers.txt', 'w', encoding='utf-8')
b = collections.defaultdict(list)
for m in re.finditer(r'^  id=(\d+): (.*)\[([^\]]*)\]\s*$', txt, re.M):
    tag = m.group(3)
    if '📺' in tag: k = 'live'
    elif tag.startswith('開催終了'): k = 'del'
    else: k = re.sub(r'[\d/\-]+', '#', tag)[:40]
    b[k].append((int(m.group(1)), m.group(2), tag))
for k, v in b.items():
    out.write(f'{k} => {len(v)}\n')
    for i, r, t in v[:4]:
        out.write(f'   {i} {r[:100]} [{t}]\n')
out.write('\n--- 先頭 ---\n' + txt[:1500])
json.dump({k: [x[0] for x in v] for k, v in b.items()},
          io.open(D + 'expired.json', 'w', encoding='utf-8'), ensure_ascii=False)
