# -*- coding: utf-8 -*-
"""振り分けた55件の一覧を logs/assigned_2026-09-08.md に残す。
   URLは index.html から機械抽出（手で書かない）。新着タブが空になる代わりの「見る場所」。"""
import io, re, json

def load(p):
    s = io.open(p, encoding="utf-8", newline="").read()
    return {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", s, re.S).group(1))}

BEFORE = load("index.html.bak_0908_assign")
AFTER = load("index.html")

moved = [i for i, e in AFTER.items()
         if e.get("genre") != "new" and BEFORE.get(i, {}).get("genre") == "new"]
moved.sort()

GL = {"jpop": "J-POP", "rock": "ロック", "classic": "クラシック", "jazz": "ジャズ",
      "enka": "演歌", "dento": "伝統", "musicetc": "その他音楽", "engeki": "演劇",
      "musical": "ミュージカル", "owarai": "お笑い", "kids": "キッズ", "art": "イベントアート",
      "aisatsu": "舞台挨拶", "dinnershow": "ディナーショー", "talkshow": "トークショー",
      "sports": "スポーツ", "fes": "フェス", "gakusai": "学園祭", "seiyuu": "声優",
      "event": "イベント"}

o = io.open("logs/assigned_2026-09-08.md", "w", encoding="utf-8")
W = o.write
W("# 2026-09-08 朝に振り分けたエントリ（新着タブから出したもの）\n\n")
W("**%d件**をぴあのカテゴリ由来の下書き(_genre)どおりに確定したわ。自分で再分類はしていない。\n\n" % len(moved))
W("検証＝別エージェントが12件をぴあの実ページからゼロ再導出（枠数・販売終了日・公演日・会場を突合）。\n")
W("機械ゲート＝check_order 違反0／check_badges OK／bareLF・CRCRLF・孤立CR 全0／NEW_ORDER と新着件数が一致。\n\n")
W("⚠️**プールに残した48件**＝e+由来47件（あなたが新着タブで実物を見るまで振り分けない）\n")
W("＋ id7165 博多・天神落語まつり（公演日の扱いを相談中）。\n\n")
W("| id | 公演名 | 会場 | 公演日 | 割り当てジャンル | 確認用URL |\n|---|---|---|---|---|---|\n")
for i in moved:
    e = AFTER[i]
    lk = e.get("links", {}) or {}
    url = (lk.get("pia") or lk.get("rakuten") or lk.get("eplus") or lk.get("lawson") or "").strip()
    if not url:
        for t in e.get("tickets", []) or []:
            if (t.get("url") or "").strip():
                url = t["url"].strip(); break
    g = e.get("genre") or ""
    extra = e.get("extraGenres") or []
    label = GL.get(g, g) + ("＋" + "＋".join(GL.get(x, x) for x in extra) if extra else "")
    cell = "[確認](%s)" % url if url else "(URLがデータに無い)"
    W("| %d | %s | %s | %s | **%s** | %s |\n" % (
        i,
        (e.get("name") or e.get("title") or "").replace("|", "｜")[:40],
        (e.get("venue") or "").replace("|", "｜")[:26],
        e.get("date") or "", label, cell))
o.close()
print("wrote logs/assigned_2026-09-08.md rows=%d" % len(moved))
