# -*- coding: utf-8 -*-
"""阪神甲子園の「席種違い」で別ページになっている16エントリを【試合ごと1エントリ】に統合する。
（2026-08-06 ユーザー選択「1. 試合ごとに1エントリへまとめる」）

  9/15    対中日ドラゴンズ       ← base id3841
  9/17    対広島東洋カープ       ← base id3853
  9/29-30 対東京ヤクルトスワローズ ← base id3849
  10/1    対読売ジャイアンツ     ← base 無し（企画席の枠だけ）→ 新規 id3858

席種エントリの枠は「<席種名>／<販売種別>（…）」に直し、各枠に元ページのURLを付ける
（[[feedback_tour_per_ticket_url]]＝どこで買うかが枠ごとに分かる）。
3836【車椅子席専用駐車場利用券】は8/28〜10/1の複数試合が対象なので単独エントリのまま残す。
"""
import json, io, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = "tmp/built_0806.json"
OUT = "tmp/built_0806_merged.json"

built = json.load(open(SRC, encoding="utf-8-sig"))
by_id = {e["id"]: e for e in built}

# 試合キー（チケットtypeの「（兵庫 9/15公演）」から引く）→ 統合先
GAME = {
    "9/15": {"base": 3841, "name": "阪神タイガース対中日ドラゴンズ 公式戦"},
    "9/17": {"base": 3853, "name": "阪神タイガース対広島東洋カープ 公式戦"},
    "9/29〜9/30": {"base": 3849, "name": "阪神タイガース対東京ヤクルトスワローズ 公式戦"},
    "10/1": {"base": None, "name": "阪神タイガース対読売ジャイアンツ 公式戦"},
}

# 吸収する側（席種エントリ）: id → 枠名に付ける席種名
SEAT = {
    3837: "車椅子席", 3838: "車椅子席", 3839: "車椅子席",
    3845: "DTSボックス", 3850: "DTSボックス", 3854: "DTSボックス",
    3846: "ドコモラウンジ付き", 3851: "ドコモラウンジ付き", 3855: "ドコモラウンジ付き",
    3848: "三ツ矢サイダーボックス", 3852: "三ツ矢サイダーボックス", 3856: "三ツ矢サイダーボックス",
    3842: "NTTドコモビジネスファミリーシート",
    3843: "JCBエキサイトシート",
    3844: "セコム ツイン・トリプルシート",
    3847: "パナソニックペアシート",
}

NEW_GIANTS_ID = 3858


def game_key(type_):
    m = re.search(r"（兵庫 ([^）]+?)公演）", type_ or "")
    return m.group(1) if m else None


# --- 統合先エントリの器を用意 -------------------------------------------------
targets = {}
for k, g in GAME.items():
    if g["base"] is not None:
        e = by_id[g["base"]]
        targets[k] = e
    else:
        donor = by_id[3842]  # 企画席bundleの器を借りて10/1専用エントリを作る
        e = json.loads(json.dumps(donor, ensure_ascii=False))
        e["id"] = NEW_GIANTS_ID
        e["artist"] = g["name"]
        e["name"] = g["name"]
        e["date"] = "2026-10-01"
        e["dateLabel"] = "2026年10月1日(木) 兵庫 阪神甲子園球場"
        e["venue"] = "阪神甲子園球場"
        e["prefecture"] = "兵庫"
        e["tickets"] = []
        e["links"] = dict(donor["links"])
        targets[k] = e

# baseエントリの枠は「そのゲームの枠」だけであることを確かめる
for k, g in GAME.items():
    if g["base"] is None:
        continue
    for t in targets[k]["tickets"]:
        assert game_key(t["type"]) == k, (k, t["type"])

# --- 席種エントリの枠を配る ---------------------------------------------------
moved, orphan = 0, []
for sid, seat in SEAT.items():
    src = by_id[sid]
    url = (src.get("links") or {}).get("pia")
    for t in src.get("tickets") or []:
        k = game_key(t["type"])
        if k not in targets:
            orphan.append((sid, t["type"]))
            continue
        nt = dict(t)
        nt["type"] = "%s／%s" % (seat, t["type"])
        if url:
            nt["url"] = url
        targets[k]["tickets"].append(nt)
        moved += 1

if orphan:
    print("🚨 行き先不明の枠があるので中止:")
    for o in orphan:
        print("   ", o)
    sys.exit(1)

# --- 出力（統合先以外の阪神席種エントリは落とす）-------------------------------
drop = set(SEAT.keys()) | {3841, 3849, 3853}
out = []
for e in built:
    if e["id"] in drop:
        continue
    out.append(e)

# 統合済みエントリを id 昇順の正しい位置に差し込む（3836の直後＝阪神が固まる）
merged = [targets["9/15"], targets["9/17"], targets["9/29〜9/30"], targets["10/1"]]
for e in merged:
    e["_mergedFrom"] = "席種違いを試合単位に統合(2026-08-06)"
pos = next(i for i, e in enumerate(out) if e["id"] == 3836) + 1
out = out[:pos] + merged + out[pos:]

json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("統合: 席種枠 %d個を %d試合へ配った" % (moved, len(merged)))
for k in ["9/15", "9/17", "9/29〜9/30", "10/1"]:
    e = targets[k]
    print("  id%s %s ＝ %d枠" % (e["id"], e["artist"], len(e["tickets"])))
print("エントリ %d件 → %d件  → %s" % (len(built), len(out), OUT))
