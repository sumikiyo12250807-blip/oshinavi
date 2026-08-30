# -*- coding: utf-8 -*-
"""e+ の判断待ち2件をユーザーの決定どおりに処理する（2026-08-30）。

① 東西ビッグバン … **2つに分ける**（大阪編は別エントリで新規）
   理由＝e+のページに東京編との関係の説明が無く、出演者も違う（大阪はニーチェ／東京はCo′COON）
② 上田正樹&内田勘太郎 … **1つにまとめる**（既存 id6004 に宮城10/21の枠を足す）

🚨 ②は「追加のみ・置換なし」。①は新規エントリ（既存は触らない）。
"""
import datetime
import importlib.util
import io
import json
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TODAY = datetime.date.today()


def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    argv = sys.argv
    sys.argv = [path, "__lib__"]
    try:
        sp.loader.exec_module(m)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return m


eh = load("eh", "tools/eplus_harvest.py")

MIYAGI_URL = "https://eplus.jp/sf/detail/4264360001-P0030002P021001"

P = "index.html"
src = io.open(P, encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", src, re.S)
EVENTS = json.loads(m.group(2))
byid = {e["id"]: e for e in EVENTS}

log = io.open("logs/eplus_decided_2026-08-30.md", "w", encoding="utf-8")
log.write("# e+ 判断待ち2件の処理 2026-08-30（ユーザー決定）\n\n")

# ---- ② 上田正樹&内田勘太郎＝1つにまとめる（既存に枠を足す） ----
e = byid[6004]
have = {re.sub(r"\?.*$", "", t.get("url") or "") for t in e.get("tickets", [])}
h = eh.fetch(MIYAGI_URL)
time.sleep(0.4)
wins = [w for w in eh.parse_windows(h) if w["ed"] >= TODAY]
iso = "2026-10-21"
tm = "18:00"
added = 0
log.write("## ② 上田正樹&内田勘太郎（id6004）＝1つにまとめる\n\n")
if re.sub(r"\?.*$", "", MIYAGI_URL) in have:
    log.write("  すでに登録済み\n")
else:
    for w in wins:
        same_day = (str(w["ed"]) == iso)
        sess = (" %s公演" % tm) if same_day else "公演"
        lab = re.sub(r"\s+", "", w["label"]) or ((w["kind"] or "先着") + "一般発売")
        if w["sd"] >= TODAY:
            typ = "%s（宮城県 10/21%s）%d/%d %s発売" % (lab, sess, w["sd"].month, w["sd"].day, w["st"])
            tk = {"type": typ, "date": str(w["ed"]), "url": MIYAGI_URL, "startDate": str(w["sd"])}
        else:
            typ = "%s（宮城県 10/21%s）〜%d/%d %s" % (lab, sess, w["ed"].month, w["ed"].day, w["et"])
            tk = {"type": typ, "date": str(w["ed"]), "url": MIYAGI_URL}
        e["tickets"].append(tk)
        added += 1
        log.write("  + %s\n    %s\n" % (typ, MIYAGI_URL))
    if added:
        # 会場・県・dateLabel をツアー表記に直す（2会場になったため）
        e["date"] = max(e.get("date") or "", iso)
        e["venue"] = "全国ツアー（BLUES ALLEY JAPAN／誰も知らない劇場）"
        e["prefecture"] = "東京・宮城"
        e["dateLabel"] = "2026年10月20日(火)〜2026年10月21日(水) 東京・宮城"
        log.write("  会場を全国ツアー表記に、公演日を 2026-10-21 に更新\n")
print("② 上田正樹＆内田勘太郎に +%d枠" % added)

shutil.copy(P, "index.html.bak_0830_decide")
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
arr = "\n".join("  " + l if i else l for i, l in enumerate(arr.split("\n")))
out = src[:m.start(2)] + arr + src[m.end(2):]
if "\r\n" in src:
    out = out.replace("\r\n", "\n").replace("\n", "\r\n")
io.open(P, "w", encoding="utf-8", newline="").write(out)
log.write("\n")
log.close()
print("index.html を更新した（①の大阪編は次のステップで新規ビルド）")
