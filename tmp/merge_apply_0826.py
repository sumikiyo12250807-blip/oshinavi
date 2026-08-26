# -*- coding: utf-8 -*-
"""分裂したツアーを既存エントリに統合する（ぴあ再導出）。

やること＝対象エントリの「今のぴあURL＋今のticket.url＋足すURL」を全部 build_pia_entries に渡して
ゼロから枠を作り直し（feedback_bundle_full_rederive）、tickets を置き換える。

🚨守っていること
 - **読み書きはテキストモードで統一**（heal_stale_deadlines と同じ。
   バイナリ読み＋テキスト書きにすると改行が \r\r\n に二重化する＝feedback_index_html_crcrlf_trap）。
 - venue / dateLabel / artist は上書きしない（過去のQC手修正が巻き戻るため。heal と同じ方針）。
   会場が増えた場合は「要目視」として報告するだけ。
 - **非ぴあの枠（e+/楽天/ローチケ）を消さない**。build はぴあ枠しか作らないので、
   ぴあに無い公演の非ぴあ枠は据え置く（heal と同じ・ネクライトーキーの事故対策）。
 - 千秋楽(ev.date)は伸ばすだけ。**縮めない**（別の売り場の公演が残っている可能性）。
 - genre:new のエントリは **最早dateが動くと新着タブの並びが変わる**ので適用せず報告
   （feedback_new_list_order_lock＝ユーザーのチェック位置を崩さない）。

使い方:
  python tmp/merge_apply_0826.py --plan tmp/merge_todo_0826.json          # 再導出のみ（適用しない）
  python tmp/merge_apply_0826.py --plan tmp/merge_todo_0826.json --apply  # index.html に適用
plan の形: {"492": ["https://...", ...], "503": [...]}
"""
import json
import re
import sys
import datetime

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

import build_pia_entries as bpe
import heal_stale_deadlines as heal

APPLY = "--apply" in sys.argv
PLAN = sys.argv[sys.argv.index("--plan") + 1]
TODAY = datetime.date.today().isoformat()

plan = {int(k): v for k, v in json.load(open(PLAN, encoding="utf-8")).items()}

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
by_id = {e["id"]: e for e in EVENTS}


def pia_urls(ev, extra):
    urls = heal.pia_urls(ev)
    for u in extra:
        u = u.replace("ticket.pia.jp/pia/event.do", "t.pia.jp/pia/event/event.do")
        if u not in urls:
            urls.append(u)
    return urls


results = []
for eid in sorted(plan):
    ev = by_id.get(eid)
    if ev is None:
        print("id=%-5d ⚠️見つからない（欠番？）" % eid)
        continue
    urls = pia_urls(ev, plan[eid])
    old = ev.get("tickets") or []
    old_min = min([t.get("date") or "9999" for t in old] or ["9999"])
    try:
        ne = bpe.build({"newid": eid, "artist": ev.get("artist", ""), "urls": urls})
    except Exception as ex:
        print("id=%-5d ❌build失敗 %s: %s" % (eid, type(ex).__name__, str(ex)[:110]))
        continue
    if not ne:
        # build は「買える枠が1つも無い」と None を返す（売切/受付終了のみ）。
        # ここで落ちると残りのエントリが全部処理されないので、飛ばして続ける。
        print("id=%-5d ⚠️再導出で買える枠0→触らない（混雑ページ/全枠終了の疑い）" % eid)
        continue
    new = list(ne.get("tickets") or [])
    if not new:
        print("id=%-5d ⚠️再導出で0枠→触らない（混雑ページ疑い）" % eid)
        continue
    # 非ぴあ枠の据え置き（ぴあが持っていない公演のぶんだけ）
    newk = {heal.perf_key(t.get("type")) for t in new}
    keep = [t for t in old
            if (t.get("url") or "") and "pia.jp" not in (t.get("url") or "")
            and heal.perf_key(t.get("type")) not in newk]
    merged = new + keep
    new_min = min([t.get("date") or "9999" for t in merged] or ["9999"])
    warn = []
    if ev.get("genre") == "new" and new_min != old_min:
        warn.append("🚨新着プールの最早dateが動く(%s→%s)＝適用しない" % (old_min, new_min))
    newest = ne.get("date") or ""
    if newest and newest > (ev.get("date") or ""):
        warn.append("千秋楽が伸びる(%s→%s)" % (ev.get("date"), newest))
    if keep:
        warn.append("非ぴあ枠%dを据え置き" % len(keep))
    # 🚨枠が減る＝受付終了が落ちただけのこともあるが、生きた枠が消える事故と見分けがつかない。
    # 混雑ページを掴んでいると静かに減る（feedback_wpia_direct_sale_trap / 2026-08-06の実害）。
    # 自動では適用せず、1件ずつ実ページを見て決める。
    if len(merged) < len(old) and "--allow-shrink" not in sys.argv:
        warn.append("🚨枠が減る(%d→%d)＝適用しない・要目視" % (len(old), len(merged)))
    elif len(merged) < len(old):
        warn.append("枠が減る(%d→%d)＝消える枠の締切が過去だと目視で確認済み" % (len(old), len(merged)))
    results.append({"id": eid, "artist": ev.get("artist"), "n_old": len(old), "n_new": len(merged),
                    "tickets": merged, "warn": warn, "urls": urls,
                    "newdate": newest if newest > (ev.get("date") or "") else ev.get("date")})
    print("id=%-5d %-24s %2d枠 → %2d枠  %s" % (
        eid, (ev.get("artist") or "")[:24], len(old), len(merged), " / ".join(warn)))

json.dump(results, open("tmp/merge_result_0826.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("")
print("=== %d件を再導出 → tmp/merge_result_0826.json ===" % len(results))
if not APPLY:
    print("（--apply を付けると index.html に反映する）")
    sys.exit(0)

applied, skipped = 0, 0
for r in results:
    if any("適用しない" in w for w in r["warn"]):
        skipped += 1
        continue
    ev = by_id[r["id"]]
    ev["tickets"] = r["tickets"]
    ev["date"] = r["newdate"]
    ev["verifiedAt"] = TODAY
    applied += 1

bak = "index.html.bak_%s_merge" % datetime.date.today().strftime("%m%d")
open(bak, "w", encoding="utf-8").write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open("index.html", "w", encoding="utf-8").write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("適用 %d件 / 保留 %d件 (backup: %s)" % (applied, skipped, bak))
