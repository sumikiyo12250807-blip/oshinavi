# 総ざらい（tmp/x0920/audit_posts.txt）の本命のうち、artist名がそっくり同じエントリが1つだけのものを足し込み候補にする
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
txt = io.open('tmp/x0920/audit_posts.txt', encoding='utf-8').read()
body = txt.split('別名義・フェス出演の候補')[0]
SKIP = {'HARU', '新日本プロレス', '大阪プロレス'}
out, skipped = [], []
for blk in re.split(r'\n● ', body)[1:]:
    kw = blk.split('  （')[0].strip()
    urls = re.findall(r'URL\s*:\s*(\S+)', blk)
    if kw in SKIP:
        skipped.append((kw, '手で外した'))
        continue
    hits = [e for e in EV if e.get('genre') != 'new' and (e.get('artist') or '').strip() == kw]
    if len(hits) != 1:
        skipped.append((kw, '同名エントリ%d件' % len(hits)))
        continue
    e = hits[0]
    us = [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e['tickets']]
    us = [u for u in dict.fromkeys(us) if u and 'pia.jp' in u and 'w.pia.jp' not in u]
    for u in urls:
        if u not in us:
            us.append(u)
    out.append({'newid': e['id'], 'artist': e['artist'], 'urls': us})
json.dump(out, io.open('tmp/x0920/cands_audit.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('足し込み候補', len(out), [o['artist'] for o in out])
for s in skipped:
    print('  外した', s)
