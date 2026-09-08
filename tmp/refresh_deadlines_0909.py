# -*- coding: utf-8 -*-
"""再ビルドの結果で、**既存の枠の締切/発売日だけを更新する**（足すのではなく上書き）。

なぜ要るか＝`tmp/merge_apply_0905.py` は「追加と補完だけ」で既存の枠を触らない。
だから **同じ枠の締切がぴあ側で延びた/再開した** 時に直せず、
reconcile が「ぴあに [受付中] があるのに登録に無い」（MISSING）と鳴り続ける。
2026-09-09 に2回踏んだ（朝＝椎名慶治ほか5件／昼＝New Acoustic Camp 9件）。

判定＝券種名＋（…公演）まで＝**同じ売り場を指す骨格**が一致する枠を、再ビルドの値に揃える。
🚨消さない・減らさない＝再ビルドに無い枠（過去の枠）はそのまま残す。
使い方: python tmp/refresh_deadlines_0909.py <built.json> [--apply]
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")
SRC = sys.argv[1]
built = {b["id"]: b for b in json.load(io.open(SRC, encoding="utf-8"))}

h = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}


def head(ty):
    """券種名＋（<県> <日付>公演）まで＝同じ売り場を指す骨格。末尾の締切/発売日だけが動く。
    🚨最初の「）」で切ってはいけない＝券種名の中に「（1台）」「（9/19-20）」が入る
      （New Acoustic Camp の駐車券・宿泊券）。別の券種が同じ骨格に潰れて**中身を取り違える**。
      2026-09-09 に作った直後に踏んだので、必ず「（…公演）」まで取る。"""
    mm = re.match(r"^(.*?（[^（）]*公演）)", ty or "")
    if mm:
        return mm.group(1)
    return ty or ""


changed, added, ambiguous = [], [], []
for i, b in built.items():
    e = by.get(i)
    if not e:
        continue
    idx = {}
    for t in e.get("tickets") or []:
        idx.setdefault(head(t.get("type")), []).append(t)
    bcnt = {}
    for bt in b.get("tickets") or []:
        bcnt[head(bt.get("type"))] = bcnt.get(head(bt.get("type")), 0) + 1
    for bt in b.get("tickets") or []:
        k = head(bt.get("type"))
        hit = idx.get(k)
        if not hit:
            e.setdefault("tickets", []).append(dict(bt))
            added.append((i, bt.get("type")))
            continue
        if len(hit) > 1 or bcnt[k] > 1:
            # 骨格が同じ枠が複数＝どれとどれの対か機械では決まらない。触らない
            ambiguous.append((i, k))
            continue
        t = hit[0]
        if t.get("type") != bt.get("type") or t.get("date") != bt.get("date"):
            changed.append((i, t.get("type"), t.get("date"), bt.get("type"), bt.get("date")))
            t["type"], t["date"] = bt["type"], bt["date"]
            if bt.get("startDate"):
                t["startDate"] = bt["startDate"]
            else:
                t.pop("startDate", None)
            if bt.get("url"):
                t["url"] = bt["url"]

print("更新 %d枠 / 追加 %d枠 / 対を決められず触らなかった %d枠" % (len(changed), len(added), len(ambiguous)))
for i, k in dict.fromkeys(ambiguous):
    print("  ⚠️id%-6d 骨格が同じ枠が複数: %s" % (i, k[:60]))
for i, ot, od, nt, nd in changed:
    print("  id%-6d %s (%s)\n          → %s (%s)" % (i, ot[:60], od, nt[:60], nd))
for i, t in added:
    print("  id%-6d ＋%s" % (i, t[:70]))
if "--apply" not in sys.argv:
    print("(--apply で書き込み)")
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace("\n", "\r\n") + h[m.end(2):]
io.open("index.html", "w", encoding="utf-8", newline="").write(out)
print("書き込み完了")
