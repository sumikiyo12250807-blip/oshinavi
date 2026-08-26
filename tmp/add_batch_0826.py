# -*- coding: utf-8 -*-
"""今日(8/26)の新着投入を last_batch.json に記録する。翌朝の再チェックで使う。"""
import json

P = ".claude/state/last_batch.json"
data = json.load(open(P, encoding="utf-8"))

if any(b.get("date") == "2026-08-26" and b.get("slot") == "noon" for b in data["batches"]):
    print("既に記録あり。何もしない。")
else:
    data["batches"].append({
        "date": "2026-08-26",
        "slot": "noon",
        "id_from": 5301,
        "id_to": 5331,
        "count": 17,
        "source": "ぴあ 発売前rlsIn=03を7ジャンル総ざらい（pia_sweep_all・全ジャンル到達率100%）",
        "assigned": False,
        "rechecked": False,
        "note": "🚨在庫の内訳＝未掲載の発売前候補201件→重複URLを除いて135件→**うち93件が同名の既存あり（＝ツアーの分裂）**で統合行き、部分一致11件が要目視、本当に新規は31件だけだった。31件をビルドして20件成立（11件は買える枠なしでskip＝宝塚『ポーの一族』系は全部これ）。そこから3件を除いて17件を投入＝5309 中田カウス／5311 さやかミニ落語会はeventCdが既存と一致（統合へ）、5323 RISE201は最終締切が8/27で近すぎる。投入前ゲート＝ページ到達率100%／dupcheck 名前一致0・eventCd一致2（除外済）／緩い部分一致0／check_badges OK／check_order 違反0／CRLF差0。翌朝(8/27)に①独立再照合②別エージェントの客観チェック→振り分け。🚨統合待ちが積み上がっている＝昨日からの65件＋今日の93件。新着収集より統合のほうが実害が大きい状態。"
    })
    with open(P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("追記した: 2026-08-26 noon id5301-5331 count=17")
