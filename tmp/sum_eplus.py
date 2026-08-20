import re, collections, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
txt = open('tmp/recon_eplus_0815.txt', encoding='utf-8').read()
kinds = collections.Counter()
ids = collections.defaultdict(set)
for m in re.finditer(r'id(\d+) t\d+ \[([^\]]+)\]', txt):
    kinds[m.group(2)] += 1
    ids[m.group(2)].add(m.group(1))
for k, v in kinds.most_common():
    print(f'{k}: {v}枠 / {len(ids[k])}エントリ  ->', ' '.join(sorted(ids[k], key=int)))
