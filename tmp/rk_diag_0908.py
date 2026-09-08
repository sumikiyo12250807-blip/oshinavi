# -*- coding: utf-8 -*-
"""楽天ハーベストで「解析不能」になったページの中身を調べる。
   🚨「買える枠が無い」と「読めなかった」は別物。読めなかっただけなら取りこぼしている。
   何が無いのかを部品ごとに数えて、直すべき場所を特定する。"""
import io, re, sys, time, urllib.request

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
urls = [u.strip() for u in io.open("tmp/rakuten_unparsed_0908.txt", encoding="utf-8") if u.strip()]

o = io.open("tmp/rk_diag_0908.md", "w", encoding="utf-8")
o.write("# 楽天「解析不能」36件の中身\n\n")
o.write("| # | URL末尾 | HTML長 | og:title | 公演カード | active | salesDisplayStatus | 販売期間の文字 | 形 |\n")
o.write("|---|---|---|---|---|---|---|---|---|\n")

import collections
shapes = collections.Counter()
for i, u in enumerate(urls, 1):
    try:
        h = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode("utf-8", "replace")
    except Exception as ex:
        o.write("| %d | %s | 取得失敗 | | | | | | %s |\n" % (i, u.rstrip("/").split("/")[-1], str(ex)[:24]))
        shapes["取得失敗"] += 1
        time.sleep(1)
        continue

    og = re.search(r'property="og:title" content="([^"]{0,60})', h)
    cards = len(re.findall(r"class='performance[^']*'", h)) + len(re.findall(r'class="performance[^"]*"', h))
    active = len(re.findall(r"performance[^'\"]*active", h))
    sds = "あり" if re.search(r"var\s+salesDisplayStatus\s*=\s*\{", h) else \
          ("false" if re.search(r"var\s+salesDisplayStatus\s*=\s*false", h) else "無し")
    baikyaku = "あり" if "販売期間" in h else "無し"

    if "/mini/" in u or "mini" in h[:3000]:
        shape = "mini形式(別レイアウト)"
    elif cards == 0 and sds == "無し":
        shape = "公演カードもJSも無い"
    elif cards > 0 and active == 0:
        shape = "カードはあるが全部終了"
    elif cards == 0 and sds != "無し":
        shape = "JSはあるがカード無し"
    else:
        shape = "その他"
    shapes[shape] += 1

    o.write("| %d | %s | %d | %s | %d | %d | %s | %s | %s |\n"
            % (i, u.rstrip("/").split("/")[-1], len(h),
               (og.group(1) if og else "(無し)")[:22], cards, active, sds, baikyaku, shape))
    time.sleep(1)

o.write("\n## 形の内訳\n\n")
for k, v in shapes.most_common():
    o.write("- %s … %d件\n" % (k, v))
o.close()
print("wrote tmp/rk_diag_0908.md  %s" % dict(shapes))
