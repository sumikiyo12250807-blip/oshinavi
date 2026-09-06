# -*- coding: utf-8 -*-
"""e+新着のうち下書きジャンル(_genre)が無いものについて、
e+ の「チケットの関連ジャンル」を実ページから機械で写し取る。

🚨 ジャンルは自分で決めずに「売り場の言う通り」に写すのが原則
   （[[feedback_genre_pia_asis_and_other]]＝ぴあのやり方をe+にも当てる）。

パンくずは <!-- breadcrumbs --> ブロックが複数あり、そのうち
「チケットの関連ジャンル」を含むブロックが欲しいもの。生HTMLの中では
タグで分断されているので、ブロックごとにタグを剥いでから探す。
"""
import html as H
import json
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

src = open("index.html", encoding="utf-8").read()
EVENTS = json.loads(re.search(r"(  const EVENTS = )(\[.*?\])(;)", src, re.S).group(2))


def is_eplus(e):
    return "eplus.jp" in json.dumps(e, ensure_ascii=False)


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", H.unescape(s))).strip()


pool = sorted([e for e in EVENTS
               if e.get("genre") == "new" and is_eplus(e) and not e.get("_genre")],
              key=lambda e: e["id"])

out = open("tmp/eplus_genre_src_0906.txt", "w", encoding="utf-8")
for e in pool:
    url = (e.get("links") or {}).get("eplus")
    genre = ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        page = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
        for blk in re.findall(r"breadcrumb.{0,3000}?</(?:ol|ul|nav)>", page, re.S):
            t = plain(blk)
            if "関連ジャンル" in t:
                genre = t.split("関連ジャンル", 1)[1].strip(' >')
                break
        if not genre:
            # 予備＝パンくずの2段目（TOP > ライブ･コンサート > …）
            for blk in re.findall(r"breadcrumb.{0,3000}?</(?:ol|ul|nav)>", page, re.S):
                t = plain(blk)
                if t.startswith("TOP") or " TOP " in t:
                    genre = "[パンくず] " + t
                    break
    except Exception as ex:
        genre = "FETCH_ERROR:%s" % ex
    line = "id=%-5d %-36s | %s" % (e["id"], (e.get("artist") or "")[:34], genre[:150])
    out.write(line + "\n")
    out.flush()
    print(line)
    time.sleep(2)
out.close()
print("\n対象 %d件" % len(pool))
