# -*- coding: utf-8 -*-
"""怪談候補(tmp/kaidan_candidates.json)を3つに仕分ける。

  A 確定  … 公演名そのものに怪談語が入っている
  B 要確認… 怪談師/怪談YouTuberの名前でヒットしたが公演名に怪談語が無い（本人の別ジャンル公演かも）
  C 除外  … どちらでもない＝検索の巻き添え

出力: tmp/kaidan_triage.txt ＋ tmp/kaidan_A.json / tmp/kaidan_B.json
"""
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"

NAMES = ["島田秀平", "好井まさお", "ナナフシギ", "田中俊行", "松原タニシ", "北野誠",
         "三木大雲", "夜馬裕", "匠平", "伊山亮吉", "チビル松村", "深津さくら",
         "シークエンスはやとも", "ゾゾゾ", "牛抱せん夏", "村上ロック"]
# 「ぁみ」は部分一致の巻き添えが308件出たので名前判定から外す（公演名に怪談語があればAで拾える）
# 全角も来るので正規化してから当てる
KAIDAN = re.compile(r"怪談|かいだん|カイダン|Kaidan|KAIDAN|心霊|しんれい|オカルト|都市伝説|"
                    r"怖い話|こわい話|百物語|怪異|ホラー|幽霊|呪い|実話怪談|怪読|恐怖")


def norm(s):
    # 全角英数を半角に
    return "".join(chr(ord(c) - 0xFEE0) if "！" <= c <= "～" else c for c in s)


cands = json.load(io.open(os.path.join(ROOT, "tmp", "kaidan_candidates.json"), encoding="utf-8"))
A, B, C = [], [], []
for r in cands:
    n = norm(r["name"])
    if KAIDAN.search(n):
        A.append(r)
    elif any(nm in n or nm in "".join(r["words"]) for nm in NAMES) and any(w in NAMES for w in r["words"]):
        B.append(r)
    else:
        C.append(r)

L = []
for tag, arr in (("A 公演名に怪談語あり＝確定", A), ("B 怪談師の名前ヒット・要確認", B)):
    L.append("=== %s  %d件 ===" % (tag, len(arr)))
    L.append("")
    for r in sorted(arr, key=lambda x: x["day"]):
        L.append("[%s] %s" % (r["status"], r["name"]))
        L.append("   %s ／ %s%s" % (r["day"], r["venue"],
                                    " ／ 発売 " + r["rls"] if r["rls"] else ""))
        L.append("   語=%s  %s" % (",".join(r["words"]), r["url"]))
        L.append("")
L.append("=== C 巻き添え(除外) %d件 ===" % len(C))
for r in sorted(C, key=lambda x: x["day"])[:60]:
    L.append("   %s ／ %s ／ 語=%s" % (r["name"][:46], r["day"], ",".join(r["words"])))
if len(C) > 60:
    L.append("   …ほか %d件" % (len(C) - 60))

io.open(os.path.join(ROOT, "tmp", "kaidan_triage.txt"), "w", encoding="utf-8").write("\n".join(L))
json.dump(A, io.open(os.path.join(ROOT, "tmp", "kaidan_A.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(B, io.open(os.path.join(ROOT, "tmp", "kaidan_B.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("A確定 %d / B要確認 %d / C除外 %d  → tmp/kaidan_triage.txt" % (len(A), len(B), len(C)))
