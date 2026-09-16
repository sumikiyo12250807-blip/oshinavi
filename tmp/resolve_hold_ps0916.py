# -*- coding: utf-8 -*-
"""発売前スイープの仕分けで「人が見る」になった11件を、前例と中身で決めて振り分け直す（2026-09-16 朝）。
  新規＝10765 辛島美登里・中西保志・中西圭三（合同公演・既存7846はソロ）／10772 さだまさし クリスマスディナー（ツアーとは別の催し）
        10776 SHERBETS 福岡（既存が会場ごとの別エントリ）／10782 ドリアン 1/9 かつしか（20周年ツアー10月とは別の公演・迷ったら畳まない）
        10820〜10822 アクトレスガールズ（既存が1大会1エントリ）
  畳む＝10781 鶴 福岡 → 1202（全国ツアー・9/15 と同じ）／10814 ソーゾーシー 東京 → 8704（同じ TOUR 2026）
  入れない＝10836（7944 とそっくり同じ枠）／10854（7858 とそっくり同じ枠）
使い方: python tmp/resolve_hold_ps0916.py
出力: tmp/merge_built_ps0916.json・tmp/merge_cands_ps0916.json・tmp/new_built_ps0916.json に足す（元は .bak に残す）
"""
import io
import json
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
NEW = [10765, 10772, 10776, 10782, 10820, 10821, 10822]
FOLD = {10781: 1202, 10814: 8704}
SKIP = [10836, 10854]

built = {b['id']: b for b in json.load(io.open('tmp/built_ps_0916.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_ps_0916.json', encoding='utf-8'))}
files = ['tmp/merge_built_ps0916.json', 'tmp/merge_cands_ps0916.json', 'tmp/new_built_ps0916.json']
for f in files:
    shutil.copyfile(f, f + '.bak')
mb, mc, nb = [json.load(io.open(f, encoding='utf-8')) for f in files]
# split_built は「部分一致」の6件（10765・10772・10782・10814・10836・10854）を最初から新規側に入れている
#   ＝新規側から「畳む・入れない」を外し、新規側に無い「複数一致」の分だけ足す
assert not (set(FOLD) | set(SKIP)) & ({x['id'] for x in mb} | {x['newid'] for x in mc}), '畳む側に混ざっている'
nb = [x for x in nb if x['id'] not in set(FOLD) | set(SKIP)]
in_new = {x['id'] for x in nb}
for i in NEW:
    if i not in in_new:
        nb.append(built[i])
for i, tgt in FOLD.items():
    mb.append(built[i])
    c = dict(cands[i])
    c['target'] = tgt
    mc.append(c)
for f, d in zip(files, (mb, mc, nb)):
    json.dump(d, io.open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('新規 %d件（計 %d）／畳む %d件（計 %d）／入れない %d件' % (len(NEW), len(nb), len(FOLD), len(mb), len(SKIP)))
