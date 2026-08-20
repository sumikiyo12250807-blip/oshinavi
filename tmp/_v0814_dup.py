import re, json, sys, os, collections
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
d = collections.defaultdict(list)
for e in ev:
    d[(e.get('date'), e.get('venue'), e.get('prefecture'))].append(e['id'])
dups = {k: v for k, v in d.items() if len(v) > 1 and k[1] and '全国ツアー' not in (k[1] or '')}
print("■ 同日・同会場・同県の重複候補:", len(dups))
byid = {e['id']: e for e in ev}
for k, v in sorted(dups.items()):
    print("  ", k[0], k[1][:30], v, [ (byid[i].get('artist') or '')[:22] for i in v])
