# -*- coding: utf-8 -*-
"""今夜組む新規候補（tmp/cands_uk01new_0915.json）を45件ずつに分けて、順番に build_pia_entries で組む（2026-09-15 夜）
・ぴあを叩きすぎると混雑ページ（sorry.pia）で「静かな0」になる＝1つ組むごとに60秒休む（memory reference_pia_rate_limit_429）
・build_pia_entries は取りこぼし（買えるのに解析できなかったカード）があると終了コード3で止まる＝その塊の番号を報告する
・出力＝tmp/built_uk01new_<n>_0915.json（塊ごと）＋ tmp/built_uk01new_0915.json（全部をつないだもの）＋ .log
使い方: python build_chunks_0915.py
"""
import io
import json
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
CH, REST = 45, 60
cands = json.load(io.open('tmp/cands_uk01new_0915.json', encoding='utf-8'))
chunks = [cands[i:i + CH] for i in range(0, len(cands), CH)]
allb, report = [], []
for n, ch in enumerate(chunks, 1):
    cj = 'tmp/cands_uk01new_%d_0915.json' % n
    bj = 'tmp/built_uk01new_%d_0915.json' % n
    lg = 'tmp/built_uk01new_%d_0915.log' % n
    json.dump(ch, io.open(cj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with io.open(bj, 'w', encoding='utf-8') as fo, io.open(lg, 'w', encoding='utf-8') as fe:
        r = subprocess.run([sys.executable, 'tools/build_pia_entries.py', cj], stdout=fo, stderr=fe)
    try:
        b = json.load(io.open(bj, encoding='utf-8'))
    except Exception as ex:
        b = []
        report.append('塊%d: 出力を読めない（%s）' % (n, str(ex)[:60]))
    allb += b
    report.append('塊%d: 候補 %d件 → 組めた %d件 ／終了コード %d（3＝取りこぼしあり・ログ %s）' % (n, len(ch), len(b), r.returncode, lg))
    print(report[-1], flush=True)
    if n < len(chunks):
        time.sleep(REST)
json.dump(allb, io.open('tmp/built_uk01new_0915.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('全部で %d件 → tmp/built_uk01new_0915.json' % len(allb))
