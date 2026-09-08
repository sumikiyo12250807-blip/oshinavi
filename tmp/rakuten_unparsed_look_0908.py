# -*- coding: utf-8 -*-
"""解析不能7件が「買える枠が無い」のか「読めなかっただけ」なのかを見る。

🚨「読めなかった」を黙って落とさない（[[project_rakuten_make_it_ironclad]]）。
   公演日が未来なら**取りこぼし**＝明日ユーザーに目視してもらう候補にする。
"""
import io, re, sys

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")
import rakuten_harvest as R

rows = []
for u in io.open("tmp/rakuten_unparsed.txt", encoding="utf-8").read().split():
    try:
        b = R.fetch(u)
    except Exception as ex:
        rows.append((u, "取得できない(%s)" % type(ex).__name__, "", ""))
        continue
    t = re.search(r"<title[^>]*>(.*?)</title>", b, re.S)
    name = R.strip_tags(t.group(1))[:52] if t else "(題名が取れない)"
    kind = ("mini形式" if "/mini/events/" in u else
            ("新型JSONあり" if "data-event-json" in b else "3種類目のレイアウト"))
    # 本文にある未来の日付を拾う（買える枠かどうかまでは決めない）
    ds = sorted({d for d in re.findall(r"20\d{2}[/-]\d{1,2}[/-]\d{1,2}", b)})
    fut = [d for d in ds if d.replace("/", "-") >= "2026-09-08"]
    rows.append((u, kind, name, "未来の日付 %d個 %s" % (len(fut), fut[:3])))

print("=== 解析不能7件の正体 ===\n")
for u, kind, name, note in rows:
    print("[%s] %s" % (kind, name))
    print("   %s" % u)
    print("   %s\n" % note)
