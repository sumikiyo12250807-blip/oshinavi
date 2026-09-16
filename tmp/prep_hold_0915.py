# -*- coding: utf-8 -*-
"""音楽・受付中の保留8件（tmp/hold_uk01_0915.txt）の行き先を決めて分ける（読むだけ・2026-09-15 昼）。
hold_compare_0915.txt を見て決めた:
  新規7＝既存も「ぴあのページごとに1エントリ」に割れている＝同じ形で。どのツアーに入るか決め手が無いのに畳むと別のツアーに混ざる
    9980 SHE'S 長野 JUNK BOX 11/23／10101 SHE'S 石川 REDSUN 11/22／10217 SHE'S 愛媛・香川 10/30〜31
    9992 スターダスト☆レビュー 埼玉 くまがやドーム 10/10／10145 スターダスト☆レビュー 三重 10/4
    10226 半崎美子 愛媛・高知 10/3〜10/25／10376 福田こうへい 秋田 11/29
  畳む1＝10195 鶴 → 1202（米子laughs・松江canova・広島Cave-Be の 10/31〜11/3 が両方にある＝同じツアーの前半）。
        重なる枠は merge_with_urls が「骨格が既存にある枠は触らない」で二重に足さない
使い方: python tmp/prep_hold_0915.py
出力: tmp/merge3_hold_built_0915.json ＋ tmp/merge3_hold_cands_0915.json ／ tmp/inject_hold_0915.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk01_0915.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk01_0915.json', encoding='utf-8'))}
hold = {int(x) for x in io.open('tmp/hold_uk01_0915.txt', encoding='utf-8').read().split(',') if x.strip()}
MERGE = {10195: 1202}
NEW = {9980, 10101, 10217, 9992, 10145, 10226, 10376}
assert hold == set(MERGE) | NEW, '保留の一覧と決めた行き先が合わない %s' % sorted(hold ^ (set(MERGE) | NEW))
json.dump([built[i] for i in sorted(MERGE)], io.open('tmp/merge3_hold_built_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([dict(cands[i], target=t) for i, t in sorted(MERGE.items())], io.open('tmp/merge3_hold_cands_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([built[i] for i in sorted(NEW)], io.open('tmp/inject_hold_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('保留 %d ＝ 畳む %d ／ 新規 %d' % (len(hold), len(MERGE), len(NEW)))
