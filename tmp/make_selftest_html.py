# -*- coding: utf-8 -*-
"""照合スクリプトの陽性担保用。新着1件(4292)だけ genre:new のまま残し、
わざと ①千秋楽を1日ずらす ②締切を実在しない日にする ③県を別県にする
壊れたコピー tmp/index_selftest.html を作る。指摘が3つ出れば検出能力あり。
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
for e in E:
    if e.get('genre') == 'new' and e['id'] != 4292:
        e['genre'] = 'classic'      # 対象から外す（1件だけ叩く）
    if e['id'] == 4292:
        e['date'] = '2026-12-06'                 # ①千秋楽ズレ（実は12/5）
        e['prefecture'] = '大阪'                  # ③県ズレ（実は東京）
        e['tickets'][1]['date'] = '2026-09-30'   # ②実在しない締切（実は9/10発売）
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('tmp/index_selftest.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('tmp/index_selftest.html を作成（4292をわざと3か所壊した）')
