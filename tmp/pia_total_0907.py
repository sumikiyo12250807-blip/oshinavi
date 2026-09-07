# -*- coding: utf-8 -*-
"""「ぴあ制覇はいつか」に数字で答えるための計測。

ぴあの各ジャンルの**総件数**（1ページ目のヘッダの「全N件中」）だけを読む。
全ページは取らない＝7ジャンル×2フィルタ＝14リクエストで済む（叩きすぎない）。

  rlsStatus=0101 … 発売中（先着で今買える）
  rlsStatus=0201 … 受付中（抽選で今受け付けている）
"""
import re, time, io, urllib.request, http.client

LGS = [("01", "音楽"), ("02", "演劇"), ("03", "スポーツ"), ("04", "映画"),
       ("05", "アート"), ("06", "イベント"), ("07", "クラシック")]
FILTERS = [("rlsStatus=0101", "発売中"), ("rlsStatus=0201", "受付中(抽選)")]

HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                     "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def total_of(lg, filt):
    url = "https://t.pia.jp/pia/rlsInfo.do?lg=%s&%s&page=1" % (lg, filt)
    req = urllib.request.Request(url, headers=HDR)
    try:
        h = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as ex:
        return -1, str(ex)[:60]
    if "sorry.pia.jp" in h:
        return -2, "混雑ページ"
    m = re.search(r"全([0-9,]+)件中", h)
    return (int(m.group(1).replace(",", "")) if m else 0), ""


rows = []
for lg, name in LGS:
    for filt, fname in FILTERS:
        n, err = total_of(lg, filt)
        rows.append((name, fname, n, err))
        time.sleep(5)

with io.open("tmp/pia_total_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== ぴあの在庫（各ジャンルの総件数・2026-09-07 夜）===\n")
    f.write("ジャンル      発売中     受付中(抽選)\n")
    tot = 0
    for _lg, name in LGS:   # 🚨 (lg, name) を (name, _) で受けていて全部 None になった
        a = [r for r in rows if r[0] == name]
        v = {r[1]: r[2] for r in a}
        e = {r[1]: r[3] for r in a}
        f.write("%-10s  %7s   %7s   %s\n"
                % (name, v.get("発売中"), v.get("受付中(抽選)"),
                   " ".join(x for x in e.values() if x)))
        for x in v.values():
            if x and x > 0:
                tot += x
    f.write("\n合計 %d件\n" % tot)
print("wrote tmp/pia_total_0907.txt")
