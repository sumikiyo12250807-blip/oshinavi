# -*- coding: utf-8 -*-
"""明日(2026-08-08)発売の枠を index.html から機械抽出する＝X投稿の候補出し（2026-08-07夕）。
判定軸は知名度でなく「Xでタグが回るファンダムか」（feedback_x_pick_bigname_miss）。
強いジャンルを先に出し、弱いジャンル（クラシック企画/歌謡等）は後ろにまとめる。
"""
import collections
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"C:\Users\user\oshinavi\tools")
from check_expired import extract_events_array  # noqa: E402

TARGET = "2026-08-08"
STRONG = ["jpop", "rock", "idol", "anime", "kpop", "vtuber", "youtuber", "seiyuu", "hiphop", "2.5ji"]

evs = extract_events_array(r"C:\Users\user\oshinavi\index.html")
rows = []
for e in evs:
    hit = [t for t in (e.get("tickets") or []) if t.get("startDate") == TARGET]
    if not hit:
        continue
    rows.append((e, hit))

print("=== %s 発売開始の枠を持つエントリ %d件 ===" % (TARGET, len(rows)))
c = collections.Counter(e.get("genre") for e, _ in rows)
print("ジャンル内訳: %s\n" % dict(c.most_common()))

def block(title, items):
    print("#" * 74)
    print("### %s （%d件）" % (title, len(items)))
    for e, hit in items:
        g = e.get("genre")
        ex = e.get("extraGenres") or []
        print("  id%-5d [%s%s] %s" % (e["id"], g, ("+" + "/".join(ex)) if ex else "", e.get("artist")))
        print("         %s ／ %s ／ 公演 %s" % (e.get("prefecture"), (e.get("venue") or "")[:46], e.get("date")))
        for t in hit:
            print("         枠: %s" % t.get("type"))

strong = [(e, h) for e, h in rows if e.get("genre") in STRONG]
weak = [(e, h) for e, h in rows if e.get("genre") not in STRONG]
strong.sort(key=lambda x: (STRONG.index(x[0].get("genre")), x[0]["id"]))
block("Xでタグが回りやすいジャンル", strong)
block("その他（クラシック/伝統/お笑い/スポーツ等）", weak)

# 既に調べたフォロワー数があれば見せる
p = r"C:\Users\user\oshinavi\tools\x_log.json"
if os.path.exists(p):
    try:
        log = json.load(open(p, encoding="utf-8"))
        print("\n--- tools/x_log.json のキー数: %d ---" % (len(log) if hasattr(log, "__len__") else 0))
    except Exception as ex:
        print("\nx_log.json 読めず: %s" % ex)
else:
    print("\n（tools/x_log.json は無い）")
