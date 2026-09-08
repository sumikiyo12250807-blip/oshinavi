# -*- coding: utf-8 -*-
"""楽天の「特設ページ形式」2件を取り込む（機械では読めないので実ページを読んで手で作った分）。

根拠（2026-09-09 に生HTMLを読んで確認。WebFetchは使っていない）
  ① https://ticket.rakuten.co.jp/event/circus/rtfjscy/
     アース製薬 クーザ 東京公演 / 公演期間 2027年2月24日(水)〜4月25日(日) / お台場ビッグトップ
     先行発売日 2026年9月12日(土)〜 ／ 一般発売日 2026年9月19日(土)〜
     🚨終了日はページに書かれていない → 発売前＋終了日不明の書き方
        （startDate と date を同じ日にする・saleUntilSoldOut は付けない・saleEndUnknown を付ける）
     🚨既存 id3674 と同じ興行なので**新エントリを作らず枠を足す**（ぴあの先行とは締切が違う別窓）
  ② https://ticket.rakuten.co.jp/event/rtb9s48/
     世田谷区たまがわ花火大会 / 令和8年10月3日(土) / 世田谷区立二子玉川緑地運動場（二子橋上流）鎌田会場
     一般販売 7月26日(日)午後2時 〜 (先着順)＝**終了日の記載なし**
     → 販売中＋終了日不明 → saleUntilSoldOut。公演日で締める
     ※テーブル席・ペアイス席・ペアシート席・シート席は「予定枚数終了」。
       イス席(6,500円)と大型シート席(55,000円)は残っているので枠としては生きている
使い方: python tmp/rakuten_add_0909.py [--apply]
"""
import io, json, re, sys, urllib.parse

sys.stdout.reconfigure(encoding="utf-8")

DEEP = "https://click.linksynergy.com/deeplink?id=z9x6HLNpWco&mid=53531&murl=%s"


def deep(u):
    return DEEP % urllib.parse.quote(u, safe="")


KOOZA = deep("https://ticket.rakuten.co.jp/event/circus/rtfjscy/")
HANABI = deep("https://ticket.rakuten.co.jp/event/rtb9s48/")

h = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
events = json.loads(m.group(2))
by = {e["id"]: e for e in events}

# ① クーザ＝既存 id3674 に楽天の2枠を足す
e = by[3674]
have = {t.get("type") for t in e.get("tickets") or []}
add = [
    {"type": "先行発売（東京 R9年 2/24〜4/25公演）9/12発売", "date": "2026-09-12",
     "startDate": "2026-09-12", "saleEndUnknown": True, "url": KOOZA},
    {"type": "一般発売（東京 R9年 2/24〜4/25公演）9/19発売", "date": "2026-09-19",
     "startDate": "2026-09-19", "saleEndUnknown": True, "url": KOOZA},
]
n_add = 0
for t in add:
    if t["type"] not in have:
        e.setdefault("tickets", []).append(t); n_add += 1
e.setdefault("links", {})["rakuten"] = KOOZA
e["verifiedAt"] = "2026-09-09"
print("id3674 クーザ ← 楽天の枠 %d件を追加（links.rakuten も付けた）" % n_add)

# ② たまがわ花火＝新エントリ（新着プールへ）
newid = max([x["id"] for x in events]) + 1
hanabi = {
    "id": newid,
    "artist": "世田谷区たまがわ花火大会",
    "name": "世田谷区たまがわ花火大会",
    "date": "2026-10-03",
    "dateLabel": "2026年10月3日(土) 東京 世田谷区立二子玉川緑地運動場",
    "venue": "世田谷区立二子玉川緑地運動場（二子橋上流）鎌田会場",
    "prefecture": "東京",
    "genre": "new",
    "_genre": "hanabi",
    "_srcgenre": "rakuten",
    "price": None,
    "links": {"rakuten": HANABI, "lawson": None, "pia": None, "eplus": None, "amazon": None},
    "tickets": [
        {"type": "一般販売（東京 10/3公演）", "date": "2026-10-03",
         "saleUntilSoldOut": True, "saleEndUnknown": True, "url": HANABI},
    ],
    "verified": True,
    "verifiedAt": "2026-09-09",
}
if not any(x.get("name") == hanabi["name"] for x in events):
    events.append(hanabi)
    print("id%d 世田谷区たまがわ花火大会 を新着に投入" % newid)
else:
    print("たまがわ花火は既にある＝投入しない")

if "--apply" not in sys.argv:
    print("(--apply で書き込み)")
    sys.exit(0)

out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace("\n", "\r\n") + h[m.end(2):]
# NEW_ORDER に新エントリを足す（並び順は投入順で固定）
m2 = re.search(r"(const NEW_ORDER = )(\[[^\]]*\])(;)", out)
order = json.loads(m2.group(2))
if newid not in order:
    order.append(newid)
out = out[:m2.start(2)] + json.dumps(order, ensure_ascii=False) + out[m2.end(2):]
io.open("index.html", "w", encoding="utf-8", newline="").write(out)
print("書き込み完了 / NEW_ORDER %d件" % len(order))
