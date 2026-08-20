# -*- coding: utf-8 -*-
"""2026-08-10：期限切れ削除候補を e+ で裏取り（feedback_delete_nonpia_blindspot）。
「ぴあで0枠」は削除理由にならない。e+ 検索JSONで受付終了日が今日以降の公演が出たら
＝別会場が生きている可能性＝削除でなく育成。結果は目視で個別ページ確認へ回す。
"""
import re
import sys
import time
import urllib.parse
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TODAY = "20260810"

# (id, 検索語)  … 検索語は登録アーティスト名から表記ゆれの少ない形にした
TARGETS = [
    (173, "たをやめオルケスタ"),
    (535, "木村充揮"),
    (595, "伊藤政則"),
    (810, "四絃一撥ノ巻"),
    (828, "ピアニカの魔術師"),
    (916, "真夏の沖縄音楽フェスティバル"),
    (933, "CULTURE!!!CULTURE!!!CULTURE!!!"),
    (941, "アル☆カンパニー"),
    (1220, "めざましWANGANフェス"),
    (2039, "ファミリー狂言会"),
    (2300, "工藤静香"),
    (2306, "月代来実"),
    (2553, "北海道 meiji カップ"),
    (2601, "愛媛FC"),
    (2693, "銀河特急 ミルキー☆サブウェイ"),
    (2739, "レイラック滋賀FC"),
    (2847, "栃木SC"),
    (3233, "コドモパーティー"),
    (3247, "東京バレエ団 はじめてのバレエ"),
    (3297, "福岡県吹奏楽コンクール"),
    (3497, "光と影のプルミエール"),
    (3555, "Story of Aesop"),
    (3706, "無伴奏ソナタ"),
]


def search(kw):
    u = "https://eplus.jp/sf/search?keyword=" + urllib.parse.quote(kw)
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    h = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    rows, seen = [], set()
    for m in re.finditer(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"', h):
        url = "https://eplus.jp" + m.group(1)
        if url in seen:
            continue
        seen.add(url)
        blk = h[max(0, m.start() - 4000): m.end() + 4000]

        def g(key):
            mm = re.search(r'"%s":"([^"]*)"' % key, blk)
            return mm.group(1) if mm else ""
        rows.append({
            "url": url, "venue": g("kaijo_name"), "pref": g("todofuken_name"),
            "status": g("uketsuke_name_pc"), "end": g("uketsuke_end_datetime"),
            "kogyo": g("kogyo_name_1"),
        })
    return rows


for eid, kw in TARGETS:
    try:
        rows = search(kw)
    except Exception as e:
        print("id=%-5d %-22s ❌検索失敗 %s" % (eid, kw, e))
        continue
    alive = [r for r in rows if r["end"][:8] >= TODAY]
    if not alive:
        print("id=%-5d %-22s e+ヒット%d件 / 受付終了日が今日以降のもの 0件 → 削除OK" % (eid, kw, len(rows)))
    else:
        print("id=%-5d %-22s 🚨e+に生きてるかも %d件:" % (eid, kw, len(alive)))
        for r in alive:
            print("        %s | %s | %s | 受付〜%s | %s" % (
                r["kogyo"][:26], r["venue"][:20], r["pref"][:5], r["end"][:12], r["url"]))
    time.sleep(1.0)
