# -*- coding: utf-8 -*-
"""バッジ0（買える枠0）のエントリが「どの型で死んでいるか」を集計する。通信なし。
仮説＝先行/プレリザーブだけ登録して一般発売を取り込めていない型が多いのでは。"""
import json
import re
import sys
import io
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

IDS = [int(x) for x in sys.argv[1].split(",")]

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = json.loads(m.group(1))
by_id = {e["id"]: e for e in events}

SENKO = ("先行", "プレリザーブ", "プリセール", "先着先行", "最速", "オフィシャル", "抽選")


def kind(t):
    ty = t.get("type") or ""
    if any(s in ty for s in SENKO):
        return "先行のみ"
    if "一般" in ty:
        return "一般発売あり"
    return "その他"


rows = []
for i in IDS:
    e = by_id.get(i)
    if e is None:
        continue
    kinds = set(kind(t) for t in (e.get("tickets") or []))
    if "一般発売あり" in kinds:
        cat = "一般も登録済（それも終了）"
    elif kinds == {"先行のみ"}:
        cat = "🚨先行/抽選だけ登録（一般を取り込めていない）"
    else:
        cat = "その他/判定不能"
    rows.append((cat, i, e))

print("=== 型の内訳（%d件）===" % len(rows))
for k, v in Counter(r[0] for r in rows).most_common():
    print("  %-40s %d" % (k, v))

for cat in sorted(set(r[0] for r in rows)):
    print("\n=== %s ===" % cat)
    for _, i, e in [r for r in rows if r[0] == cat]:
        tys = " / ".join((t.get("type") or "")[:38] for t in (e.get("tickets") or []))
        print("  id=%-5d 公演%s %-28s %s" % (i, e.get("date"), (e.get("artist") or "")[:28], tys))
