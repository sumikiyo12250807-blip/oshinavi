import re, json, sys, subprocess, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
SO = re.compile(r'(予定枚数|完売|売り?切)')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
tgt = [e for e in ev if any(t.get('soldout') for t in (e.get('tickets') or []))]

PREF = re.compile(r'（([^（）]*?)\s*(\d{1,2}/\d{1,2}(?:〜\d{1,2}/\d{1,2})?)公演）')
bad = []
for e in tgt:
    url = (e.get('links') or {}).get('pia')
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
    rows = json.loads(r.stdout.decode('utf-8','replace'))
    soldrows = [x for x in rows if SO.search(x.get('statustext') or '')]
    # ぴあ側の 完売 公演日集合
    solddates = set()
    for x in soldrows:
        d0, d1 = x.get('perfdate'), x.get('perf_end')
        solddates.add((d0, d1, x.get('pref')))
    mine = [t for t in e['tickets'] if t.get('soldout')]
    print("\n=== id%s %s" % (e['id'], (e.get('artist') or '')[:34]))
    print("   ぴあ完売枠(%d):" % len(soldrows), [(x['perfdate'], x['perf_end'], x['pref']) for x in soldrows])
    for t in mine:
        m = PREF.search(t['type'])
        pr, dr = (m.group(1), m.group(2)) if m else ('?', '?')
        # 公演日を YYYY-MM-DD に
        def toiso(md):
            mm, dd = md.split('/'); return '2026-%02d-%02d' % (int(mm), int(dd))
        parts = dr.split('〜') if dr != '?' else []
        s = toiso(parts[0]) if parts else None
        en = toiso(parts[1]) if len(parts) > 1 else s
        hit = any((x['perfdate'] or '') <= (en or '') and (x['perf_end'] or '') >= (s or '') for x in soldrows)
        prefhit = any(pr and any(p[:2] in (x.get('pref') or '') for p in pr.replace('・','／').split('／')) for x in soldrows) if pr != '?' else False
        flag = 'OK' if (hit and prefhit) else '❌不一致'
        if flag != 'OK':
            bad.append((e['id'], e.get('artist'), t['type']))
        print("   %s 登録枠: %s  (県=%s 公演=%s〜%s)" % (flag, t['type'], pr, s, en))

print("\n\n########## 裏取り不一致まとめ:", len(bad))
for b in bad:
    print("  id%s %s | %s" % b)
