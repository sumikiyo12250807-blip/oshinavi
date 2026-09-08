# -*- coding: utf-8 -*-
"""投入した楽天の発売前5件のうち2件は既存と同じ興行だったので畳む。

  id7586 さだまさし［東京｜11月公演］ → 既存 id1 さだまさしコンサートツアー2026 神さまの言うとおり
     既存は「一般発売（東京 11/19〜11/20公演）10/9 10:00発売」を**締切なし**で持っている
     （＝発売日の翌日から画面に出ない隠れ枠）。楽天は締切 11/11 23:59 まで取れているので
     **楽天の枠を足す**（売り場が違う＝別の窓。feedback_capture_all_deadlines_on_add）。
  id7587 『禅とジブリ』京都展 [京都] → 既存 id2949 『禅とジブリ』京都展
     楽天の2枠はどちらも既存の枠が同じか、より広い締切で覆っているので**枠は足さない**。
     購入ボタンは楽天優先（feedback_vendor_priority）なので links.rakuten だけ付ける。

使い方: python tmp/rakuten_presale_dedup_0909.py [--apply]
"""
import io, json, re, sys, urllib.parse

sys.stdout.reconfigure(encoding="utf-8")
DEEP = "https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl=%s"


def deep(u):
    return DEEP % urllib.parse.quote(u, safe="")


SADA = deep("https://ticket.rakuten.co.jp/music/rtkb710/")
ZEN = deep("https://ticket.rakuten.co.jp/event/rtyt103/")

h = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

# ① さだまさし
e = by[1]
row = {"type": "一般発売（東京 11/19〜11/20公演）10/9 10:00発売 〜11/11 23:59",
       "date": "2026-11-11", "startDate": "2026-10-09", "url": SADA}
if not any(t.get("type") == row["type"] for t in e["tickets"]):
    e["tickets"].append(row)
    print("id1 に楽天の枠を足した: %s" % row["type"])
e.setdefault("links", {})["rakuten"] = SADA
e["verifiedAt"] = "2026-09-09"

# ② 禅とジブリ
e2 = by[2949]
e2.setdefault("links", {})["rakuten"] = ZEN
e2["verifiedAt"] = "2026-09-09"
print("id2949 に楽天リンクを付けた（枠は既存が覆っているので足さない）")

# ③ 重複した新エントリを落とす
before = len(events)
events = [x for x in events if x["id"] not in (7586, 7587)]
print("重複した新エントリ %d件を落とした（id7586 / id7587）" % (before - len(events)))

if "--apply" not in sys.argv:
    print("(--apply で書き込み)")
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace("\n", "\r\n") + h[m.end(2):]
m2 = re.search(r"(const NEW_ORDER = )(\[[^\]]*\])(;)", out)
order = [i for i in json.loads(m2.group(2)) if i not in (7586, 7587)]
out = out[:m2.start(2)] + json.dumps(order, ensure_ascii=False) + out[m2.end(2):]
io.open("index.html", "w", encoding="utf-8", newline="").write(out)
print("書き込み完了 / NEW_ORDER %d件" % len(order))
