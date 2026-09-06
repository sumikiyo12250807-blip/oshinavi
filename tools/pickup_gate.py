# -*- coding: utf-8 -*-
"""記事「今週のピックアップ」を反映する前の**絶対条件**を機械で守る番人。

ユーザー明示（2026-09-06）＝「①②は絶対条件です」
  ①取りこぼしチェック ②ファクトチェック → ③ユーザーに見せる → ④OK後に反映

【なぜ要るか】
2026-09-06、9/5にファクトチェックを通した記事を**その後で大幅に書き直し**、
古いチェックを根拠に「ファクトチェック済み」としてユーザーに見せ、公開した。
結果＝**故人（西村智彦・2025年6月5日逝去）を現在形で「3人ね」と書いた記事が公開された**。
①の取りこぼしチェックにいたっては一度も走らせていなかった
（窓の発売356件に対し記事は17組。沢田研二・モーニング娘。'26 などが漏れていた）。

【この番人の効き方】
記録は **draft.md の中身のハッシュ** に結びつける。だから
**本文を1文字でも書き直すと、前の記録は自動的に無効になる**。
「前に通したから大丈夫」が成立しない。

使い方:
  python tools/pickup_gate.py --record gap  tmp/pickup0906/draft.md   # ①を終えたら
  python tools/pickup_gate.py --record fact tmp/pickup0906/draft.md   # ②を終えたら
  python tools/pickup_gate.py --verify      tmp/pickup0906/draft.md   # 反映前（apply_pickup が自動で呼ぶ）
  python tools/pickup_gate.py --show        tmp/pickup0906/draft.md
"""
import datetime
import hashlib
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KINDS = {"gap": "①取りこぼしチェック", "fact": "②ファクトチェック"}


def digest(draft):
    body = io.open(draft, encoding="utf-8").read().replace("\r\n", "\n")
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


def statepath(draft):
    return os.path.join(os.path.dirname(draft), "checked.json")


def load(draft):
    p = statepath(draft)
    if not os.path.exists(p):
        return {}
    try:
        return json.load(io.open(p, encoding="utf-8"))
    except Exception:
        return {}


def record(draft, kind, note=""):
    st = load(draft)
    st[kind] = {"hash": digest(draft),
                "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "note": note}
    json.dump(st, io.open(statepath(draft), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("記録した: %s / draft=%s" % (KINDS[kind], digest(draft)))


def verify(draft, quiet=False):
    st = load(draft)
    now = digest(draft)
    ng = []
    for kind, label in KINDS.items():
        rec = st.get(kind)
        if not rec:
            ng.append("%s を一度も通していない" % label)
        elif rec.get("hash") != now:
            ng.append("%s は**前の本文**に対するもの（記録 %s / いまの本文 %s）＝本文を書き直したので無効"
                      % (label, rec.get("hash"), now))
    if ng:
        print("=" * 64)
        print("🚨 記事を反映できません。①②は絶対条件です（2026-09-06 ユーザー明示）")
        for x in ng:
            print("   - %s" % x)
        print("")
        print("   ①取りこぼし＝その窓で発売が始まる分を全部並べて、載せるべき大物が漏れていないか見る")
        print("     例) python tmp/pickup_gap_0906.py")
        print("     終わったら: python tools/pickup_gate.py --record gap %s" % draft)
        print("   ②ファクトチェック＝独立エージェントに本文の事実記述を裏取りさせる")
        print("     終わったら: python tools/pickup_gate.py --record fact %s" % draft)
        print("=" * 64)
        return False
    if not quiet:
        for kind, label in KINDS.items():
            print("✅ %s 済み（%s）" % (label, st[kind]["at"]))
    return True


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        sys.exit(2)
    if a[0] == "--record":
        record(a[2], a[1], " ".join(a[3:]))
    elif a[0] == "--verify":
        sys.exit(0 if verify(a[1]) else 1)
    elif a[0] == "--show":
        print(json.dumps(load(a[1]), ensure_ascii=False, indent=1))
        print("いまの本文のハッシュ: %s" % digest(a[1]))
    else:
        print(__doc__)
        sys.exit(2)
