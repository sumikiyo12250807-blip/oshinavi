#!/usr/bin/env python3
"""X投稿の準備で調べたフォロワー数の表（tmp/x*/x/followers_*.md）から「エントリid → フォロワー数」を集めて
tools/artist_popularity.json に足す（build_artist_pages.py が「人気の組から」並べるのに使う）。

表の形は日によって違う（id が名前の列に入る日・別の列の日／「1,474,298」「173.7万」「★3.2M」）ので、
行の中の id(\\d+) をぜんぶ拾い、数だけのセルのうち最初のものをフォロワー数とみなす。
同じ id が何度も出たら大きい方を残す。

使い方: python tools/collect_followers.py
"""
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tools", "artist_popularity.json")
NUM = re.compile(r"([\d,]+(?:\.\d+)?)\s*(万|M|K)?")


def to_int(cell):
    c = cell.replace("★", "").replace("約", "").strip()
    m = NUM.fullmatch(c)
    if not m:
        return None
    v = float(m.group(1).replace(",", ""))
    v *= {"万": 10000, "M": 1000000, "K": 1000}.get(m.group(2), 1)
    return int(v)


def main():
    try:
        pop = {int(k): v for k, v in json.load(open(OUT, encoding="utf-8")).items()}
    except FileNotFoundError:
        pop = {}
    n_rows = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "tmp", "x*", "x", "followers_*.md"))):
        for line in open(p, encoding="utf-8"):
            if not line.startswith("|") or "---" in line:
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            ids = [int(x) for x in re.findall(r"id(\d+)", line)]
            if not ids:
                continue
            fol = next((v for v in (to_int(c) for c in cells[2:]) if v is not None and v >= 100), None)
            if fol is None:
                continue
            n_rows += 1
            for i in ids:
                pop[i] = max(pop.get(i, 0), fol)
    json.dump({str(k): v for k, v in sorted(pop.items())}, open(OUT, "w", encoding="utf-8"), indent=0)
    print(f"rows {n_rows} / ids {len(pop)} -> {OUT}")


if __name__ == "__main__":
    main()
