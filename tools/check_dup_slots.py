# -*- coding: utf-8 -*-
"""🚨同じエントリに「実質同じ枠」が2つ以上ある＝画面に同じバッジが2枚並ぶのを拾う番人。

2026-09-04 新設。この日、サイト全体で196グループ（392枠）が二重登録されているのが見つかった。
どの既存の道具でも拾えなかった＝
  - dedup_badges は判定キーに url を含むので「url無し版 と url有り版」のペアを畳めない
  - reconcile_pia --new は新着プールだけ
  - check_zero_badge は「枠が0」を見る（多すぎるほうは見ない）
原因の型（[[feedback_build_pia_multiurl_loses_ticket_url]]＝複数URLを渡すと2本目以降の
ticket.url が落ちる）で探すのではなく、**結果（同じ枠が2枚ある）で数える**
（[[feedback_zero_badge_gate]]「原因で網を張ると知らない原因は漏れる」と同じ設計）。

分類:
  A url無し と url有り のペア（url有り側は1種類）→ 畳んでよい。url有りを残す
  B url まで完全に同じ            → 畳んでよい。1つ残す
  C url が2種類以上ある            → 🚨触らない。飛び先が違う＝別の売り場かもしれない
                                     （[[feedback_dedup_badges_keeps_urls]]）

終了コード: 2＝A/Bがある（要対応） / 1＝Cだけある（方針の確認待ち） / 0＝健全

  python tools/check_dup_slots.py
  python tools/check_dup_slots.py --ids   # A/Bを持つエントリのidをカンマ区切りで
"""
import json, re, io, sys
from collections import defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

PATH = "index.html"
IDS_ONLY = "--ids" in sys.argv

raw = io.open(PATH, encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", raw, re.S)
if not m:
    print("EVENTS配列が読めない"); sys.exit(3)
events = json.loads(m.group(1))

A, B, C = [], [], []
for e in events:
    g = defaultdict(list)
    for t in e.get("tickets", []):
        g[(t.get("type"), t.get("date"))].append(t)
    for k, ts in g.items():
        if len(ts) < 2:
            continue
        urls = [t.get("url") or "" for t in ts]
        uniq = set(urls)
        rec = (e.get("id"), e.get("name"), k[0], k[1], urls)
        if "" in uniq and len(uniq - {""}) == 1:
            A.append(rec)
        elif len(uniq) == 1:
            B.append(rec)
        else:
            C.append(rec)

if IDS_ONLY:
    ids = sorted(set(r[0] for r in A + B))
    print(",".join(str(i) for i in ids))
    sys.exit(0)

total_slots = sum(len(e.get("tickets", [])) for e in events)
print("=== 同じ枠が2枚以上あるエントリ（全%d件・枠%d） ===" % (len(events), total_slots))
print("  A url無し＋url有りのペア … %d組（%dエントリ）＝畳んでよい"
      % (len(A), len(set(r[0] for r in A))))
print("  B urlまで完全に同じ      … %d組（%dエントリ）＝畳んでよい"
      % (len(B), len(set(r[0] for r in B))))
print("  C urlが2種類以上         … %d組（%dエントリ）＝🚨触らない・方針の確認へ"
      % (len(C), len(set(r[0] for r in C))))

for tag, g, limit in (("【A 畳んでよい（url無し版が余っている）】", A, 20),
                      ("【B 畳んでよい（完全重複）】", B, 20),
                      ("【C 触らない（飛び先が違う）】", C, 10)):
    if not g:
        continue
    print("\n" + tag)
    for eid, name, ty, dt, urls in g[:limit]:
        print("  id=%-5s %s" % (eid, (name or "")[:44]))
        print("        %s | 〜%s" % (ty, dt))
        for u in urls:
            print("          %s" % (u or "(url無)"))
    if len(g) > limit:
        print("  … 他 %d組" % (len(g) - limit))

if A or B:
    print("\n🚨要対応＝A/Bが %d組ある。畳んでから push すること。" % (len(A) + len(B)))
    sys.exit(2)
if C:
    print("\nC のみ＝飛び先が違う重複。方針が決まるまで触らない。")
    sys.exit(1)
print("\n✅健全＝二重登録なし。")
sys.exit(0)
