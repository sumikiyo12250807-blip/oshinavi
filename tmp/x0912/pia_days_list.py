# -*- coding: utf-8 -*-
"""ぴあの発売前一覧（指定ジャンル・先着0102/抽選0202）を全ページ読み、発売日が 9/12〜9/14 の行を全部出して、
OSHINAVIにその発売日の枠があるかを突き合わせる（読むだけ）。
使い方: python tmp/x0912/pia_days_list.py <lg>   例: 01=音楽 02=演劇 07=クラシック 06=イベント 03=スポーツ
🚨 presale_harvest は読み込むと本体が走るので、一覧の読み取り部分（parse_page）だけを取り出して使う。
"""
import io, json, re, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
LG = sys.argv[1] if len(sys.argv) > 1 else '01'
DAYS = {'2026/9/12': '2026-09-12', '2026/9/13': '2026-09-13', '2026/9/14': '2026-09-14'}
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

# presale_harvest.py から関数定義だけを取り出して使う（本体は走らせない）
import html
code = io.open('tools/presale_harvest.py', encoding='utf-8').read()
ns = {'re': re, 'sys': sys, 'html': html}
a = code.index('def strip(')
b = code.index("\nif '--selftest' in sys.argv")
exec(code[a:b], ns)

src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
cd2e = {}
for e in ev:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', u):
            cd2e.setdefault(c, e)
hits = []
for filt in ('rlsStatus=0102', 'rlsStatus=0202'):
    page, prev = 1, None
    while page < 150:
        url = 'https://t.pia.jp/pia/rlsInfo.do?lg=%s&%s&page=%d' % (LG, filt, page)
        h = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        rows = ns['parse_page'](h)
        sig = [r.get('url') for r in rows]
        if not rows or sig == prev:
            break
        prev = sig
        for r in rows:
            d = (r.get('rlsdate') or '').split('(')[0]
            if d in DAYS:
                hits.append((DAYS[d], r))
        page += 1
        time.sleep(0.6)
miss = []
for iso, r in sorted(hits, key=lambda x: x[0]):
    m = re.search(r'event(?:Bundle)?Cd=(\w+)', r['url'])
    e = cd2e.get(m.group(1)) if m else None
    has = bool(e) and any(t.get('startDate') == iso for t in e.get('tickets') or [])
    if not has:
        miss.append((iso, r, e))
print('ぴあ lg=%s で9/12〜9/14発売の行 %d件 ／ OSHINAVIにその日の枠が無い %d件' % (LG, len(hits), len(miss)))
for iso, r, e in miss:
    print('  %s %s | %s | %s | %s' % (iso, r.get('artist'), r.get('saletype'), r.get('venue'),
          ('登録あり id%s（その日の枠なし）' % e['id']) if e else ('未登録 ' + r['url'])))
