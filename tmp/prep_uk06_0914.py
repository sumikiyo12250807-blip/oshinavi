# -*- coding: utf-8 -*-
"""受付中・イベントの組み立て354件（tmp/built_uk06_0914.json）を「既存に畳む」「新規投入」「投入後に畳む」に分ける
（読むだけ・2026-09-14）。split_built_0914.py の結果と、相手の既存エントリの名前・会期を見て決めた:
  畳む＝完全一致4（落合博満→8359・俺だけレベルアップな件 展→51・Kobe Calling→3862・神戸モンキーズ劇場→7139）
        ＋同じ展覧会の券違い3（俺だけレベルアップ展 スーパーパス／土日祝／平日→51）
        ＋ケロポンズ in 加茂→2384（8/23 にも 2384 に畳んだ前例）
        ＋名探偵プリキュア ドリームステージ 郡山→450（450 がその全国ツアー）
        ＋松崎しげる クリスマスディナーショー→742（8/24 にディナーショーの枠を 742 で持った前例）
  投入後に畳む＝サンリオピューロランド パスポート 3件＝9225 に 9226・9227 を寄せる
  新規＝残り全部（でんじろう Part2＝題名が別／郷ひろみ ディナーショー＝ツアー 397 とは別の催し／エビ中・宮本佳林のお渡し会＝別の催し）
使い方: python tmp/prep_uk06_0914.py
出力: tmp/inject_uk06_0914.json ／ tmp/merge_uk06_built_0914.json ＋ tmp/merge_uk06_cands_0914.json ／
      tmp/merge_uk06b_built_0914.json ＋ tmp/merge_uk06b_cands_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk06_0914.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk06_0914.json', encoding='utf-8'))}
MERGE = {
    9164: 8359, 9165: 51, 9166: 51, 9167: 51, 9168: 51,
    9204: 2384, 9206: 3862, 9207: 7139, 9426: 450, 9415: 742,
}
LATER = {9226: 9225, 9227: 9225}
missing = [i for i in list(MERGE) + list(LATER) + [9225] if i not in built]
assert not missing, '組み立てに無い id を指している %s' % missing
new_ids = sorted(set(built) - set(MERGE) - set(LATER))
for path, data in (('tmp/inject_uk06_0914.json', [built[i] for i in new_ids]),
                   ('tmp/merge_uk06_built_0914.json', [built[i] for i in MERGE]),
                   ('tmp/merge_uk06_cands_0914.json', [dict(cands[i], target=t) for i, t in MERGE.items()]),
                   ('tmp/merge_uk06b_built_0914.json', [built[i] for i in LATER]),
                   ('tmp/merge_uk06b_cands_0914.json', [dict(cands[i], target=t) for i, t in LATER.items()])):
    json.dump(data, io.open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('組み立て %d件 ＝ 新規投入 %d / 既存に畳む %d / 投入後に畳む %d' % (len(built), len(new_ids), len(MERGE), len(LATER)))
print('新規のid範囲 %s〜%s' % (new_ids[0], new_ids[-1]))
