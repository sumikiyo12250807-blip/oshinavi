import re, json, sys, subprocess, os, datetime
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
TODAY = '2026-08-14'
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
tgt = [e for e in ev if any(t.get('soldout') for t in (e.get('tickets') or []))]
print("soldoutエントリ:", len(tgt))
for e in tgt:
    url = (e.get('links') or {}).get('pia')
    print("\n=== id%s %s  公演日=%s  pia=%s" % (e['id'], (e.get('artist') or '')[:30], e.get('date'), url))
    for t in e['tickets']:
        print("   登録: %s | date=%s start=%s soldout=%s" % (t.get('type'), t.get('date'), t.get('startDate'), t.get('soldout')))
    if not url:
        print("   >> ぴあURLなし"); continue
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
    try:
        rows = json.loads(r.stdout.decode('utf-8','replace'))
    except Exception as ex:
        print("   >> 読めず", ex, r.stdout[:200]); continue
    buy = [x for x in rows if x.get('state') in ('受付中','発売前')]
    soldwords = [x for x in rows if re.search(r'(予定枚数|完売|売り?切)', x.get('statustext') or '')]
    print("   ぴあ: 全%d券種 買える=%d 予定枚数終了系=%d" % (len(rows), len(buy), len(soldwords)))
    for x in buy:
        print("      [買える] %s | %s | %s | %s" % (x.get('state'), x.get('name'), x.get('statustext'), x.get('pref') or x.get('venue')))
    for x in soldwords[:8]:
        print("      [完売表示] %s | %s | %s" % (x.get('name'), x.get('statustext'), x.get('showdate') or ''))
    if not soldwords:
        kinds = sorted({(x.get('statustext') or '?') for x in rows})
        print("      >> 完売表示ゼロ! statustext種別:", "／".join(kinds)[:200])
