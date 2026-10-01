import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
for u in sys.argv[1:]:
    t = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20).read().decode("utf-8", "ignore")
    print("=====", u)
    for m in sorted(set(re.findall(r'href="([^"]+)"', t))):
        if any(k in m for k in ("ticketInformation", "perfCd", "rlsCd", "eventCd")):
            print(html.unescape(m))
    for m in re.findall(r"[^<>]{0,40}(?:開演|開場)[^<>]{0,40}", t):
        print("TIME:", m.strip())
