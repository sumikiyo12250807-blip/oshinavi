# -*- coding: utf-8 -*-
"""夜のX投稿の素材＝明日(9/10)発売が始まる公演を、ジャンル別に機械抽出する。

🚨「発売開始」を拾う＝ticket.startDate が明日のもの（締切が明日のものではない）。
   曖昧な「一般発売」を発売開始と決めつけない（feedback_sale_start_vs_deadline）。
出力は tmp/x_material_0910.md（コンソールに日本語を出さない）。
"""
import io, re, json, datetime, collections

TOMORROW = "2026-09-10"
GL = {"jpop": "J-POP", "rock": "ロック", "kpop": "K-POP", "yougaku": "洋楽",
      "classic": "クラシック", "jazz": "ジャズ", "enka": "演歌", "dento": "伝統",
      "musicetc": "その他音楽", "engeki": "演劇", "musical": "ミュージカル",
      "owarai": "お笑い", "kids": "キッズ", "sports": "スポーツ", "art": "イベントアート",
      "anime": "アニソン", "idol": "アイドル", "seiyuu": "声優", "fes": "フェス",
      "aisatsu": "舞台挨拶", "talkshow": "トークショー", "dinnershow": "ディナーショー",
      "hanabi": "花火大会", "event": "イベント", "gakusai": "学園祭", "2.5ji": "2.5次元"}

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))

rows = collections.defaultdict(list)
for e in EV:
    if e.get("genre") == "new":
        continue                      # 新着プールはまだ振り分け前なので出さない
    for t in e.get("tickets") or []:
        if t.get("startDate") != TOMORROW or t.get("soldout"):
            continue
        ty = t.get("type") or ""
        m = re.search(r"(\d{1,2}):(\d{2})\s*発売", ty)
        hhmm = "%02d:%s" % (int(m.group(1)), m.group(2)) if m else "??:??"
        mp = re.search(r"（([^（）]*?)\s*[\d/〜～・]+公演）", ty)
        pref = mp.group(1) if mp else (e.get("prefecture") or "")
        senko = "先行" in ty or "プレリザーブ" in ty or "抽選" in ty or "プリセール" in ty
        rows[e.get("genre") or "?"].append(
            (hhmm, e.get("name") or "", pref, e.get("venue") or "", senko, e["id"]))

o = io.open("tmp/x_material_0910.md", "w", encoding="utf-8")
o.write("# 明日 %s に発売が始まる公演（Xの素材）\n\n" % TOMORROW)
tot = sum(len(v) for v in rows.values())
o.write("合計 **%d枠** / %dジャンル\n\n" % (tot, len(rows)))
o.write("| ジャンル | 枠数 |\n|---|---|\n")
for g, v in sorted(rows.items(), key=lambda x: -len(x[1])):
    o.write("| %s | %d |\n" % (GL.get(g, g), len(v)))

for g, v in sorted(rows.items(), key=lambda x: -len(x[1])):
    o.write("\n## %s（%d枠）\n\n" % (GL.get(g, g), len(v)))
    for hhmm, name, pref, venue, senko, i in sorted(v):
        o.write("- `%s` %s／%s%s  <small>id%d %s</small>\n"
                % (hhmm, name[:44], pref, "（先行）" if senko else "", i, venue[:28]))
o.close()
print("明日発売 %d枠 / ジャンル %d -> tmp/x_material_0910.md" % (tot, len(rows)))
