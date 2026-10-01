import urllib.request, re, html, sys
sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
urls = sys.argv[1:] or [f"https://www.suntory.co.jp/suntoryhall/schedule/detail/{d}_M_{n}.html" for d in ("20270206", "20270207") for n in (1, 2, 3)]
for u in urls:
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20)
        raw = r.read()
        t = raw.decode("utf-8", "ignore")
        t = re.sub(r"(?is)<(script|style).*?</\1>", "", t)
        t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
        t = re.sub(r"\n\s*\n+", "\n", t)
        print("=====", u, r.status)
        print(t[:6000])
    except Exception as e:
        print("=====", u, "ERR", e)
