# -*- coding: utf-8 -*-
"""統合の再ビルド結果を、既存エントリへ「追加と補完だけ」で当てる。

🚨 置換しない（feedback_build_pia_multiurl_loses_ticket_url の2026-08-27項＝
   再ビルドで tickets を丸ごと置き換えたら劇団四季の「ぴあシート」6枠が消えた）。
   やるのは3つだけ：
     ① links.pia を「実際に買える枠が取れたページ」に寄せる（ビルド側が決めた値を採用）
     ② url が空の既存枠に、ビルド側の url を補完する
     ③ 再ビルドにしか無い枠を足す
   ＋ 公演日(date)・dateLabel・venue・prefecture は、枠が増えたぶん範囲が広がるので更新する。

使い方:
  python tmp/merge_apply_0905.py tmp/merge_built_0905.json          # 差分を見るだけ
  python tmp/merge_apply_0905.py tmp/merge_built_0905.json --apply
"""
import json, re, io, sys, datetime

PATH = "index.html"
OUT = "tmp/merge_apply_0905.txt"
built = {e["id"]: e for e in json.load(open(sys.argv[1], encoding="utf-8"))}

h = open(PATH, encoding="utf-8").read()
m = re.search(r"(const EVENTS = )(\[.*?\])(;\n)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}


def base_type(ty):
    ty = re.sub(r"〜\s*\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*$", "", ty or "")
    ty = re.sub(r"\d{1,2}/\d{1,2}(?:\s*\d{1,2}:\d{2})?\s*発売\s*$", "", ty)
    return ty.strip()


buf, added_total, filled_total = [], 0, 0
touched = []
for i, b in sorted(built.items()):
    e = by.get(i)
    if not e:
        buf.append("SKIP id=%s（現物に無い）" % i)
        continue
    before = len(e.get("tickets") or [])
    idx = {}
    for t in e.get("tickets") or []:
        idx.setdefault(base_type(t.get("type")), []).append(t)
    add, fill = [], 0
    for nt in b.get("tickets") or []:
        k = base_type(nt.get("type"))
        if k in idx:
            # ② url の補完だけ（既存の値は上書きしない）
            for t in idx[k]:
                if not (t.get("url") or "") and (nt.get("url") or ""):
                    t["url"] = nt["url"]
                    fill += 1
        else:
            add.append(nt)          # ③ 再ビルドにしか無い枠
    buf.append("id=%-5s %s | 既存%d枠 → +%d枠 / url補完%d"
               % (i, e.get("name", "")[:36], before, len(add), fill))
    for nt in add:
        buf.append("      + %s | %s" % (nt.get("type"), nt.get("url") or "(url無し)"))
    added_total += len(add)
    filled_total += fill
    touched.append((i, before, len(add), fill, b, e, add))

buf.append("")
buf.append("合計: +%d枠 / url補完 %d枠 / 対象 %d件" % (added_total, filled_total, len(touched)))
io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("MERGE +%d slots / fill %d / entries %d -> %s" % (added_total, filled_total, len(touched), OUT))

if "--apply" not in sys.argv:
    sys.exit(0)

TODAY = datetime.date.today().isoformat()
for i, before, nadd, fill, b, e, add in touched:
    e["tickets"] = (e.get("tickets") or []) + add
    # ① links.pia は「買える枠が取れたページ」をビルド側が選んでいるので採用
    if (b.get("links") or {}).get("pia"):
        e.setdefault("links", {})["pia"] = b["links"]["pia"]
    for f in ("date", "dateLabel", "venue", "prefecture"):
        if b.get(f):
            e[f] = b[f]
    e["verifiedAt"] = TODAY

bak = "index.html.bak_%s_merge" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
open(PATH, "w", encoding="utf-8").write(
    h[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print("APPLIED entries=%d backup=%s" % (len(touched), bak))
