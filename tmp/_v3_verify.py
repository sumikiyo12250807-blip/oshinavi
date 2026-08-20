import re, json, sys, subprocess, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
SO = re.compile(r'(予定枚数|完売|売り?切)')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
PREF = re.compile(r'（([^（）]*?)\s*(\d{1,2}/\d{1,2}(?:〜\d{1,2}/\d{1,2})?)公演）')
def toiso(md):
    mm, dd = md.split('/'); return '2026-%02d-%02d' % (int(mm), int(dd))

cache = {}
def pia(url):
    if url not in cache:
        r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
        try: cache[url] = json.loads(r.stdout.decode('utf-8','replace'))
        except Exception: cache[url] = None
    return cache[url]

bad = []
print("■ ぴあ売りの soldout枠を1枠ずつ照合")
for e in ev:
    url = (e.get('links') or {}).get('pia')
    for t in (e.get('tickets') or []):
        if not t.get('soldout'): continue
        if 'eplus.jp' in (t.get('url') or ''): continue   # e+売りは別途
        rows = pia(url) if url else None
        if rows is None:
            print("  id%-5s ⚠️ぴあ読めず %s" % (e['id'], t['type'][:40])); continue
        m = PREF.search(t['type'])
        pr, dr = (m.group(1), m.group(2)) if m else ('?', '?')
        parts = dr.split('〜'); s = toiso(parts[0]); en = toiso(parts[-1])
        cand = [x for x in rows
                if (x.get('perfdate') or '') <= en and (x.get('perf_end') or '') >= s
                and any(p[:2] in (x.get('pref') or '') for p in pr.replace('・','／').split('／'))]
        sold = [x for x in cand if SO.search(x.get('statustext') or '')]
        want_sold = not t.get('saleEnded')
        ok = (len(sold) > 0) == want_sold
        # 買える枠が同公演にあるか（取扱なしは除く）
        buy = [x for x in cand if x.get('state') in ('受付中','発売前')
               and '取扱なし' not in (x.get('statustext') or '')]
        mark = 'OK ' if ok and not buy else '❌ '
        if mark != 'OK ': bad.append((e['id'], e.get('artist'), t['type'], '予定枚数終了' if want_sold else '販売終了',
                                      [x.get('statustext') for x in cand], [x.get('statustext') for x in buy]))
        print("  %sid%-5s %-9s | %-46s | ぴあ該当%d件 状態=%s 買える=%d" % (
            mark, e['id'], '販売終了' if t.get('saleEnded') else '予定枚数終了', t['type'][:46],
            len(cand), '／'.join(sorted({x.get('statustext') or '?' for x in cand}))[:40], len(buy)))

print("\n■ 不一致まとめ:", len(bad))
for b in bad: print("   ", b)
