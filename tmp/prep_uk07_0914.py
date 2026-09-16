# -*- coding: utf-8 -*-
"""受付中・クラシックの組み立て338件（tmp/built_uk07_0914.json）を「既存に畳む」「新規投入」に分ける（読むだけ・2026-09-14）。
split_built_0914.py の結果と、畳み先の会期・県を見て決めた:
  畳む＝同じツアーで会期の中かすぐ近く（秋川雅史・ガヴリリュク・カントロフ・Quartet Explloce×2・ケヴィン・チェン×2・
        アヴデーエワ・阪田知樹・佐渡裕シエナ・ジブリの思い出×2・牛田智大 Vol.4・仙台クラシックフェス×2）
        ※ガヴリリュク・阪田知樹・仙台フェスは同じ枠が既にある＝merge_with_urls は骨格が同じ枠を足さないので害は無い
  新規＝残り全部。オーケストラは既存が「1公演＝1エントリ」（project_pia_presale_caught_up）＝部分一致でも畳まない
        （大阪フィル定期6・特別演奏会2・NHK交響楽団・群馬交響楽団・Osaka Shion×4・仙台フィル第九）。
        五十嵐紅・石田組・しいきアルゲリッチハウス・ケヴィン・チェン in MIYAZAKI は既存が会場ごとの別エントリ。
        「0歳からのコンサート」北海道10/31 は既存6351（静岡12/13）と地域も主催も違う＝畳まない。
🚨この組み立ては「中止」を弾く直し（9ab9925a）の前に走った＝投入後に reconcile --new で中止の枠が紛れていないか見る。
使い方: python tmp/prep_uk07_0914.py
出力: tmp/inject_uk07_0914.json ／ tmp/merge_uk07_built_0914.json ＋ tmp/merge_uk07_cands_0914.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
built = {b['id']: b for b in json.load(io.open('tmp/built_uk07_0914.json', encoding='utf-8'))}
cands = {c['newid']: c for c in json.load(io.open('tmp/cands_uk07_0914.json', encoding='utf-8'))}
MERGE = {
    9478: 2471, 9500: 29, 9503: 1716, 9682: 1942, 9683: 1942, 9699: 92, 9701: 92, 9719: 4927,
    9740: 28, 9753: 2104, 9811: 2494, 9812: 2494, 9542: 1835, 9844: 1947, 9845: 1947,
}
missing = [i for i in MERGE if i not in built]
assert not missing, '組み立てに無い id を指している %s' % missing
new_ids = sorted(set(built) - set(MERGE))
json.dump([built[i] for i in new_ids], io.open('tmp/inject_uk07_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([built[i] for i in MERGE], io.open('tmp/merge_uk07_built_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump([dict(cands[i], target=t) for i, t in MERGE.items()],
          io.open('tmp/merge_uk07_cands_0914.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('組み立て %d件 ＝ 新規投入 %d / 既存に畳む %d' % (len(built), len(new_ids), len(MERGE)))
print('新規のid範囲 %s〜%s' % (new_ids[0], new_ids[-1]))
