# -*- coding: utf-8 -*-
"""ビルド結果から id7152（中部フィル室内楽Vol.6）を外す。
ぴあの生HTMLの状態が [貸切公演] is-before ＝**一般に売らない公演**。
パーサーが「貸切公演」という表記を知らないので「発売前なのに枠が取れない」と警告していたが、
これは取りこぼしではなく掲載対象外。
🚨 build_pia_entries の parse_when/状態判定に「貸切公演」を足すのは別途（plan.md に残す）。
"""
import io, json

d = json.load(io.open("tmp/built_0907.json", encoding="utf-8"))
before = len(d)
kept = [e for e in d if e["id"] != 7152]
dropped = [e for e in d if e["id"] == 7152]

for e in dropped:
    print("外した: id=%s 枠%d %s" % (e["id"], len(e.get("tickets", [])), (e.get("name") or "")[:40]))

json.dump(kept, io.open("tmp/built_0907_final.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
n_slot = sum(len(e.get("tickets", [])) for e in kept)
print("%d件 → %d件 / 枠%d" % (before, len(kept), n_slot))
