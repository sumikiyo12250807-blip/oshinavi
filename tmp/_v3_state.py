import re, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\Users\user\oshinavi')
h = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
print("EVENTS件数:", len(ev))
raw = open('index.html','rb').read()
print("CRLF:", raw.count(b'\r\n'), "単独LF:", len(re.findall(rb'(?<!\r)\n', raw)))
byid = {e['id']: e for e in ev}

print("\n=== soldout枠 全件（売り手つき） ===")
for e in ev:
    for t in (e.get('tickets') or []):
        if not t.get('soldout'): continue
        u = t.get('url') or ''
        lk = e.get('links') or {}
        vendor = 'e+(枠URL)' if 'eplus.jp' in u else ('楽天(枠URL)' if 'rakuten' in u or 'linksynergy' in u else
                 ('ぴあ(枠URL)' if 't.pia.jp' in u else ('枠URL無→pia' if lk.get('pia') else '枠URL無→'+','.join(k for k,v in lk.items() if v))))
        print("  id%-5s %-9s | %-50s | 売り手=%s" % (
            e['id'], '販売終了' if t.get('saleEnded') else '予定枚数終了', (t.get('type') or '')[:50], vendor))
        if u: print("        url=%s" % u)

print("\n=== id1149 / id2300 ===")
for i in (1149, 2300):
    print(json.dumps(byid[i], ensure_ascii=False, indent=1))
