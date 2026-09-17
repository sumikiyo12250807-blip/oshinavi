# -*- coding: utf-8 -*-
"""発売前スイープ 9/17 の「人が見る」20件を前例と中身で決める（2026-09-17 朝）。見比べ＝tmp/hold_compare_ps0917.txt
  畳む＝11067 syrup16g 福岡11/18 → 5526（会期11/1〜12/9の中・9/15 長野と同じ）
        11113 新日本プロレス 赤磐（ぴあ） → 10762（ローチケだけの同じ大会・8021 未唯mie→6239 と同じ＝ぴあの枠を足す）
        11135・11136 クーザ 3月・4月 → 3674（3674 にぴあの「一般発売【月別】9/19発売」が無い＝足りない枠だけ入る）
  新規＝11068・11069 SCANDAL（既存がぴあの売り場ごとの別エントリ・会期の外）／11073・11074 NEWS（NEWSTAR とは別）
        11085 忘れらんねえよ 広島（既存が会場ごと）／11093 キーウ 春日井（4638 東海と同じ形の単独公演・迷ったら畳まない）
        11111・11112 新日本プロレス 後楽園（1大会1エントリ）／11116〜11120 天皇杯 3回戦 5会場（7933 は 9/23 の別の回戦）
  入れない＝11081 宮田まゆみ（7858 とそっくり同じ2枠）／11126 リポビタンD（7790 とそっくり同じ2枠）
  保留＝11121 天皇杯 アイスタ＜駐車券＞（コンサドーレの駐車券だけのページと同じ問い＝ユーザーに聞いている）
"""
import io, json, shutil, sys
sys.stdout.reconfigure(encoding='utf-8')
NEW = [11068, 11069, 11073, 11074, 11085, 11093, 11111, 11112, 11116, 11117, 11118, 11119, 11120]
FOLD = {11067: 5526, 11113: 10762, 11135: 3674, 11136: 3674}
SKIP = [11081, 11126]
HOLD = [11121]
built = {b['id']: b for b in json.load(io.open('tmp/built_ps_0917.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_ps_0917.json', encoding='utf-8'))}
files = ['tmp/merge_built_ps0917.json', 'tmp/merge_cands_ps0917.json', 'tmp/new_built_ps0917.json']
for f in files:
    shutil.copyfile(f, f + '.bak')
mb, mc, nb = [json.load(io.open(f, encoding='utf-8')) for f in files]
decided = set(NEW) | set(FOLD) | set(SKIP) | set(HOLD)
assert not decided & ({x['id'] for x in mb} | {x['newid'] for x in mc}), '畳む側に混ざっている'
nb = [x for x in nb if x['id'] not in set(FOLD) | set(SKIP) | set(HOLD)]
in_new = {x['id'] for x in nb}
for i in NEW:
    if i not in in_new:
        nb.append(built[i])
for i, tgt in FOLD.items():
    mb.append(built[i])
    c = dict(cands[i]); c['target'] = tgt
    mc.append(c)
for f, d in zip(files, (mb, mc, nb)):
    json.dump(d, io.open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('新規 %d件 ／ 畳む %d件 ／ 入れない %d件 ／ 保留 %d件' % (len(nb), len(mb), len(SKIP), len(HOLD)))
