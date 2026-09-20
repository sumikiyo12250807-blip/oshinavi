# -*- coding: utf-8 -*-
"""ぴあ発売前スイープ（tmp/x0921/presale_*.json）の未登録分から、
build_pia_entries に渡す候補JSON [{newid, artist, urls}] を作る。

同じアーティストの複数URLは1エントリにまとめる（ツアーは1エントリ＝feedback_tour_consolidate）。
🚨eventCd が既に index.html にあるものは外す（二重登録を名前でなくeventCdで見る
  ＝[[feedback_harvest_name_dedup_blindspot]]）。
"""
import glob, io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

h = io.open('index.html', encoding='utf-8', newline='').read()
have_cd = set(re.findall(r'event(?:Cd|BundleCd)=([0-9a-z]+)', h))

rows = []
for f in sorted(glob.glob('tmp/x0921/presale_*.json')):
    d = json.load(io.open(f, encoding='utf-8'))
    for r in (d.get('new') or []):
        r['_lg'] = d.get('lg')
        rows.append(r)

keys = sorted({k for r in rows for k in r})
out = io.open('tmp/x0921/cands_report.txt', 'w', encoding='utf-8')
out.write('未登録 %d件 / レコードのキー: %s\n\n' % (len(rows), keys))

cands, skipped = {}, []
for r in rows:
    url = r.get('url') or r.get('pia_url') or ''
    cd = re.search(r'event(?:Cd|BundleCd)=([0-9a-z]+)', url)
    if cd and cd.group(1) in have_cd:
        skipped.append((r.get('artist') or r.get('name'), url, 'eventCdが既に登録にある'))
        continue
    if not url:
        skipped.append((r.get('artist') or r.get('name'), '', 'URLが無い'))
        continue
    name = (r.get('artist') or r.get('name') or '').strip()
    d = cands.setdefault(name, {'newid': 91000 + len(cands), 'artist': name, 'urls': []})
    if url not in d['urls']:
        d['urls'].append(url)

json.dump(list(cands.values()), io.open('tmp/x0921/cands.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
out.write('=== 組む候補 %d件 ===\n' % len(cands))
for c in cands.values():
    out.write('  %-40s %s\n' % (c['artist'][:40], ' '.join(c['urls'])))
out.write('\n=== 外した %d件 ===\n' % len(skipped))
for n, u, why in skipped:
    out.write('  %-36s %-60s %s\n' % ((n or '')[:36], u[:60], why))
out.close()
print('候補 %d件 / 外した %d件 → tmp/x0921/cands.json' % (len(cands), len(skipped)))
