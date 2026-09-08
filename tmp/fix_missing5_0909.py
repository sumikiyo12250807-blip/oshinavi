# -*- coding: utf-8 -*-
"""統合後の再照合で MISSING が出た5件を直す。
中身は「新しい枠」ではなく **同じ枠の締切が延びた／ぴあが発売前に作り直した** 型。
merge_apply は足すことしかしないので、ここだけ**既存の枠を再ビルドの値に更新**する。

  id674  椎名慶治      滋賀・奈良 9/12〜9/13 … 〜9/10 → 〜9/12 23:59（締切が延びた）
  id3148 Chage        大阪 9/22        … 〜9/6  → 〜9/21 23:59（同上）
  id3922 大阪桐蔭      奈良 10/10       … 〜10/9 → 9/12 10:00発売（ぴあが発売前に作り直した）
  id4926 プリキュア     大阪 9/12        … 〜8/27 → 〜9/9 23:59（同上）
  id6452 真夜中の音楽室  poco会員限定先行  … 9/8発売 → 〜9/9 23:59（発売後に締切が入った）

🚨消さない・減らさない＝再ビルドに無い枠（過去の枠）はそのまま残す。
使い方: python tmp/fix_missing5_0909.py [--apply]
"""
import json, io, re, sys

sys.stdout.reconfigure(encoding="utf-8")
IDS = [674, 3148, 3922, 4926, 6452]

built = {b["id"]: b for b in json.load(io.open("tmp/merge_built_0909.json", encoding="utf-8"))}
h = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}


def head(ty):
    """券種名＋（…公演）まで＝同じ売り場を指す骨格。末尾の締切/発売日だけが動く。"""
    mm = re.match(r"^(.*?[）)])", ty or "")
    return mm.group(1) if mm else (ty or "")


changed, added = [], []
for i in IDS:
    e, b = by[i], built[i]
    idx = {}
    for t in e.get("tickets") or []:
        idx.setdefault(head(t.get("type")), []).append(t)
    for bt in b.get("tickets") or []:
        k = head(bt.get("type"))
        hit = idx.get(k)
        if not hit:
            e.setdefault("tickets", []).append(dict(bt))
            added.append((i, bt.get("type")))
            continue
        t = hit[0]
        if t.get("type") != bt.get("type") or t.get("date") != bt.get("date"):
            changed.append((i, t.get("type"), t.get("date"), bt.get("type"), bt.get("date")))
            t["type"] = bt["type"]
            t["date"] = bt["date"]
            if bt.get("startDate"):
                t["startDate"] = bt["startDate"]
            else:
                t.pop("startDate", None)
            if bt.get("url"):
                t["url"] = bt["url"]

print("更新 %d枠 / 追加 %d枠" % (len(changed), len(added)))
for i, ot, od, nt, nd in changed:
    print("  id%-6d %s (%s)\n          → %s (%s)" % (i, ot, od, nt, nd))
for i, t in added:
    print("  id%-6d ＋%s" % (i, t))
if "--apply" not in sys.argv:
    print("(--apply で書き込み)")
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace("\n", "\r\n") + h[m.end(2):]
io.open("index.html", "w", encoding="utf-8", newline="").write(out)
print("書き込み完了")
