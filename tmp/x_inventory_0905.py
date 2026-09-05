# -*- coding: utf-8 -*-
"""X投稿の在庫側の素材＝「明日以降に発売開始する公演」をアーティスト単位で集める。

X投稿の本数の決め方（2026-09-01 ユーザー決定）:
  ① トレンド8位までに在庫があれば1本 ② Xフォロワー1位を主役に1本 ③ 残りはジャンル別まとめ
この道具は③の材料＝**ジャンル別に「誰が」「いつ」発売するか**を出す。

🚨 件数は投稿に書かない（[[feedback_x_no_counts_oshi_first]]）。ここで数えるのは選ぶためだけ。
"""
import json, re, io, datetime, collections

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", html, re.S).group(1))
TODAY = datetime.date.today()
WD = "月火水木金土日"
RE_START = re.compile(r"(\d{1,2})/(\d{1,2})(?:\s*(\d{1,2}:\d{2}))?\s*発売\s*$")

GENRE_JP = {"jpop": "J-POP", "rock": "ROCK", "kpop": "K-POP", "yougaku": "洋楽",
            "enka": "演歌", "idol": "アイドル", "anime": "アニメ・声優", "classic": "クラシック",
            "jazz": "ジャズ", "engeki": "演劇", "musical": "ミュージカル", "2.5ji": "2.5次元",
            "owarai": "お笑い", "dento": "伝統芸能", "hougaku": "邦楽", "ballet": "バレエ",
            "sports": "スポーツ", "fes": "フェス", "kids": "キッズ", "event": "イベント",
            "talkshow": "トークショー", "aisatsu": "舞台挨拶", "fanevent": "ファンイベント"}


def sale_start(t):
    if t.get("startDate"):
        return t["startDate"]
    m = RE_START.search(t.get("type") or "")
    if m:
        y = 2026 if int(m.group(1)) >= 9 else 2027
        return "%04d-%02d-%02d" % (y, int(m.group(1)), int(m.group(2)))
    return None


rows = collections.defaultdict(list)
for e in events:
    g = e.get("genre")
    if g == "new":
        continue
    for t in e.get("tickets") or []:
        sd = sale_start(t)
        if not sd:
            continue
        d = datetime.date(*(int(x) for x in sd.split("-")))
        if not (TODAY < d <= TODAY + datetime.timedelta(days=7)):
            continue          # 明日から1週間ぶん
        rows[g].append((sd, e.get("artist") or e.get("name", ""), e.get("name", ""),
                        e.get("prefecture", ""), t.get("type", ""), e["id"]))

buf = ["X投稿の在庫（明日 %s 〜 1週間に発売開始する公演）" % (TODAY + datetime.timedelta(days=1)).isoformat(), ""]
for g in sorted(rows, key=lambda k: -len(rows[k])):
    xs = sorted(rows[g])
    arts = []
    for _, a, _, _, _, _ in xs:
        if a not in arts:
            arts.append(a)
    buf.append("■ %s（%s） … %d枠 / %d組" % (GENRE_JP.get(g, g), g, len(xs), len(arts)))
    seen = set()
    for sd, a, nm, pref, ty, i in xs:
        if a in seen:
            continue
        seen.add(a)
        d = datetime.date(*(int(x) for x in sd.split("-")))
        n = sum(1 for r in xs if r[1] == a)
        buf.append("    %s(%s) %-26s %-22s %s%s"
                   % ("%d/%d" % (d.month, d.day), WD[d.weekday()], a[:26], nm[:22], pref,
                      ("  ×%d枠" % n) if n > 1 else ""))
    buf.append("")

io.open("tmp/x_inventory_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("GENRES=%d SLOTS=%d" % (len(rows), sum(len(v) for v in rows.values())))
