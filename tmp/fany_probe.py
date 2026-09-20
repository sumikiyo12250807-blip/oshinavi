# -*- coding: utf-8 -*-
"""FANYチケット（ticket.fany.lol）の在庫の全体像を測る。
入口: /search/event?from=&to=&genre=  … 1ページ目はHTMLに入っている（カードあり）
      /search/event_more?<同じクエリ>&offset=N  … JSONで10件ずつ（これで全部取れる）
総件数はページ内 loadMore() の「newOffset >= N」の N（＝そのクエリの総数）。
"""
import re, json, time, io, sys
import urllib.request, urllib.parse

BASE = "https://ticket.fany.lol"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

GENRES = {
    "30": "お笑い", "31": "音楽", "32": "演劇/ステージ", "33": "スポーツ",
    "34": "アニメ", "35": "ゲーム", "36": "映画/LV", "37": "アート/イベント",
    "38": "劇場以外",
}


def get(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                return "ERR:%s" % e
            time.sleep(2)


def total_of(qs):
    html = get(BASE + "/search/event?" + qs)
    if html.startswith("ERR:"):
        return -1, html
    m = re.search(r"newOffset\s*>=\s*(\d+)", html)
    n = int(m.group(1)) if m else 0
    return n, html


def main():
    frm, to = sys.argv[1], sys.argv[2]
    out = io.open("tmp/fany_probe.txt", "w", encoding="utf-8")
    out.write("FANY 在庫しらべ  %s 〜 %s\n\n" % (frm, to))
    grand = 0
    for g, label in sorted(GENRES.items()):
        qs = urllib.parse.urlencode({"from": frm, "to": to, "genre": g})
        n, _ = total_of(qs)
        grand += max(n, 0)
        out.write("genre=%s %-12s %6d件\n" % (g, label, n))
        out.flush()
        time.sleep(1)
    qs = urllib.parse.urlencode({"from": frm, "to": to})
    n_all, _ = total_of(qs)
    out.write("\nジャンル指定なし        %6d件\n" % n_all)
    out.write("ジャンル合計            %6d件\n" % grand)
    out.close()
    print("wrote tmp/fany_probe.txt  all=%d genresum=%d" % (n_all, grand))


if __name__ == "__main__":
    main()
