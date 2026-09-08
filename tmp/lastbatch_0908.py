# -*- coding: utf-8 -*-
"""9/8朝に投入したバッチを .claude/state/last_batch.json に記録する（翌朝の再チェックで使う）"""
import io, json

P = ".claude/state/last_batch.json"
d = json.load(io.open(P, encoding="utf-8"))

d["batches"].append({
    "date": "2026-09-08",
    "slot": "morning",
    "id_from": 7187,
    "id_to": 7336,
    "count": 105,
    "source": "ぴあ 発売前スイープ 7ジャンル×rlsStatus=0102/0202（14本とも最終ページまで到達・rc=0）",
    "assigned": False,
    "rechecked": False,
    "note": ("未掲載候補150件→ビルド148件→枠0で1件除外→重複チェック147件。"
             "投入105（同名の既存なし）／保留27（名前は同じだが既存に無い窓あり＝エージェント判定中）／"
             "投入しない15（既存と同じ販売窓）。"
             "実ページで確認して外した3件＝7268カマタマーレ讃岐と7293筑後SAKEフェスタが「本サイト取扱なし」、"
             "7313中部フィル室内楽が「貸切公演」（取りこぼし警告は誤報）。"
             "🚨投入105件は全部『発売前』＝受付中(0101)の穴埋めは0件。発売前だけで150件出たため。"
             "投入後ゲート＝check_badges OK / check_order 違反0 / bareLF・CRCRLF・孤立CR 全0 / "
             "reconcile --new は OK105・MISSING/DROP/STALE/FETCH/QC 全0・照合枠120/132。"
             "idは7187から＝削除済みidを再利用しないため過去バッチのid_toも見て採番した。"),
})

io.open(P, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=2))
print("batches=%d last=%s %s id%s..%s"
      % (len(d["batches"]), d["batches"][-1]["date"], d["batches"][-1]["slot"],
         d["batches"][-1]["id_from"], d["batches"][-1]["id_to"]))
