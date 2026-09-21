# -*- coding: utf-8 -*-
"""aiko（歌手）が今のOSHINAVIに載っているか、今日の収集に出てきたかを機械で探す。
🚨部分一致（taiko/daiko/saiko/大工…）を拾わないよう、名前が「aiko」単独か
「アイコ」で始まる/囲まれている場合だけ数える。
"""
import glob, io, json, re, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
out = io.open('tmp/x0921/find_aiko.txt', 'w', encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))

WORD = re.compile(r'(?<![A-Za-z])aiko(?![A-Za-z])', re.I)
hits = []
for e in ev:
    for f in ('artist', 'name'):
        if WORD.search(e.get(f) or ''):
            hits.append(e)
            break
out.write('=== 登録されている aiko（名前が単独一致）= %d件 ===\n' % len(hits))
for e in hits:
    out.write('id%-6s %-10s 公演%s %-28s @ %s\n'
              % (e['id'], e.get('genre'), e.get('date'), (e.get('artist') or '')[:28],
                 (e.get('venue') or '')[:24]))
    for t in e.get('tickets') or []:
        fl = ' '.join(k for k in ('soldout', 'saleEnded', 'presaleEnded', 'saleEndUnknown')
                      if t.get(k))
        out.write('      %s | date=%s %s\n' % ((t.get('type') or '')[:66], t.get('date'), fl))
    out.write('      links: %s\n' % {k: v for k, v in (e.get('links') or {}).items() if v})

out.write('\n=== 今日の収集ファイルに aiko が出てきたか ===\n')
for f in sorted(glob.glob('tmp/x0921/presale_*.json') + glob.glob('tmp/x0921/uke*.json')):
    try:
        d = json.load(io.open(f, encoding='utf-8'))
    except Exception:
        continue
    rows = (d.get('new') or []) + (d.get('rows') or [])
    m = [r for r in rows if WORD.search(str(r.get('artist') or '') + str(r.get('name') or ''))]
    out.write('  %-34s 行%-5d うち aiko %d\n' % (f.split('/')[-1], len(rows), len(m)))
    for r in m:
        out.write('      %s | %s | %s\n' % (r.get('rlsdate'), r.get('artist'), r.get('url')))
out.close()
print('登録 %d件 → tmp/x0921/find_aiko.txt' % len(hits))
