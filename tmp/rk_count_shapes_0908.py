# -*- coding: utf-8 -*-
"""残り14件の解析不能を、レイアウトの型ごとに数える。
   何を作れば何件拾えるのかを、先に数字にしておく（作ってから数えない）。"""
import io, re, sys, time, collections, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
urls = [u.strip() for u in io.open("tmp/rakuten_unparsed.txt", encoding="utf-8") if u.strip()]

o = io.open("tmp/rk_shapes_0908.md", "w", encoding="utf-8")
o.write("# 残り %d件の解析不能を型で分ける\n\n" % len(urls))
o.write("| # | ページ | 型 | 手がかり |\n|---|---|---|---|\n")
cnt = collections.Counter()
for i, u in enumerate(urls, 1):
    tag = u.rstrip("/").split("/")[-1]
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "replace")
    except Exception as ex:
        o.write("| %d | %s | 取得失敗 | %s |\n" % (i, tag, str(ex)[:24]))
        cnt["取得失敗"] += 1
        time.sleep(1)
        continue

    has_ej = bool(re.search(r"data-event-json=", h))
    has_card = bool(re.search(r"class='performance", h))
    has_ed = bool(re.search(r"class='event-details", h))
    haishin = ("配信" in h) or ("Rakuten TV" in h)
    t = re.search(r"<title[^>]*>(.*?)</title>", h, re.S)
    title = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", t.group(1))).strip()[:26] if t else ""

    if has_ej:
        shape = "新型(data-event-json)"
        hint = "JSONを辿れば読める"
    elif has_ed and haishin:
        shape = "配信型(event-details)"
        hint = "締切が日付でないことがある"
    elif has_ed:
        shape = "event-details型"
        hint = "公演カードが無い"
    elif has_card:
        shape = "従来型だが公演が読めない"
        hint = "カードはあるが日付が取れない"
    else:
        shape = "手がかり無し"
        hint = "%d文字・空の雛形の疑い" % len(h)
    cnt[shape] += 1
    o.write("| %d | %s | %s | %s / %s |\n" % (i, tag, shape, title, hint))
    time.sleep(1)

o.write("\n## 型ごとの件数\n\n")
for k, v in cnt.most_common():
    o.write("- %s … **%d件**\n" % (k, v))
o.close()
print("%s -> tmp/rk_shapes_0908.md" % dict(cnt))
