# -*- coding: utf-8 -*-
"""e+ビルドの artist 欄が公演名の頭で切れているものを直す。

🚨 artist は次回ハーベストの「同名でDBにある」判定に使われる。「THE」「Planet」のような
一般語が入ると、次から「THE ◯◯」系が全部同名扱いになって取りこぼす
（[[feedback_harvest_name_dedup_blindspot]]と同じ型の目つぶし）。
値は**すべて name に書いてある文字**から取る（外から補わない＝裏取り不要）。
"""
import json, io

SRC = "tmp/eplus_built_pre18_0905.json"
FIX = {
    6937: "おとぎ話",              # name: THE SUN ALSO RISES vol.423 … おとぎ話 / SCOOBIE DO
    6938: "Planet CHILD Music",   # name: Planet CHILD Music presents 『四季彩プラネタリウム』
    6939: "MEME",                 # name: MEME× tzkwym 「血湧き肉躍る-ハロウィン-」
    6940: "楓",                   # name: 記念単独公演 楓生誕祭2026
}

a = json.load(io.open(SRC, encoding="utf-8"))
buf = []
for e in a:
    if e["id"] in FIX:
        buf.append("id=%s  %s → %s   （name=%s）" % (e["id"], e.get("artist"), FIX[e["id"]], e.get("name")))
        e["artist"] = FIX[e["id"]]
json.dump(a, io.open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open("tmp/fix_artist_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("FIXED=%d" % len(buf))
