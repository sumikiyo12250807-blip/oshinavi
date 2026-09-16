# -*- coding: utf-8 -*-
"""音楽・受付中の組み上がり（tmp/built_uk01_0915.json）の残り＝「新規」と「追加で畳む分」を分ける（読むだけ・2026-09-15）。
既存と名前が完全一致1件の169件は merge_with_urls_0912.py で畳み済み（commit 済み）。ここはその残り。

決めたこと（split_built_0915.txt・partial_compare_0915.txt・multi_match_plan_0915.txt を見て）:
  部分一致8件
    入れない（二重）＝9906 大江千里トリオ（4741 に同じ枠）／10331 琉球フェス（1253 と同じ枠）／
                     10409 ボロフェスタ（6251 に今朝足した4枠と同じ）／10420 New Acoustic Camp 宝川温泉ツアー（6481 に同じ枠）
    畳む＝9976 SHOW-WA 武道館 → 3235（楽天だけのエントリにぴあ）／10370 ザ・ゴールデンステージ長崎 → 6983（e+だけにぴあ）
    新規＝9963 澤田知可子 東京10/17（5202 は兵庫の別の会）／9979 CiON's Love Call（3421 は別のツアー）
  複数一致53件
    A 畳む10件＝会期の中に入る既存が1つだけ（multi_match_plan_0915.txt の行き先）
    B 新規14件＝既存が全部1会場のエントリで会期の外
    C のうち 新規19件＝既存の会期の外（9/14 の jizue・TSUKEMEN と同じ判断）
    C のうち 畳む2件＝福田こうへい 9/19・9/25 → 734 全国ツアー（9/26開始の直前）
    C のうち 保留8件＝会期に入るツアーが2つ（SHE'S 9980・10101・10217／スタレビ 9992・10145／半崎美子 10226／福田こうへい 10376）・鶴 10195
使い方: python tmp/prep_uk01_0915.py
出力: tmp/merge2_uk01_built_0915.json ＋ tmp/merge2_uk01_cands_0915.json ／ tmp/inject_uk01_0915.json ／ tmp/hold_uk01_0915.txt
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk01_0915.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk01_0915.json', encoding='utf-8'))}
merged_already = {c['newid'] for c in json.load(io.open('tmp/merge_cands_0915.json', encoding='utf-8'))}
split = io.open('tmp/split_built_0915.txt', encoding='utf-8').read()
plan = io.open('tmp/multi_match_plan_0915.txt', encoding='utf-8').read()

SKIP_DUP = {9906, 10331, 10409, 10420}
MERGE = {9976: 3235, 10370: 6983, 10373: 734, 10374: 734}
NEW_PARTIAL = {9963, 9979}
HOLD = {9980, 10101, 10217, 9992, 10145, 10226, 10376, 10195}

# A＝会期の中の既存1つへ畳む（行き先は plan の「→ idNNN に畳む」）
for m in re.finditer(r'^A new(\d+).*?→ id(\d+) に畳む', plan, re.M):
    MERGE[int(m.group(1))] = int(m.group(2))
B = {int(x) for x in re.search(r'^B=(.*)$', plan, re.M).group(1).split(',') if x}
C = {int(x) for x in re.search(r'^C=(.*)$', plan, re.M).group(1).split(',') if x}
C_NEW = C - HOLD - set(MERGE)
pure_new = {int(m.group(1)) for m in re.finditer(r'^新規\s+new(\d+)', split, re.M)}

NEW = pure_new | NEW_PARTIAL | B | C_NEW
decided = merged_already | SKIP_DUP | set(MERGE) | NEW | HOLD
left = set(built) - decided
assert not left, '行き先の決まっていない組み上がりがある %s' % sorted(left)
assert not (NEW & set(MERGE)) and not (NEW & HOLD) and not (NEW & SKIP_DUP), '重なり'

mb = [built[i] for i in sorted(MERGE)]
mc = [dict(cands[i], target=t) for i, t in sorted(MERGE.items())]
inject = [built[i] for i in sorted(NEW)]
json.dump(mb, io.open('tmp/merge2_uk01_built_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(mc, io.open('tmp/merge2_uk01_cands_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(inject, io.open('tmp/inject_uk01_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
io.open('tmp/hold_uk01_0915.txt', 'w', encoding='utf-8').write(','.join(str(i) for i in sorted(HOLD)) + '\n')
print('組み上がり %d ＝ 畳み済み %d ／ 追加で畳む %d ／ 新規 %d（名前なし %d・部分 %d・B %d・C %d）／ 保留 %d ／ 二重で入れない %d' % (
    len(built), len(merged_already), len(MERGE), len(NEW), len(pure_new), len(NEW_PARTIAL), len(B), len(C_NEW), len(HOLD), len(SKIP_DUP)))
print('追加で畳む: ' + ' '.join('%s→%s' % kv for kv in sorted(MERGE.items())))
