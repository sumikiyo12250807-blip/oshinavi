# -*- coding: utf-8 -*-
"""X投稿の素材を「1投稿＝1束」に整形して、Fableに渡せる形で書き出す。

本数の決め方（X_SCRIPT.md）＝
  ① トレンド枠 0〜1本（別途トレンドを見てから）
  ② 主役枠 1本＝翌日発売でXフォロワー1位 → **LiSA（159.5万・記録済み）**
  ③ まとめ枠＝ジャンル別（1投稿＝1ジャンル）

🚨明日発売はそのジャンルを1件も削らず全部並べる。
🚨2〜3日後は5件くらいに絞る＝**箱の大きさ（会場のキャパ）で選ぶ**。
"""
import collections, datetime, json, re, io

TOMORROW = "2026-09-05"
LATER = ["2026-09-06", "2026-09-07"]
WD = "月火水木金土日"

# 投稿の束（1投稿＝1束）。ジャンルキーの並びがそのまま本文の並び。
BUNDLES = [
    ("J-POPなどの音楽", ["jpop"]),
    ("クラシック", ["classic"]),
    ("お笑い・落語", ["owarai"]),
    ("舞台・ミュージカル", ["engeki", "musical", "aisatsu", "talkshow", "dento", "hougaku", "2.5ji", "seiyuu"]),
    ("スポーツ・おでかけ", ["sports", "art", "gakusai", "hanabi", "kids", "event", "gourmet", "dinnershow", "fes"]),
    ("洋楽・演歌・ジャズなど", ["yougaku", "enka", "jazz", "rock", "musicetc", "anime", "idol",
                               "kpop", "hiphop", "chanson", "vtuber", "youtuber", "fanevent",
                               "kaidan", "magic", "circus", "douyou"]),
]
STAR_ID = 4052   # LiSA

src = io.open("index.html", encoding="utf-8", newline="").read()
EVENTS = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", src, re.S).group(1))

rows = collections.defaultdict(list)
seen = set()
for e in EVENTS:
    g = e.get("genre") or ""
    if g == "new":
        g = e.get("_genre") or "musicetc"
    for t in e.get("tickets", []):
        if t.get("soldout"):
            continue
        sd = t.get("startDate")
        if sd != TOMORROW and sd not in LATER:
            continue
        m = re.search(r"(\d{1,2})/(\d{1,2})\s+(\d{1,2}:\d{2})発売", t.get("type", ""))
        if not m:
            continue
        hhmm = m.group(3)
        pref = e.get("prefecture") or ""
        pm = re.search(r"（([^（）]*?)\s+(?:R\d年\s*)?\d{1,2}/\d{1,2}", t.get("type", ""))
        if pm and pm.group(1).strip():
            pref = pm.group(1).strip()
        kind = "先行" if re.match(r"^(先行|.*先行|プレリザーブ|プリセール|抽選|.*次受付|.*次プレリザーブ)",
                                  t["type"]) else "一般"
        key = (sd, hhmm, e.get("artist", ""), pref, kind)
        if key in seen:
            continue
        seen.add(key)
        rows[(sd, g)].append({"time": hhmm, "artist": e.get("artist", ""), "pref": pref,
                              "kind": kind, "id": e.get("id"), "venue": e.get("venue", "")})

# 箱の大きさで「2〜3日後の5件」を選ぶための目安
BIG = ("ドーム", "アリーナ", "スタジアム", "大ホール", "ホールA", "国際フォーラム", "武道館",
       "Zepp", "サンプラザ", "文化会館", "市民会館", "オーチャード", "サントリーホール",
       "オペラシティ", "芸術劇場", "劇場")


def big_first(lst):
    return sorted(lst, key=lambda r: (0 if any(b in r["venue"] for b in BIG) else 1, r["time"]))


def jp(d):
    dt = datetime.date.fromisoformat(d)
    return "%d/%d(%s)" % (dt.month, dt.day, WD[dt.weekday()])


out = []
star = next((e for e in EVENTS if e.get("id") == STAR_ID), None)
out.append("=" * 72)
out.append("【投稿1・主役枠】LiSA（Xフォロワー 159.5万＝翌日発売で1位）")
out.append("=" * 72)
if star:
    out.append("  エントリ名: %s" % star.get("name"))
    out.append("  ツアー期間: %s" % star.get("dateLabel"))
    out.append("  会場一覧  : %s" % star.get("venue"))
    for t in star.get("tickets", []):
        if t.get("startDate") == TOMORROW:
            out.append("  ★明日発売: %s" % t.get("type"))
    out.append("  ※このエントリの他の枠（先行など）は明日発売ではないので投稿に出さない")

for label, gens in BUNDLES:
    tom = []
    for g in gens:
        tom += rows.get((TOMORROW, g), [])
    if not tom:
        continue
    out.append("")
    out.append("=" * 72)
    out.append("【投稿・まとめ枠】%s … 明日 %d件" % (label, len(tom)))
    out.append("=" * 72)
    out.append("■ %s発売（この分は1件も削らず全部並べる）" % jp(TOMORROW))
    for r in sorted(tom, key=lambda x: (x["time"], x["artist"])):
        mark = "（先行）" if r["kind"] == "先行" else ""
        out.append("  %s %s／%s%s" % (r["time"], r["artist"], r["pref"], mark))
    for d in LATER:
        lat = []
        for g in gens:
            lat += rows.get((d, g), [])
        if not lat:
            continue
        pick = big_first(lat)[:5]
        out.append("")
        out.append("■ %s発売（大きい会場から5件だけ・残りは件数を丸めて書く）" % jp(d))
        for r in sorted(pick, key=lambda x: x["time"]):
            mark = "（先行）" if r["kind"] == "先行" else ""
            out.append("  %s %s／%s%s" % (r["time"], r["artist"], r["pref"], mark))
        if len(lat) > 5:
            n = len(lat)
            rounded = ("%d件以上" % (n // 10 * 10)) if n >= 20 else ("%d件近く" % (round(n / 10) * 10) if n >= 10 else "%d件" % n)
            out.append("  … 他 %s（本文では「%s」と丸めて書く／実数は書かない）" % (n - 5, rounded))

io.open("tmp/x_bundles_0904.txt", "w", encoding="utf-8").write("\n".join(out))
print("WROTE tmp/x_bundles_0904.txt")
print("まとめ枠=%d本 ＋ 主役1本" % sum(1 for label, gens in BUNDLES
                                      if any(rows.get((TOMORROW, g)) for g in gens)))
