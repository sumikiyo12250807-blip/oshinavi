# -*- coding: utf-8 -*-
"""9/14朝の新着（組み立て43件）を「新規投入」「既存に畳む」「投入後に畳む」の3つのファイルに分ける（読むだけ）。
決め方（split_built_0914.py の結果を1件ずつ見て決めた）:
  畳む＝正規化名が完全一致で、既存ツアーの会期の中かすぐ続き／同じ試合の二重／同じツアーの部分一致
  新規＝既存の会期の外（TSUKEMEN 2027年2月・jizue 2027年2月＝9/11 のTSUKEMEN保留と同じ判断）／
        既存が会場ごとの別エントリ（SHERBETS）／題名つきの別公演（日食なつこ横須賀）／別の会（玉川太福）
  投入後に畳む＝TK from 凛として時雨 の2件（8406 → 8405）
使い方: python tmp/prep_inject_0914.py
出力: tmp/inject_0914.json ／ tmp/merge_built2_0914.json ＋ tmp/merge_cands2_0914.json ／
      tmp/merge_tk_built_0914.json ＋ tmp/merge_tk_cands_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_presale_0914.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_presale_0914.json', encoding='utf-8'))}

MERGE = {  # 新着id → 畳む先の既存id
    8398: 3892,  # 夜の本気ダンス 京都11/21（既存は〜2/27の全国ツアー）
    8399: 5155,  # きゃりーぱみゅぱみゅ 北海道5/15（既存は〜6/12）
    8400: 549,   # 坂本冬美 佐賀・長崎1/18〜19（既存は〜1/11）
    8401: 7326,  # 35.7 広島11/21
    8402: 7326,  # 35.7 香川12/5
    8417: 8333,  # コンサドーレ×岡山 ルヴァン 9/29＝同じ試合
    8418: 8335,  # コンサドーレ×秋田 J2 10/17＝同じ試合
    8429: 727,   # 西村由紀江 12/12＝同じツアー（12/4〜12/24）
    8407: 5332,  # 人間椅子 北海道11/11＝愛知・宮城をまとめてある 5332 へ
}
LATER = {8406: 8405}  # TK from 凛として時雨 福岡 → 広島（投入後に畳む）

inject = [b for i, b in sorted(built.items()) if i not in MERGE and i not in LATER]
mb = [built[i] for i in MERGE]
mc = [dict(cands[i], target=t) for i, t in MERGE.items()]
lb = [built[i] for i in LATER]
lc = [dict(cands[i], target=t) for i, t in LATER.items()]
for path, data in (('tmp/inject_0914.json', inject), ('tmp/merge_built2_0914.json', mb),
                   ('tmp/merge_cands2_0914.json', mc), ('tmp/merge_tk_built_0914.json', lb),
                   ('tmp/merge_tk_cands_0914.json', lc)):
    json.dump(data, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('新規投入 %d件 / 既存に畳む %d件 / 投入後に畳む %d件 ＝ 計 %d（組み立て %d）' % (
    len(inject), len(mb), len(lb), len(inject) + len(mb) + len(lb), len(built)))
print('新規のid: %s' % ','.join(str(b['id']) for b in inject))
