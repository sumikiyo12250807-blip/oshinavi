# -*- coding: utf-8 -*-
"""【e+ 投入ゲート】ビルド結果が実ページと「1つ残らず」合っているかを機械で突き合わせる。

見るのは2つ：
  A. **枠（券種）の数**  … 実ページの買える窓の数 == 登録の ticket 数か
  B. **公演の数**        … アーティストページ(/sf/word/)に**同じ公演名の他の公演**が残っていないか

🚨 なぜ作ったか（どちらも2026-08-30・ユーザーが画面で発見）
  A＝`build` が公演ごとに窓を1つしか採っておらず（`max(near, key=ed)`）、
     **抽選プレオーダーと先着一般が両方ある公演で片方が消えた**。
     実害＝TOKIWA FES 2026（10/18 常磐大学）＝抽選プレオーダー(9/26 12:00〜10/1 18:00)が丸ごと欠落。
  B＝e+ の JSON-LD は多公演ツアーだと一部の公演しか持たない（reference_eplus_harvest 手順8）。
     実害＝**NoGoD**＝e+ に5公演あるのに登録は10/25浦和の1公演だけ
     （https://eplus.jp/sf/word/0000022177）。

🚨 設計＝[[feedback_zero_badge_gate]]と同じ「**原因でなく結果で網を張る**」。
   窓や公演の"選び方"を検査せず、「ページにN個 → 登録もN個か」という結果だけを見る。

使い方:
  python tools/gate_eplus_slots.py tmp/eplus_built.json
  python tools/gate_eplus_slots.py tmp/eplus_built.json --json tmp/gate_eplus_result.json
  python tools/gate_eplus_slots.py tmp/eplus_built.json --no-shows   # Aだけ見る（速い）

終了コード: 0=PASS / 1=枠か公演が合わない / 2=読めないページがあり判定不能
"""
import argparse
import datetime
import importlib.util
import io
import json
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TODAY = datetime.date.today()


def load_harvester():
    """eplus_harvest.py を main() を走らせずに読み込む（fetch / parse_windows / parse_ld を借りる）。"""
    spec = importlib.util.spec_from_file_location("eh", "tools/eplus_harvest.py")
    eh = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["eplus_harvest.py", "__gate__"]
    try:
        spec.loader.exec_module(eh)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return eh


def strip_q(u):
    return re.sub(r"\?.*$", "", u or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("built")
    ap.add_argument("--json", default="")
    ap.add_argument("--sleep", type=float, default=0.4)
    ap.add_argument("--no-shows", action="store_true", help="公演の取りこぼし判定(B)を省く")
    a = ap.parse_args()

    entries = json.load(io.open(a.built, encoding="utf-8"))
    if not entries:
        print("🚨 ビルド結果が0件。**index.html を投入前のバックアップに戻してから build したか**を確認して。")
        print("   （投入済みのまま build すると、DB突合が自分自身を既存と判定して0件になる）")
        return 2

    eh = load_harvester()
    cache, bad, unread, rows, miss = {}, [], [], [], []

    # ---- A: 枠の数 ----
    for e in entries:
        by_url = {}
        for t in e.get("tickets", []):
            u = strip_q(t.get("url") or (e.get("links") or {}).get("eplus"))
            by_url.setdefault(u, []).append(t)
        for u, ts in by_url.items():
            if not u:
                unread.append((e["id"], e.get("artist"), "ticket.url が無い"))
                continue
            if u not in cache:
                try:
                    cache[u] = eh.fetch(u)
                except Exception as ex:
                    cache[u] = ""
                    unread.append((e["id"], e.get("artist"), "fetch失敗 " + str(ex)[:40]))
                time.sleep(a.sleep)
            h = cache[u]
            if not h:
                unread.append((e["id"], e.get("artist"), "ページが空 " + u))
                continue
            live = [w for w in eh.parse_windows(h) if w["ed"] >= TODAY]
            rows.append((e["id"], e.get("artist"), u, len(live), len(ts)))
            if len(live) != len(ts):
                bad.append({
                    "id": e["id"], "artist": e.get("artist"), "url": u,
                    "page": len(live), "built": len(ts),
                    "page_slots": ["%s %s〜%s" % (w["label"], w["sd"], w["ed"]) for w in live],
                    "built_slots": [t.get("type") for t in ts],
                })

    # ---- B: 公演の取りこぼし ----
    if not a.no_shows:
        for e in entries:
            u0 = strip_q((e.get("links") or {}).get("eplus") or "")
            h0 = cache.get(u0) or ""
            if not h0:
                continue
            try:
                sibs = eh.sibling_show_urls(h0, None, eh.fetch)
            except Exception:
                sibs = []
            if not sibs:
                continue
            have = {strip_q(t.get("url") or "") for t in e.get("tickets", [])}
            have.add(u0)
            name = (e.get("name") or "").strip()
            extra = []
            for su in sibs:
                if su in have:
                    continue
                if su not in cache:
                    try:
                        cache[su] = eh.fetch(su)
                    except Exception:
                        cache[su] = ""
                    time.sleep(a.sleep)
                sh = cache[su]
                if not sh:
                    continue
                for sev in eh.parse_ld(sh):
                    if (sev.get("name") or "").strip() == name:
                        extra.append((sev.get("date"), sev.get("venue"), su))
                        break
            if extra:
                miss.append({"id": e["id"], "name": name, "extra": extra})

    print("=== e+ 投入ゲート ===")
    print("  エントリ %d件 / 照合したURL %d本" % (len(entries), len(rows)))
    print("  A 実ページの枠合計 %d / ビルドの枠合計 %d"
          % (sum(r[3] for r in rows), sum(r[4] for r in rows)))
    print("  B 公演の取りこぼし %d件" % (len(miss) if not a.no_shows else -1))

    if unread:
        print("\n⚠️ 読めなかったもの %d件（判定不能＝投入しない）:" % len(unread))
        for x in unread[:20]:
            print("   id%-6s %-24s %s" % (x[0], (x[1] or "")[:22], x[2]))
    if bad:
        print("\n🚨 A 枠数が合わない %d件（**投入しない**）:" % len(bad))
        for b in bad:
            print("   id%-6s %-24s 実ページ%d枠 ≠ ビルド%d枠"
                  % (b["id"], (b["artist"] or "")[:22], b["page"], b["built"]))
            print("      URL: %s" % b["url"])
            for s in b["page_slots"]:
                print("      ページ: %s" % s)
            for s in b["built_slots"]:
                print("      ビルド: %s" % s)
    if miss:
        print("\n🚨 B 同じ公演名の他の公演がアーティストページにある %d件（**投入しない**）:" % len(miss))
        for x in miss:
            print("   id%-6s %s ＋%d公演" % (x["id"], x["name"][:34], len(x["extra"])))
            for d, v, u in x["extra"]:
                print("      %s %s  %s" % (d, (v or "")[:24], u))

    if a.json:
        json.dump({"rows": rows, "bad": bad, "unread": unread, "missing_shows": miss},
                  io.open(a.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("\n→ %s" % a.json)

    if bad or miss:
        print("\n=== ❌ FAIL: 枠または公演が落ちている。直してから再ビルドすること ===")
        return 1
    if unread:
        print("\n=== ❌ FAIL: 読めないページがある＝一致を確認できていない ===")
        return 2
    print("\n=== ✅ PASS: 枠も公演も実ページと全件一致 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
