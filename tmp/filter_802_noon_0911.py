# -*- coding: utf-8 -*-
"""昼のヒールのブロック分のうち id802 山崎育三郎だけ、当てる枠を絞る（2026-09-11）。
既存は「一般発売（山形 9/26公演・福島 9/27公演）」のように2公演まとめた枠で、
ビルドは1公演ずつに割って返す＝そのまま足すと同じ販売窓が二重に出る。
→ 802 は「当日引換券販売（兵庫 9/13公演）」の締切差し替えと、既存に無い新しい窓
  「一般発売.（岡山 9/12公演）〜9/11」だけにする。"""
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
P = 'tmp/blocked_built_noon_0911.json'
d = json.load(io.open(P, encoding='utf-8'))
for b in d:
    if b['id'] == 802:
        keep = [t for t in b['tickets'] if t['type'].startswith('当日引換券販売（兵庫 9/13公演）') or t['type'].startswith('一般発売.（岡山 9/12公演）')]
        print('802: %d枠 → %d枠' % (len(b['tickets']), len(keep)))
        for t in keep:
            print('   ', t['type'])
        b['tickets'] = keep
json.dump(d, io.open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
