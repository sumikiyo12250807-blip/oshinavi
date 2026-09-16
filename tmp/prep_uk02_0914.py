# -*- coding: utf-8 -*-
"""受付中・演劇の組み立て208件（tmp/built_uk02_0914.json）を「既存に畳む」「新規投入」「投入後に畳む」「外す」に分ける
（読むだけ・2026-09-14 朝／昼のpush用）。split_built_0914.py の結果と、相手の既存エントリの会期・県を見て決めた:
  畳む＝完全一致16件（どれも既存の会期の中かすぐ続き）＋桂宮治5件→1028（全国ツアー）＋
        劇団四季ロボット11月・12月→5181（月ごとに売り出す同じ演目）＋立川談春2件→3157（独演会2026）
  投入後に畳む＝立川小春志 芸歴二十周年記念落語会の7件＝8712 に 8713〜8718 を寄せる
      （既存1053 は名前が「in名古屋（第62回あきつ落語会）」＝そこへ畳むと会の名前が嘘になる）
  外す＝8686『TOUCH FIVE』（ぴあで「この公演は中止になりました」）
  保留＝8580・8581 キーウ・クラシック・バレエ（942 全国ツアーの一部かどうか確かめてから）
  新規＝残り全部（桂文珍 奈良・広島は既存が会場ごとの別エントリ＝同じ形で）
使い方: python tmp/prep_uk02_0914.py
出力: tmp/inject_uk02_0914.json ／ tmp/merge_uk02_built_0914.json ＋ tmp/merge_uk02_cands_0914.json ／
      tmp/merge_uk02b_built_0914.json ＋ tmp/merge_uk02b_cands_0914.json（投入後に畳む分）
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk02_0914.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk02_0914.json', encoding='utf-8'))}

MERGE = {
    8507: 3187, 8521: 987, 8523: 1008, 8587: 4625, 8593: 5181, 8600: 1103, 8601: 5185, 8602: 5977,
    8606: 2818, 8607: 5929, 8609: 484, 8637: 5933, 8641: 4836, 8662: 43, 8673: 2121, 8727: 4629,
    8556: 1028, 8557: 1028, 8558: 1028, 8559: 1028, 8560: 1028,   # 桂宮治 全国ツアー
    8594: 5181, 8595: 5181,                                        # 劇団四季ロボット 11月・12月
    8730: 3157, 8731: 3157,                                        # 立川談春 独演会2026
}
LATER = {i: 8712 for i in (8713, 8714, 8715, 8716, 8717, 8718)}   # 立川小春志 二十周年記念落語会
DROP = {8686}          # 中止
HOLD = {8580, 8581}    # キーウ・クラシック・バレエ

missing = [i for i in list(MERGE) + list(LATER) + list(DROP) + list(HOLD) if i not in built]
assert not missing, '組み立てに無い id を指している %s' % missing
new_ids = sorted(set(built) - set(MERGE) - set(LATER) - DROP - HOLD)
assert 8712 in new_ids, '寄せ先の 8712 が新規に入っていない'
inject = [built[i] for i in new_ids]
for path, data in (('tmp/inject_uk02_0914.json', inject),
                   ('tmp/merge_uk02_built_0914.json', [built[i] for i in MERGE]),
                   ('tmp/merge_uk02_cands_0914.json', [dict(cands[i], target=t) for i, t in MERGE.items()]),
                   ('tmp/merge_uk02b_built_0914.json', [built[i] for i in LATER]),
                   ('tmp/merge_uk02b_cands_0914.json', [dict(cands[i], target=t) for i, t in LATER.items()])):
    json.dump(data, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('組み立て %d件 ＝ 新規投入 %d / 既存に畳む %d / 投入後に畳む %d / 外す %d / 保留 %d' % (
    len(built), len(inject), len(MERGE), len(LATER), len(DROP), len(HOLD)))
print('新規のid範囲 %s〜%s' % (new_ids[0], new_ids[-1]))
