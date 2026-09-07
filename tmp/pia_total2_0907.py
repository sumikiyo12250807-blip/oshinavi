# -*- coding: utf-8 -*-
"""ぴあの各ジャンルの総件数（1ページ目の「全N件中」だけ読む）。
前のスクリプトは出力の組み立てで詰まったので、素直に1行ずつ書き出す形にした。
"""
import re, time, io, urllib.request

LGS = [("01", "音楽"), ("02", "演劇"), ("03", "スポーツ"), ("04", "映画"),
       ("05", "アート"), ("06", "イベント"), ("07", "クラシック")]
FILTERS = [("rlsStatus=0101", "発売中"), ("rlsStatus=0201", "受付中(抽選)")]
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

out = io.open("tmp/pia_total2_0907.txt", "w", encoding="utf-8")
out.write("=== ぴあの在庫（1ページ目の「全N件中」・2026-09-07 夜）===\n\n")
grand = 0
for lg, jname in LGS:
    for filt, fname in FILTERS:
        url = "https://t.pia.jp/pia/rlsInfo.do?lg=%s&%s&page=1" % (lg, filt)
        try:
            h = urllib.request.urlopen(urllib.request.Request(url, headers=HDR),
                                       timeout=30).read().decode("utf-8", "replace")
            if "sorry.pia.jp" in h:
                out.write("%-10s %-12s 混雑ページ\n" % (jname, fname))
            else:
                m = re.search(r"全([0-9,]+)件中", h)
                n = int(m.group(1).replace(",", "")) if m else 0
                grand += n
                out.write("%-10s %-12s %6d件\n" % (jname, fname, n))
        except Exception as ex:
            out.write("%-10s %-12s 取得できず（%s）\n" % (jname, fname, str(ex)[:40]))
        out.flush()
        time.sleep(5)
out.write("\n合計 %d件\n" % grand)
out.close()
print("done grand=%d" % grand)
