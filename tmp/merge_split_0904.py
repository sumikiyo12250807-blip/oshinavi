# -*- coding: utf-8 -*-
"""build_pia_entries の出力（tmp/split_merge_built_0904.json）を、
既存エントリへ「枠を足す」形で統合する。

🚨足す枠には ticket.url が必ず付いていること。1つでも欠けたら中止する
   （url無しで足すと二重登録の温床になる＝今朝それを片づけたばかり）。
🚨既存に同じ枠（券種名の日付部分を落として＋受付終了日が一致）があれば足さない。

  python tmp/merge_samename_0904.py          # 下見
  python tmp/merge_samename_0904.py --apply  # 実行
"""
import json, re, io, sys, shutil

PATH = "index.html"
BUILT = "tmp/split_merge_built_0904.json"
CAND = "tmp/split_merge_cand_0904.json"
APPLY = "--apply" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
src_text = m.group(1)
events = json.loads(src_text)


def dump(evs):
    return json.dumps(evs, ensure_ascii=False, indent=2)


if dump(events) != src_text.replace("\r\n", "\n"):
    print("ABORT: 書式の往復チェックに落ちた")
    sys.exit(1)

by_id = {e.get("id"): e for e in events}
cand = {c["newid"]: c for c in json.load(io.open(CAND, encoding="utf-8"))}
built = json.load(io.open(BUILT, encoding="utf-8"))


def key(t):
    ty = re.sub(r"\d{1,2}/\d{1,2}", "#", t.get("type", ""))
    ty = re.sub(r"\d{1,2}:\d{2}", "#", ty)
    return (ty, t.get("date"))


added, skipped, report = 0, 0, []
for b in built:
    c = cand.get(b.get("id"))
    if not c:
        print("ABORT: build結果 id=%s に対応する候補が無い" % b.get("id"))
        sys.exit(1)
    target = by_id.get(c["_merge_into"])
    if not target:
        print("ABORT: 統合先 id=%s が見つからない" % c["_merge_into"])
        sys.exit(1)
    oldkeys = set(key(t) for t in target.get("tickets", []))
    # build は1URLで呼ぶと ticket.url を付けない（multi=False）。統合先には他の会場の枠が
    # 並ぶので、飛び先が分かるよう候補の個別ページURLを必ず付ける（[[feedback_tour_per_ticket_url]]）
    src_url = (c.get("urls") or [None])[0]
    if not src_url:
        print("ABORT: 候補にURLが無い（build=%s）" % b.get("id"))
        sys.exit(1)
    for t in b.get("tickets", []):
        if key(t) in oldkeys:
            skipped += 1
            continue
        t = dict(t)
        t.setdefault("url", src_url)
        target.setdefault("tickets", []).append(dict(t))
        oldkeys.add(key(t))
        added += 1
        report.append((c["_merge_into"], target.get("name"), t.get("type"), t.get("date")))

print("ADDED=%d  SKIPPED(既にある)=%d  対象エントリ=%d" % (
    added, skipped, len(set(c["_merge_into"] for c in cand.values()))))
buf = ["統合ログ 2026-09-04（同名既存＝ツアー分裂の回収）", ""]
for eid, name, ty, dt in report:
    buf.append("- id%s %s ← %s（〜%s）" % (eid, name, ty, dt))
io.open("tmp/merge_split_0904.txt", "w", encoding="utf-8").write("\n".join(buf))

if not APPLY:
    print("(下見のみ。--apply で書き込み)")
    sys.exit(0)

shutil.copy(PATH, PATH + ".bak_0904_samename")
out = raw[:m.start(1)] + dump(events).replace("\n", "\r\n") + raw[m.end(1):]
io.open(PATH, "w", encoding="utf-8", newline="").write(out)
print("WROTE index.html (backup: index.html.bak_0904_split)")
