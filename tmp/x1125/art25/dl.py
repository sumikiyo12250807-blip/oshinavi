import sys, urllib.request, time, os
# 使い方: dl.py URL 保存名 ...（そのまま保存・4秒おき）
D = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[1:]
for k in range(0, len(a), 2):
    if k: time.sleep(4)
    req = urllib.request.Request(a[k], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36', 'Accept-Language': 'ja', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    try:
        b = urllib.request.urlopen(req, timeout=40).read()
        open(os.path.join(D, a[k + 1]), 'wb').write(b)
        print(a[k + 1], len(b))
    except Exception as e:
        print(a[k + 1], 'ERR', repr(e))
