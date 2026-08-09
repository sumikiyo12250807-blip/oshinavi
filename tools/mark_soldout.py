#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「予定枚数終了」を消さずに残す（ユーザー方針 2026-08-09）。

Why:
  売り切れた瞬間にエントリを消すと、見た人には「売り切れた」のか
  「最初から載っていなかった」のか区別がつかない。それだとサイトを信用できない。
  （ユーザーが大相撲九月場所で実感＝OSHINAVIで見つけて買いに行ったら売り切れていた。
    その事実を後から確認できないと「載ってなかったのでは」と思ってしまう。）
  → ぴあが「予定枚数終了」と出している間は OSHINAVI にも出しておく。URLも生かしたまま。

判定（エントリ単位・ぴあ実ページが根拠）:
  1. 公演日が過ぎている            → 対象外（従来どおり削除ルート）
  2. ぴあに買える枠(受付中/発売前)  → 対象外（そもそも売り切れていない）
  3. ぴあ券種に「予定枚数終了」あり → soldout:true + soldoutSince を付ける
  4. 「予定枚数終了」が1つも無い    → 触らない（受付終了・取扱なし等＝従来どおり削除候補）
  販売期間が満了した枠(date < today)は売り切れではないので soldout にしない。

使い方:
  python tools/mark_soldout.py --ids 130,1644        # 判定のみ
  python tools/mark_soldout.py --ids 130,1644 --apply
  python tools/mark_soldout.py --review              # 既存soldoutを再チェック（朝ルーチン）
  python tools/mark_soldout.py --review --apply      # ぴあが下げた枠のsoldoutを解除
"""
import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heal_stale_deadlines import load_events, pia_urls  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
TODAY = datetime.date.today().isoformat()
OUT = "tmp/mark_soldout.json"

# ぴあが「売り切れ」の意味で出す文言。「受付終了」「結果発表」等は在庫切れとは限らないので含めない。
SOLDOUT_WORDS = re.compile(r"(予定枚数|完売|売り?切)")

# 🚨「本サイト取扱なし」（セブン-イレブン店頭のみ等）は is-before クラスが付くため
#    pia_tickets.py が「発売前＝買える枠」と読んでしまう。ぴあでは買えないので除外する。
#    （2026-08-09 大相撲九月場所で発覚＝全席完売なのに「買える枠2件」と出た）
NOT_ON_PIA = re.compile(r"(本サイト取扱なし|取扱なし|取り扱いなし)")


def pia_rows(url):
    """pia_tickets.py --all --json を呼ぶ。読めなければ None（混雑ページ等）。"""
    r = subprocess.run([sys.executable, "tools/pia_tickets.py", url, "--all", "--json"],
                       capture_output=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return None


def judge(ev):
    """(status, soldout券種リスト, メモ) を返す。"""
    if (ev.get("date") or "") < TODAY:
        return "skip", [], "公演日が過去"
    urls = pia_urls(ev)
    if not urls:
        return "skip", [], "ぴあURLなし"
    rows = pia_rows(urls[0])
    if rows is None:
        return "unreadable", [], "ぴあが読めない（混雑ページ疑い）"
    buyable = [r for r in rows if r.get("state") in ("受付中", "発売前")
               and not NOT_ON_PIA.search(r.get("statustext") or "")]
    if buyable:
        return "alive", [], "ぴあに買える枠が%d件ある" % len(buyable)
    sold = [r for r in rows if SOLDOUT_WORDS.search(r.get("statustext") or "")]
    if not sold:
        kinds = sorted({(r.get("statustext") or "?") for r in rows})
        return "nosold", [], "予定枚数終了の表示なし（%s）" % "／".join(kinds)[:60]
    return "soldout", sold, "ぴあ%d券種が予定枚数終了" % len(sold)


def targets_for_review(EVENTS):
    return [e for e in EVENTS
            if any(t.get("soldout") for t in (e.get("tickets") or []))]


def main():
    argv = sys.argv[1:]
    h = open("index.html", encoding="utf-8").read()
    m, EVENTS = load_events(h)
    byid = {e["id"]: e for e in EVENTS}

    if "--review" in argv:
        targets = targets_for_review(EVENTS)
        if not targets:
            print("既に soldout の枠を持つエントリは無し。")
            return
    elif "--ids" in argv:
        ids = [int(x) for x in argv[argv.index("--ids") + 1].replace(" ", "").split(",") if x]
        targets = [byid[i] for i in ids if i in byid]
    else:
        print("--ids か --review を指定して。")
        return

    review = "--review" in argv
    results = []
    for i, ev in enumerate(targets, 1):
        st, sold, note = judge(ev)
        results.append({"id": ev["id"], "status": st, "note": note})
        print("[%d/%d] id=%-5s %-24s %-10s %s"
              % (i, len(targets), ev["id"], (ev.get("artist") or "")[:24], st, note))

    if "--apply" not in argv:
        json.dump(results, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("\n（判定のみ。適用するなら --apply）→ %s" % OUT)
        return

    by_res = {r["id"]: r for r in results}
    marked = unmarked = 0
    drop = []
    for ev in targets:
        r = by_res.get(ev["id"])
        if not r:
            continue
        tickets = ev.get("tickets") or []
        if r["status"] == "soldout":
            for t in tickets:
                # 「販売期間が満了して終わった枠」は売り切れではないので触らない。
                # ただし startDate==date の隠れ枠は"発売日しか分かっていない"だけで
                # 満了ではない（ぴあが予定枚数終了にすると締切を出さないため締切が取れない）。
                # ここを満了扱いにすると、当日即完した枠が1つも売り切れ表示にならない。
                if t.get("soldout"):
                    continue
                d, sd = t.get("date") or "", t.get("startDate")
                expired = d < TODAY and not (sd and sd == d)
                if expired:
                    continue
                t["soldout"] = True
                t["soldoutSince"] = TODAY
                marked += 1
        elif review and r["status"] in ("nosold", "skip"):
            # ぴあがもう予定枚数終了を出していない＝枠ごと下げた → soldoutを外して削除候補へ
            for t in tickets:
                if t.get("soldout"):
                    t.pop("soldout", None)
                    t.pop("soldoutSince", None)
                    unmarked += 1
            drop.append((ev["id"], ev.get("artist", ""), r["note"]))
        elif review and r["status"] == "alive":
            for t in tickets:
                if t.get("soldout"):
                    t.pop("soldout", None)
                    t.pop("soldoutSince", None)
                    unmarked += 1

    bak = "index.html.bak_%s_soldout" % datetime.date.today().strftime("%m%d")
    open(bak, "w", encoding="utf-8").write(h)
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open("index.html", "w", encoding="utf-8").write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print("\n=== 予定枚数終了に変更 %d枠 / 解除 %d枠 (backup: %s) ===" % (marked, unmarked, bak))
    if drop:
        print("\n🚨 ぴあが枠を下げた＝削除候補（ユーザーOK後に削除）:")
        for i, name, note in drop:
            print("  id=%s %s … %s" % (i, name[:30], note))


if __name__ == "__main__":
    main()
