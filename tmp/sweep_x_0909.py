# -*- coding: utf-8 -*-
"""【夜の便8】X投稿に出した公演を、ぴあで"アーティスト名"検索して総ざらいする。

なぜ＝X投稿の誘導先は oshinavi.jp。着地したページに枠が欠けていたら、
      わざわざ来た人が自分の推しを見つけられない（.claude/skills/day/SKILL.md 第4便8）。
🚨ツアーまとめ(bundle)ページだけ見ない＝そこに出てこない公演がある
  （feedback_pia_bundle_hides_shows）。だからキーワード検索で引き直す。

道具は tools/pia_missing_audit.py を **キーワードだけ差し替えて** 再利用する
（feedback_check_existing_logic＝スクリプトを書く前に既存ロジックを見る）。
"""
import io
import json
import os
import sys
import importlib.util

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_spec = importlib.util.spec_from_file_location(
    "pma", os.path.join(ROOT, "tools", "pia_missing_audit.py"))
pma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pma)

# 投稿の本文から抜いた名前を、ぴあの検索語として使える形に直したもの。
# 券種違いの重複（〈ワイドシート〉〈3階見切れ席〉）と回数表記は落とす。
KWS = [
    "モーニング娘。",
    "矢野顕子",
    "宇都宮隆",
    "C&K",
    "こおり健太",
    "二見颯一",
    "ブギ連",
    "前橋汀子",
    "中部フィルハーモニー交響楽団",
    "山形交響楽団",
    "牧阿佐美バレヱ団",
    "角野未来",
    "東京シティ・フィルハーモニック管弦楽団",
    "千葉ロッテマリーンズ",
    "新日本プロレス",
    "レイラック滋賀FC",
    "天満天神繁昌亭",
    "桂吉弥",
    "柳家喬太郎",
    "立川談笑",
    "三山ひろし",
    "松原健之",
    "市川團十郎",
    "KAGAYA",
    "カイ・フランク",
]

OUT = os.path.join(ROOT, "tmp", "sweep_x_0909.txt")
STATE = os.path.join(ROOT, "tmp", "sweep_x_0909_state.json")


def main():
    evs = pma.load_events()
    reg = pma.registered_cds(evs)
    excl = pma.load_excluded()
    print("登録済みエントリ %d件 / 登録済みぴあコード %d件 / 除外 %d件"
          % (len(evs), len(reg), len(excl)))
    print("引くキーワード %d件" % len(KWS))

    prior = None
    if os.path.exists(STATE):
        prior = json.load(io.open(STATE, encoding="utf-8"))

    res = pma.audit(KWS, reg, excl, 5.0, STATE, OUT, prior=prior)

    hot = {k: v for k, v in res.items() if v["missing"]}
    own = sum(len([m for m in v["missing"] if m["own_name"]]) for v in hot.values())
    other = sum(len([m for m in v["missing"] if not m["own_name"]]) for v in hot.values())
    print("引き終わり %d/%d ／ 未登録の候補 本人名義 %d件・別名義 %d件"
          % (len(res), len(KWS), own, other))
    print("報告書 -> %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
