# -*- coding: utf-8 -*-
"""2回目の新着候補(tmp/built2_0819.json)のうち、既存エントリと同じ興行だったものを統合する準備。

判定の内訳：
 ・今朝も同じ相手に統合した10件（同じアーティストの別公演。ぴあが別eventCdで持っているだけ）
 ・4714 牛田智大室内楽プロジェクトVol.4 → 既存1835 と同一プログラムの巡回公演（検証エージェント）
 ・4718 東京フィル「第九」特別演奏会 → 既存4293 と指揮・独唱・合唱まで同一の会場違い。
   さらに **12/19 サントリーホール(2626567) が登録から漏れている**ので、そのURLも足して拾う
別の興行として単独で投入するもの＝4701 桂文珍／4713 アンセットシス／4724 仙台フィル／4732 大阪フィル
（いずれも主催・指揮者・プログラムが別。楽団名がそのまま公演名になる型は1回1回が独立した興行）
"""
import re, json, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

# 新id -> (統合先の既存id, 追加で足したいURL)
MERGE = {
    4691: (1149, []), 4692: (3035, []), 4693: (3526, []), 4694: (2500, []),
    4695: (3040, []), 4696: (1203, []), 4697: (4189, []), 4698: (4249, []),
    4699: (3501, []), 4703: (3755, []),
    4714: (1835, []),
    4718: (4293, ['https://t.pia.jp/pia/event/event.do?eventCd=2626567']),
}

built = {e['id']: e for e in json.load(open('tmp/built2_0819.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
EVENTS = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}


def urls_of(e):
    out = []
    u = (e.get('links') or {}).get('pia')
    if u:
        out.append(u)
    for t in (e.get('tickets') or []):
        if t.get('url') and 't.pia.jp' in t['url']:
            out.append(t['url'])
    return out


cand, drop, merged = [], {}, []
for nid, (keep_id, extra) in sorted(MERGE.items()):
    keep = EVENTS.get(keep_id)
    b = built.get(nid)
    if not keep or not b:
        print('!! id %d / %d が見つからない' % (nid, keep_id))
        sys.exit(1)
    urls = urls_of(keep) + urls_of(b) + extra
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u); uniq.append(u)
    cand.append({'newid': keep_id, 'artist': keep.get('artist') or keep['name'], 'urls': uniq})
    merged.append(nid)
    print('%d %s ← 新%d %s ／ URL %d本%s'
          % (keep_id, (keep.get('artist') or '')[:26], nid, b['name'][:26], len(uniq),
             ' ＋漏れ枠1本' if extra else ''))

json.dump(cand, open('tmp/mergecand3_0819.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump({}, open('tmp/mergedrop3_0819.json', 'w', encoding='utf-8'))
json.dump(sorted(merged), open('tmp/merged_newids2_0819.json', 'w', encoding='utf-8'))
print('=== 統合先 %d件 / 投入から外す新候補 %d件 ===' % (len(cand), len(merged)))
