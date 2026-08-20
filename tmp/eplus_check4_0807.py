# -*- coding: utf-8 -*-
"""925 忘れらんねえよ(大阪8/11)の正しい公演ページを興行トップから特定＋
3065 栄ミナミ音楽祭パートナーズライブ の先の公演を一覧する（2026-08-07）。"""
import html
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def get(url):
    return urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60
    ).read().decode("utf-8", "replace")


def clean(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def blocks(h):
    out = []
    for p in re.split(r'<header class="block-ticket__header"', h)[1:]:
        seg = p[:6000]
        head = clean(seg.split("</header>")[0])
        sts = [x.strip() for x in re.findall(r"ticket-status__item[^>]*>([^<]{1,30})<", seg)]
        out.append((head[:140], " / ".join(dict.fromkeys(sts)) or "(取れず)"))
    return out


print("########## 925 忘れらんねえよ 興行トップ ##########")
h = get("https://eplus.jp/sf/detail/0753900001")
m = re.search(r"<title>(.*?)</title>", h, re.S)
print("title: " + (clean(m.group(1))[:110] if m else "?"))
print("--- 公演日option ---")
for o in re.findall(r"<option[^>]*>(.*?)</option>", h, re.S):
    t = clean(o)
    if t and re.search(r"\d{4}/\d", t):
        print("  " + t)

print("\n--- 各公演リンク（koen_detail_url_pc）---")
seen = set()
for mm in re.finditer(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h):
    s = max(0, mm.start() - 3000)
    blk = h[s:mm.end() + 3000]

    def g(k):
        x = re.search(r'"%s":"([^"]*)"' % k, blk)
        return x.group(1) if x else ""
    u = mm.group(1)
    if u in seen:
        continue
    seen.add(u)
    print("  %s %s %s | %s" % (g("koenbi")[:8], g("kaijo_name")[:24], g("todofuken_name")[:5],
                               "https://eplus.jp" + u))

time.sleep(5)
print("\n########## 3065 栄ミナミ音楽祭パートナーズライブ ##########")
h2 = get("https://eplus.jp/sf/detail/3658480001")
m = re.search(r"<title>(.*?)</title>", h2, re.S)
print("title: " + (clean(m.group(1))[:110] if m else "?"))
for o in re.findall(r"<option[^>]*>(.*?)</option>", h2, re.S):
    t = clean(o)
    if t and re.search(r"\d{4}/\d", t):
        print("  " + t)
