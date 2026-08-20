import re, json, sys, subprocess, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
for url in ['https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667295',
            'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668844',
            'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667004',
            'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667138',
            'https://t.pia.jp/pia/event/event.do?eventCd=2624996']:
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
    rows = json.loads(r.stdout.decode('utf-8','replace'))
    print("\n===", url, "全%d" % len(rows))
    print("   keys:", list(rows[0].keys()))
    for x in rows:
        if re.search(r'(予定枚数|完売|売り?切)', x.get('statustext') or '') or x.get('state') in ('受付中','発売前'):
            print("   *", json.dumps(x, ensure_ascii=False)[:400])
