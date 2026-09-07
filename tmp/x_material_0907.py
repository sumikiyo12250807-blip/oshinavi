# -*- coding: utf-8 -*-
"""夜のX投稿の素材を作る。Fableに渡すのはこのファイルとX_SCRIPT.mdだけ。

・明日(9/8)発売＝OSHINAVIに載っている分を**そのジャンル全部**、`時刻 名前／県` で並べる
・2〜3日後(9/9・9/10)＝**大物5件くらい**＋残りは丸めた件数（rough）
  🚨大物＝箱の大きさ（アリーナ・ドーム・大ホール等）で選ぶ。並べる順は時刻順のまま
"""
import io, re, json, collections

TOMORROW = "2026-09-08"
D2, D3 = "2026-09-09", "2026-09-10"
BIG = re.compile(r"大ホール|アリーナ|ドーム|フォーラム|Zepp|NHK|シンフォニーホール|サントリーホール|"
                 r"みなとみらいホール|オペラパレス|芸術劇場|コンサートホール|市民会館|文化会館|オペラシティ")

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))


def rough(n):
    if n < 10:
        return "%d件" % n
    base = (n // 10) * 10
    if n - base <= 2:
        return "%d件近く" % base
    if n - base >= 8:
        return "%d件近く" % (base + 10)
    return "%d件以上" % base


def rows_for(day):
    out = []
    for e in EV:
        for t in e.get("tickets", []):
            if t.get("startDate") != day:
                continue
            ty = t.get("type") or ""
            mt = re.search(r"(\d{1,2}):(\d{2})発売", ty)
            hhmm = "%s:%s" % (mt.group(1).zfill(2), mt.group(2)) if mt else "??:??"
            mp = re.search(r"（([^（）]*?)\s*(?:R9年\s*)?\d{1,2}/\d{1,2}", ty)
            pref = mp.group(1) if mp else (e.get("prefecture") or "")
            # 県名の表記ゆれを揃える（e+由来は「滋賀県」、ぴあ由来は「滋賀」）
            # 🚨 `(都|府|県)$` を丸ごと落とすと **「京都」が「京」になる**（2026-09-07にやらかした）。
            #    正式名の接尾辞だけを、都道府県の名前ごとに落とす。
            pref = re.sub(r"^東京都$", "東京", pref)
            pref = re.sub(r"^(大阪|京都)府$", r"\1", pref)
            pref = re.sub(r"^(..+?)県$", r"\1", pref)
            senko = "（先行）" if re.search(r"先行|プレリザーブ|プリセール|受付|会員|抽選", ty) else ""
            out.append({
                "genre": e.get("genre"), "id": e["id"],
                "name": (e.get("artist") or e.get("name") or "").strip(),
                "full": e.get("name") or "", "pref": pref, "time": hhmm,
                "senko": senko, "venue": e.get("venue") or "", "type": ty,
                "big": bool(BIG.search(e.get("venue") or "")),
            })
    # 🚨1行＝1公演。同じ公演の券種違い（一般／U-30／学生券）は1行に畳む
    seen, uniq = set(), []
    for r in out:
        k = (r["id"], r["time"], r["pref"], r["senko"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(r)
    uniq.sort(key=lambda r: (r["time"], r["name"]))
    return uniq


tm = rows_for(TOMORROW)
by_g = collections.OrderedDict()
for r in tm:
    by_g.setdefault(r["genre"], []).append(r)

with io.open("tmp/x_material_0907.txt", "w", encoding="utf-8") as f:
    f.write("■ 明日 9/8(火) 発売＝%d枠（このジャンルは1件も削らずに全部並べる）\n\n" % len(tm))
    for g, rs in by_g.items():
        f.write("【%s】%d枠\n" % (g, len(rs)))
        for r in rs:
            f.write("  %s %s／%s%s   （%s・%s）\n"
                    % (r["time"], r["name"], r["pref"], r["senko"], r["full"][:34], r["venue"][:26]))
        f.write("\n")

    for day, label in ((D2, "9/9(水)"), (D3, "9/10(木)")):
        rs = rows_for(day)
        # 🚨大物＝箱の大きさで選ぶ（時刻順に上から5件ではない）。選んでから時刻順に並べ直す
        RANK = ["ドーム", "アリーナ", "フォーラム", "NHK", "Zepp", "サントリーホール",
                "シンフォニーホール", "みなとみらいホール", "芸術劇場", "オペラパレス",
                "オペラシティ", "コンサートホール", "大劇場", "大ホール", "市民会館", "文化会館"]

        def score(r):
            v = r["venue"] or ""
            for i, w in enumerate(RANK):
                if w in v:
                    return i
            return len(RANK)

        seen, pick = set(), []
        for r in sorted(rs, key=score):
            # 同じ団体の別公演（指揮者違いの定期演奏会など）で5件を埋めない＝先頭10字で見る
            key = re.sub(r"[\s　]", "", r["name"])[:10]
            if score(r) >= len(RANK) or key in seen:
                continue
            seen.add(key)
            pick.append(r)
            if len(pick) >= 5:
                break
        pick.sort(key=lambda r: r["time"])
        f.write("■ %s 発売＝全%d枠。**大物5件だけ**並べて、残りは「%s」と書く\n"
                % (label, len(rs), rough(max(0, len(rs) - len(pick)))))
        for r in pick:
            f.write("  %s %s／%s%s   （%s）\n" % (r["time"], r["name"], r["pref"], r["senko"], r["venue"][:26]))
        f.write("\n")

print("明日 %d枠 / ジャンル %d" % (len(tm), len(by_g)))
