# -*- coding: utf-8 -*-
"""oshinavi.jp のOGPがXで読めるかを機械で測る（毎回この実測で判断する・推測しない）。
  python tools/ogp_probe.py [URL]
見るもの＝Twitterbot UAでの取得可否／転送量／所要時間／og:image がHTMLの何バイト目か／
og-image.png 単体の応答。memory: feedback_x_no_link_spam（原因の本命＝トップが重い）
"""
import gzip
import io
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

URL = sys.argv[1] if len(sys.argv) > 1 else "https://oshinavi.jp/"
UA = "Twitterbot/1.0"


def get(url, ua=UA, accept_gzip=True):
    h = {"User-Agent": ua}
    if accept_gzip:
        h["Accept-Encoding"] = "gzip"
    t0 = time.time()
    r = urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120)
    raw = r.read()
    dt = time.time() - t0
    body = raw
    if r.headers.get("Content-Encoding") == "gzip":
        body = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    return r, raw, body, dt


print("=== %s （UA=%s）===" % (URL, UA))
try:
    r, raw, body, dt = get(URL)
except Exception as e:
    print("❌取得できない: %s" % e)
    raise SystemExit(1)

print("  HTTP %s / 転送 %.2fMB（展開後 %.2fMB）/ %.1f秒" %
      (r.status, len(raw) / 1048576, len(body) / 1048576, dt))

text = body.decode("utf-8", "replace")
for tag in ("og:image", "og:url", "og:title", "twitter:card"):
    m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]*>' % tag, text)
    if m:
        print("  %-13s %d バイト目 | %s" % (tag, m.start(), re.sub(r"\s+", " ", m.group(0))[:110]))
    else:
        print("  %-13s 🚨見つからない" % tag)

m = re.search(r'<meta[^>]+og:image["\'][^>]*content=["\']([^"\']+)', text)
if m:
    img = m.group(1)
    print("\n=== og:image 単体 ===\n  %s" % img)
    try:
        ri, rawi, _, dti = get(img, accept_gzip=False)
        print("  HTTP %s / %s / %dKB / %.1f秒" %
              (ri.status, ri.headers.get("Content-Type"), len(rawi) / 1024, dti))
    except Exception as e:
        print("  ❌取得できない: %s" % e)

print("\n※Xのクローラーは重いページを最後まで読み切らないことがある。"
      "転送量と秒数が判断材料（memory: feedback_x_no_link_spam）")
