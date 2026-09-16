# -*- coding: utf-8 -*-
"""総ざらい（完全版）の候補から「本当の抜け」だけを候補jsonにする（2026-09-16 夜）。

決め手は県＋公演日。売り場番号（eventCd）は使えない＝ぴあは同じ窓を別URLでも出すので、
番号が無いだけで「未登録」と言うと二重登録になる（PENTAGON 大阪10/1・サントリーホールのクリスマス 12/25 で実証）。

KEEP = 県＋公演日で登録側に窓が無いと確かめた売り場番号だけを手で並べたもの。
出力: tmp/x0917/cands2.json（build_pia_entries.py に渡す形）
使い方: python tmp/x0917/cands2_build.py
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 県＋公演日で登録に無いと確かめた候補（除外の理由はコミットメッセージと plan.md に書く）
KEEP = {
    'b2671079': ('Juice=Juice', '01'),
    '2634612': ('アンジュルム', '01'),
    '2634700': ('カキンツハルカ', '01'),
    '2626446': ('佐野元春&THE COYOTE BAND', '01'),
    '2616872': ('務川慧悟（p）', '07'),
    '2619189': ('務川慧悟（p）', '07'),
    '2615447': ('岩崎宏美', '01'),
    '2617419': ('柳亭小痴楽 全国ツアー カチコミ’26', '06'),
    '2623973': ('柳亭小痴楽 瀧川鯉八 二人会', '06'),
    '2626852': ('沢田研二', '01'),
    '2624029': ('沢田研二', '01'),
    '2625711': ('沢田研二', '01'),
    '2624031': ('沢田研二', '01'),
    'b2667819': ('イルカ', '01'),
    '2613573': ('イルカ', '01'),
    'b2669868': ('ザ・キングズ・シンガーズ', '07'),
    '2635787': ('中川晃教', '01'),
    'b2670116': ('佐野元春&THE COYOTE BAND', '01'),
    'b2671003': ('原田真二', '01'),
    '2633316': ('春風亭一之輔独演会', '06'),
    'b2670634': ('柳家花緑独演会', '06'),
    'b2666785': ('森山直太朗', '01'),
    '2629913': ('神はサイコロを振らない', '01'),
    '2617499': ('名曲コンサート', '07'),
    'b2670997': ('名曲コンサート', '07'),
    '2626312': ('名曲コンサート', '07'),
    '2618160': ('名曲コンサート', '07'),
    '2539932': ('名曲コンサート', '07'),
    '2612178': ('名曲コンサート', '07'),
}

src = io.open('index.html', encoding='utf-8').read()
events = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
maxid = max(e['id'] for e in events)
try:
    lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))
    for r in (lb if isinstance(lb, list) else lb.get('batches', [])):
        for k in ('id_to', 'idTo', 'to'):
            if isinstance(r, dict) and isinstance(r.get(k), int):
                maxid = max(maxid, r[k])
except Exception as ex:
    print('last_batch.json は読めなかった（index の最大idを使う）: %s' % ex)

out = []
nid = maxid
for cd, (artist, lg) in KEEP.items():
    nid += 1
    key = 'eventBundleCd' if cd.startswith('b') else 'eventCd'
    out.append({'newid': nid, 'artist': artist, '_lg': lg,
                'urls': ['https://ticket.pia.jp/pia/event.do?%s=%s' % (key, cd)]})

io.open('tmp/x0917/cands2.json', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('候補 %d 件 / id %d〜%d（index の最大id %d の次から）' % (len(out), out[0]['newid'], out[-1]['newid'], maxid))
for r in out:
    print('  %d %-28s %s' % (r['newid'], r['artist'][:28], r['urls'][0].split('?')[1]))
