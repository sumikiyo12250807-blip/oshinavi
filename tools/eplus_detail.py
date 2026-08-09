#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""e+ の /sf/detail/ ページを機械パースし、公演ごと・販売枠ごとの
「券種名 / 受付期間 / ステータス」を対応づけて出す（恒久ツール）。

なぜ必要か（feedback_delete_nonpia_blindspot）:
  - 検索一覧の「一般発売」は"券種名"であって"販売中"ではない。
  - 旧 tmp/eplus_detail_0803.py は枠とステータスを set() で別々に集めていたため、
    どの枠が受付中なのか対応が取れず、削除判定に使うと危険だった。

使い方:
  python tools/eplus_detail.py <URL> [<URL> ...]
  python tools/eplus_detail.py --live-only <URL>   # 受付中の枠がある公演だけ出す
"""
import html
import re
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ALIVE = "受付中"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


def _text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def parse(page: str):
    """[{date, venue, pref, tickets:[{name, period, status}]}] を返す。"""
    shows = []
    # 公演ブロック（article）で分割。1公演に複数の block-ticket section がぶら下がる。
    parts = re.split(r'(?=<article class="block-ticket-article)', page)
    for part in parts[1:]:
        d = re.search(r'class="block-ticket-article__date">([^<]*)<', part)
        v = re.search(r'class="block-ticket-article__venue">([^<]*)<', part)
        p = re.search(r'class="block-ticket-article__region">([^<]*)<', part)
        tickets = []
        for sec in re.split(r'(?=<section class="block-ticket">)', part)[1:]:
            nm = re.search(r'class="block-ticket__title">(.*?)</h4>', sec, re.S)
            pe = re.search(r'class="block-ticket__time">([^<]*)<', sec)
            # ステータスspanは複数出る（先頭が空タグのことがある）ので全部拾って空を捨てる
            labels = [_text(x) for x in
                      re.findall(r'class="ticket-status__item[^"]*"[^>]*>([^<]*)<', sec)]
            labels = [x for x in labels if x]
            tickets.append({
                "name": _text(nm.group(1)) if nm else "",
                "period": _text(pe.group(1)) if pe else "",
                "status": " / ".join(labels) if labels else "(状態不明)",
            })
        if tickets:
            shows.append({
                "date": _text(d.group(1)) if d else "",
                "venue": _text(v.group(1)) if v else "",
                "pref": _text(p.group(1)) if p else "",
                "tickets": tickets,
            })
    return shows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    live_only = "--live-only" in sys.argv
    for i, url in enumerate(args):
        if i:
            time.sleep(3)
        print("=" * 78)
        print(url)
        try:
            shows = parse(fetch(url))
        except Exception as e:  # noqa: BLE001
            print("  [取得失敗] %s" % e)
            continue
        if not shows:
            print("  （公演ブロックが取れない＝ページ構造変更を疑う）")
            continue
        for s in shows:
            alive = [t for t in s["tickets"] if ALIVE in t["status"]]
            if live_only and not alive:
                continue
            print("  ▼%s %s%s  … 受付中の枠 %d/%d"
                  % (s["date"], s["venue"], s["pref"], len(alive), len(s["tickets"])))
            for t in s["tickets"]:
                mark = "[LIVE]" if ALIVE in t["status"] else "[   ] "
                print("    %s %s | %s | %s" % (mark, t["status"], t["name"], t["period"]))


if __name__ == "__main__":
    main()
