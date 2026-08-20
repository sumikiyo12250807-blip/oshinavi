# -*- coding: utf-8 -*-
"""阪神4試合の企画席枠のURLを「バンドル」から「その試合の券種ページ」に差し替える。

reconcile_pia はエントリが参照する全ぴあURLの買える枠を数える。企画席のURLが
4試合ぶんを含むバンドル(b2665272等)のままだと、1試合のエントリなのに4試合分の枠が
見えて 12対24 のズレになる。ぴあは試合ごとに券種eventCdを持っているのでそれを使う。

  b2665272 NTTドコモビジネスファミリーシート
  b2665270 JCBエキサイトシート
  b2664954 セコム ツイン・トリプルシート
  b2664952 パナソニックペアシート
"""
import json, re, io, sys, shutil, os, time, urllib.request, html as _html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

P = "index.html"
BAK = "index.html.bak_0806_hanshin_urls"
BUNDLES = {
    "b2665272": "NTTドコモビジネスファミリーシート",
    "b2665270": "JCBエキサイトシート",
    "b2664954": "セコム ツイン・トリプルシート",
    "b2664952": "パナソニックペアシート",
}
# 公演日 → 統合先エントリ
GAME_BY_DATE = {"2026-09-15": 3841, "2026-09-17": 3853,
                "2026-09-29": 3849, "2026-10-01": 3858}


def fetch(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


def txt(s):
    return _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or ""))).strip()


# --- バンドルごとに「公演日 → 券種eventCd」を作る -----------------------------
seat_url = {}   # (席種名, 統合先id) -> URL
for bcd, seat in BUNDLES.items():
    h = fetch("https://t.pia.jp/pia/event/event.do?eventBundleCd=" + bcd)
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)', h):
        if "ticketSalesCard-2024__status" not in it:
            continue
        m_url = re.search(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"', it)
        dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
        if not m_url or not dts:
            continue
        gid = GAME_BY_DATE.get(dts[0])
        cd = re.search(r"eventCd=(\w+)", m_url.group(1))
        if gid and cd:
            seat_url[(seat, gid)] = "https://t.pia.jp/pia/event/event.do?eventCd=" + cd.group(1)
    time.sleep(1.2)

print("試合別の券種URLを %d本 取得" % len(seat_url))
if len(seat_url) != 16:
    print("🚨 16本そろわないので中止")
    sys.exit(1)

# --- 差し替え -----------------------------------------------------------------
h = open(P, encoding="utf-8", newline="").read()
NL = "\r\n" if "\r\n" in h else "\n"
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
if not os.path.exists(BAK):
    shutil.copyfile(P, BAK)

fixed = 0
for e in EVENTS:
    if e["id"] not in GAME_BY_DATE.values():
        continue
    for t in e.get("tickets") or []:
        mm = re.search(r"〔([^〕]+)〕", t.get("type") or "")
        if not mm:
            continue
        u = seat_url.get((mm.group(1), e["id"]))
        if u:
            t["url"] = u
            fixed += 1

new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2).replace("\n", NL)
open(P, "w", encoding="utf-8", newline="").write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("企画席の枠URLを試合別に差し替え: %d枠" % fixed)
