# -*- coding: utf-8 -*-
"""Fableに渡す素材を1枚にまとめる。
  ・明日(9/10)発売＝ジャンル別に**全部**
  ・9/11 と 9/12＝ジャンル別に「大物」5件くらい（会場の大きさで選ぶ）
🚨「発売開始」＝ticket.startDate がその日のもの（締切がその日のものではない）。
"""
import io, re, json, collections, sys
sys.stdout.reconfigure(encoding='utf-8')

DAYS = ["2026-09-10", "2026-09-11", "2026-09-12"]
WD = {0: "月", 1: "火", 2: "水", 3: "木", 4: "金", 5: "土", 6: "日"}
import datetime

GL = {"jpop": "J-POP", "rock": "ロック", "kpop": "K-POP", "yougaku": "洋楽",
      "classic": "クラシック", "jazz": "ジャズ", "enka": "演歌", "dento": "伝統",
      "hougaku": "邦楽", "musicetc": "その他音楽", "engeki": "演劇", "musical": "ミュージカル",
      "owarai": "お笑い", "kids": "キッズ", "sports": "スポーツ", "art": "アート",
      "anime": "アニソン", "idol": "アイドル", "seiyuu": "声優", "fes": "フェス",
      "aisatsu": "舞台挨拶", "talkshow": "トークショー", "dinnershow": "ディナーショー",
      "hanabi": "花火大会", "event": "イベント", "gakusai": "学園祭", "2.5ji": "2.5次元",
      "circus": "サーカス", "magic": "マジック", "gourmet": "グルメ", "fanevent": "ファンイベント"}

# 「大物」＝箱の大きさ。会場名のこの語を上位に。
BIG = ["ドーム", "アリーナ", "国際フォーラム", "武道館", "スタジアム", "коンサートホール",
       "大ホール", "コンサートホール", "大劇場", "文化会館", "市民会館", "芸術劇場", "公会堂",
       "サンプラザ", "ホール"]


def bigness(venue):
    v = venue or ""
    for i, k in enumerate(BIG):
        if k in v:
            return i
    return len(BIG)


h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

per_day = {d: collections.defaultdict(list) for d in DAYS}
for e in EV:
    if e.get("genre") == "new":
        continue
    for t in e.get("tickets") or []:
        sd = t.get("startDate")
        if sd not in per_day or t.get("soldout"):
            continue
        ty = t.get("type") or ""
        m = re.search(r"(\d{1,2}):(\d{2})\s*発売", ty)
        hhmm = "%02d:%s" % (int(m.group(1)), m.group(2)) if m else "??:??"
        mp = re.search(r"（([^（）]*?)\s*[\d/〜～・]+公演）", ty)
        pref = (mp.group(1) if mp else (e.get("prefecture") or "")).replace("県", "")
        senko = any(k in ty for k in ("先行", "プレリザーブ", "抽選", "プリセール", "受付"))
        per_day[sd][e.get("genre") or "?"].append(
            (hhmm, e.get("name") or "", pref, e.get("venue") or "", senko, e["id"]))

o = io.open("tmp/x_material_full_0910.md", "w", encoding="utf-8")
for di, d in enumerate(DAYS):
    dt = datetime.date.fromisoformat(d)
    label = "%d/%d(%s)" % (dt.month, dt.day, WD[dt.weekday()])
    rows = per_day[d]
    tot = sum(len(v) for v in rows.values())
    if di == 0:
        o.write("# 【明日】%s 発売＝ジャンル別に全部（1件も削らない）\n\n" % label)
    else:
        o.write("\n\n# 【%s 発売】＝各ジャンル 大物5件くらい（箱の大きい順に選んである）\n\n" % label)
    o.write("合計 %d枠 / %dジャンル\n" % (tot, len(rows)))
    for g, v in sorted(rows.items(), key=lambda x: -len(x[1])):
        pick = sorted(v)
        if di > 0:
            pick = sorted(sorted(v, key=lambda r: bigness(r[3]))[:5])
        o.write("\n## %s（%s・%d枠中%d件）\n" % (GL.get(g, g), label, len(v), len(pick)))
        for hhmm, name, pref, venue, senko, i in pick:
            o.write("- `%s` %s／%s%s\n" % (hhmm, name[:48], pref, "（先行）" if senko else ""))
        if di > 0 and len(v) > len(pick):
            o.write("- 他\n")
o.close()
print("→ tmp/x_material_full_0910.md")
for d in DAYS:
    print("  %s = %d枠 / %dジャンル" % (d, sum(len(v) for v in per_day[d].values()), len(per_day[d])))
