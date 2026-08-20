# -*- coding: utf-8 -*-
"""投入するものと、既存へ回すものを仕分ける。

 DROP  ＝ 既存エントリと枠まで同じ（＝ぴあの別入口を拾っただけ）。投入しない。
 MERGE ＝ 同じ興行の別会場・別日程。既存へ枠を足す/差し替える（tmp/merge_0820.py で処理）。
 残り  ＝ 新規として新着プールへ投入。
"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')

DROP = {
    4742: '3129 Pearl Drums と枠3つ完全一致',
    4743: '1149 いぎなり東北産に含まれる（既存の方が枠が多い）',
    4748: '3035 7ORDER に含まれる（既存はe+枠も持つ）',
    4750: '2500 ドラクエ ウインドオーケストラに含まれる',
    4752: '3040 山崎ハコに含まれる（既存はe+枠も持つ）※piaURLだけ既存へ補完',
    4753: '1203 徳永ゆうき と枠4つ完全一致',
    4759: '4189 扇辰・喬太郎の会 と枠2つ完全一致',
    4763: '4249 メイビー、ハッピーエンディング と枠3つ完全一致',
    4764: '3501 ワハハ本舗「エンド(仮)」と枠6つ完全一致',
    4773: '1835 牛田智大 室内楽Vol.4 に含まれる',
    4777: '3775 コバケンとその仲間たち Vol.7 と枠2つ完全一致',
}
MERGE = {
    4740: '850 横山だいすけ＝既存は愛知9/3のみ。ツアー全体（山梨・北海道・宮城）に置き換える',
    4749: '3526 dustbox＝同じ2Daysだが eventCd が別（2629991/2629992）＝別の売り場なので枠を足す',
    4751: '738 フラワーカンパニーズ＝同じツアーの栃木12/5を足す',
    4755: '950 天満天神繁昌亭＝同じ寄席の11/18公演を足す',
    4758: '1028 桂宮治 全国ツアー＝東京R9年1/30公演を足す',
}

built = json.load(io.open('tmp/built_0820.json', encoding='utf-8'))
keep = [e for e in built if e['id'] not in DROP and e['id'] not in MERGE]
io.open('tmp/inject_0820.json', 'w', encoding='utf-8').write(
    json.dumps(keep, ensure_ascii=False, indent=1))

print('=== build %d件 → 投入 %d件 / 捨てる %d件 / 既存へ統合 %d件 ===' % (
    len(built), len(keep), len(DROP), len(MERGE)))
for i, why in sorted(DROP.items()):
    print('  捨てる %d  %s' % (i, why))
for i, why in sorted(MERGE.items()):
    print('  統合   %d  %s' % (i, why))
