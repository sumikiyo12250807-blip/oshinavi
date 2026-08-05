# -*- coding: utf-8 -*-
"""ぴあで受付終了だった怪談9件を、e+で拾えないか探す（2026-08-05）。

🚨 e+の検索一覧に出る「先着一般発売」は【券種名】であって販売中ではない。
   必ず /sf/detail/ の個別ページまで開いてステータスを読む（[[feedback_delete_nonpia_blindspot]]）。
ここでは①検索でdetail URLを集め ②名前が合うものだけ個別ページを開いて実ステータスを出す。
"""
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"
UA = {"User-Agent": "Mozilla/5.0"}

# (検索語, 名前照合に使う語)
TARGETS = [
    ("怪談の語り場", ["怪読劇", "語り場"]),
    ("オカルト超会議", ["オカルト超会議", "PSYCHIC"]),
    ("好井まさお", ["好井"]),
    ("北海道オカルトトークライブ", ["北こわ", "オカルトトークライブ"]),
    ("Tokyo Kaidan Collection", ["Kaidan", "カイダン"]),
    ("島田秀平", ["島田秀平"]),
    ("三木大雲", ["三木大雲"]),
    ("牛抱せん夏", ["牛抱"]),
]


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "replace")


def norm(s):
    return unicodedata.normalize("NFKC", s).lower()


found = {}
for kw, keys in TARGETS:
    try:
        h = get("https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw))
    except Exception as ex:
        print("検索失敗 %s: %s" % (kw, ex))
        continue
    urls = set(re.findall(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h))
    # 同じHTML内で、そのURLの近くに照合語があるものだけ拾う
    hit = []
    for u in urls:
        i = h.find('"koen_detail_url_pc":"%s"' % u)
        blk = norm(h[max(0, i - 4000): i + 4000])
        if any(norm(k) in blk for k in keys):
            hit.append(u)
    print("[%s] 検索%d件 → 名前が合う %d件" % (kw, len(urls), len(hit)))
    for u in hit:
        found.setdefault("https://eplus.jp" + u, []).append(kw)
    time.sleep(2)

print("\n=== 個別ページで実ステータスを見る（%d件）===" % len(found))
out = []
for i, (u, kws) in enumerate(sorted(found.items()), 1):
    try:
        h = get(u)
    except Exception as ex:
        print("%s 取得失敗 %s" % (u, ex))
        continue
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", (re.search(r"<title>(.*?)</title>", h, re.S) or [None, ""])[1])).strip()
    days = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m)).strip()
            for m in re.findall(r"<option[^>]*value=\"[^\"]*\"[^>]*>(.*?)</option>", h, re.S)]
    blocks = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b)).strip()
              for b in re.findall(r'<header class="block-ticket__header".*?</header>', h, re.S)]
    stats = set(re.findall(r'ticket-status__item[^>]*>([^<]{1,30})<', h))
    print("\n--- [%d] %s" % (i, u))
    print("    語: %s" % ",".join(kws))
    print("    title: %s" % title[:100])
    if days:
        print("    公演日: %s" % " / ".join(d for d in days[:6] if d))
    for b in blocks[:8]:
        print("    枠: %s" % b[:130])
    print("    状態: %s" % ", ".join(s.strip() for s in stats))
    out.append({"url": u, "words": kws, "title": title, "days": days, "blocks": blocks, "stats": sorted(stats)})
    time.sleep(2)

json.dump(out, io.open(os.path.join(ROOT, "tmp", "kaidan_eplus_hunt.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n→ tmp/kaidan_eplus_hunt.json")
