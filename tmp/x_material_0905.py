# -*- coding: utf-8 -*-
"""X投稿（夜の便）の素材を作る。台本 X_SCRIPT.md の形に合わせて出す。

出すもの:
  ① 明日(9/6)発売＝**ジャンル別に全部**（1件も削らない）
  ② 9/7・9/8 発売＝各ジャンル 5件くらい（**箱の大きさで選ぶ**＝ホール/アリーナを上に）
  ③ 各ジャンルの枠数（丸め方の判断用。投稿には実数を書かない）
"""
import json, re, io, datetime, collections

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS\s*=\s*(\[.*?\]);", html, re.S).group(1))
TODAY = datetime.date.today()
WD = "月火水木金土日"
RE_START = re.compile(r"(\d{1,2})/(\d{1,2})(?:\s*(\d{1,2}:\d{2}))?\s*発売\s*$")

GENRE_JP = {"jpop": "J-POP", "rock": "ROCK", "kpop": "K-POP", "yougaku": "洋楽",
            "enka": "演歌・歌謡", "idol": "アイドル", "anime": "アニメ・声優", "classic": "クラシック",
            "jazz": "ジャズ", "engeki": "演劇", "musical": "ミュージカル", "2.5ji": "2.5次元",
            "owarai": "お笑い", "dento": "伝統芸能", "hougaku": "邦楽", "ballet": "バレエ・ダンス",
            "sports": "スポーツ", "fes": "フェス", "kids": "キッズ", "event": "イベント",
            "talkshow": "トークショー", "aisatsu": "舞台挨拶", "fanevent": "ファンイベント",
            "musicetc": "その他の音楽"}
# 箱の大きさ（②の5件を選ぶため）。上にあるものを優先する
BIG = ("ドーム", "アリーナ", "スタジアム", "国際フォーラム", "NHKホール", "オーチャード", "サントリーホール",
       "フェスティバルホール", "オーブ", "ガーデンシアター", "武道館", "大ホール", "文化会館", "市民会館",
       "県民ホール", "芸術劇場", "オペラシティ", "Zepp", "サンプラザ", "厚生年金", "文化センター")


def sale_start(t):
    if t.get("startDate"):
        return t["startDate"]
    m = RE_START.search(t.get("type") or "")
    if m:
        y = 2026 if int(m.group(1)) >= 9 else 2027
        return "%04d-%02d-%02d" % (y, int(m.group(1)), int(m.group(2)))
    return None


def sale_time(t):
    m = re.search(r"(\d{1,2}:\d{2})\s*発売", t.get("type") or "")
    return m.group(1) if m else ""


def is_senko(t):
    return bool(re.search(r"(先行|プレリザーブ|プレオーダー|プリセール|抽選|先着先行)", t.get("type") or ""))


def venue_rank(e):
    v = (e.get("venue") or "") + (e.get("name") or "")
    for n, key in enumerate(BIG):
        if key in v:
            return n
    return 999


rows = collections.defaultdict(lambda: collections.defaultdict(list))
for e in events:
    g = e.get("genre")
    if g == "new":
        continue
    for t in e.get("tickets") or []:
        sd = sale_start(t)
        if not sd:
            continue
        d = datetime.date(*(int(x) for x in sd.split("-")))
        if not (TODAY < d <= TODAY + datetime.timedelta(days=3)):
            continue
        rows[g][sd].append((sale_time(t), e.get("artist") or e.get("name", ""),
                            e.get("prefecture", ""), is_senko(t), venue_rank(e),
                            e.get("venue", "")[:24], e["id"]))

TOM = (TODAY + datetime.timedelta(days=1)).isoformat()
buf = ["X投稿の素材（today=%s）" % TODAY.isoformat(), ""]
order = sorted(rows, key=lambda g: -len(rows[g].get(TOM, [])))
for g in order:
    days = rows[g]
    if not days.get(TOM):
        continue
    buf.append("=" * 70)
    buf.append("■ %s  … 明日%s発売 %d枠" % (GENRE_JP.get(g, g), TOM[5:], len(days[TOM])))
    for sd in sorted(days):
        d = datetime.date(*(int(x) for x in sd.split("-")))
        xs = days[sd]
        head = "【%d/%d(%s)発売】" % (d.month, d.day, WD[d.weekday()])
        if sd == TOM:
            buf.append("  %s ← 全部並べる（%d枠）" % (head, len(xs)))
            for tm, a, pref, sk, _, ven, i in sorted(xs, key=lambda x: (x[0] or "99:99", x[1])):
                buf.append("     %-6s %s／%s%s   [%s]" % (tm or "時刻なし", a, pref, "（先行）" if sk else "", ven))
        else:
            big = sorted(xs, key=lambda x: (x[4], x[0] or "99:99"))[:5]
            buf.append("  %s ← 5件くらい（全%d枠のうち箱の大きい順）" % (head, len(xs)))
            for tm, a, pref, sk, r, ven, i in sorted(big, key=lambda x: (x[0] or "99:99")):
                buf.append("     %-6s %s／%s%s   [%s]" % (tm or "時刻なし", a, pref, "（先行）" if sk else "", ven))
            buf.append("     （他 %d枠）" % (len(xs) - len(big)))
    buf.append("")

io.open("tmp/x_material_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("GENRES_TOMORROW=%d" % sum(1 for g in rows if rows[g].get(TOM)))
