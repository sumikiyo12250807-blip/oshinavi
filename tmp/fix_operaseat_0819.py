# -*- coding: utf-8 -*-
"""統合ビルド(tmp/mergebuilt2_0819.json)の「オペラ座の怪人」名古屋3件で、
通常席と「ぴあスペシャルシートS1席」が同じ文言に潰れているのを書き分ける。
潰れたままだと統合の union キー（券種名＋締切）で1枠に畳まれて、スペシャルシートの売り場が消える
（[[feedback_pia_parser_flattens_slots]] / [[feedback_dedup_badges_keeps_urls]]）。
席種名はぴあ実ページの <title> から取ったもの。
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

SEAT = {'2633222': 'ぴあスペシャルシートS1席',
        '2633227': 'ぴあスペシャルシートS1席',
        '2633229': 'ぴあスペシャルシートS1席'}

data = json.load(open('tmp/mergebuilt2_0819.json', encoding='utf-8'))
n = 0
for e in data:
    for t in e.get('tickets') or []:
        m = re.search(r'eventCd=(\w+)', t.get('url') or '')
        seat = SEAT.get(m.group(1)) if m else None
        if not seat or '【' in t['type']:
            continue
        t['type'] = re.sub(r'^(一般発売|先行|プリセール|プレリザーブ[^（]*)', r'\1【%s】' % seat, t['type'], count=1)
        n += 1
        print('id=%d → %s' % (e['id'], t['type']))
json.dump(data, open('tmp/mergebuilt2_0819.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('=== %d枠に席種を入れた ===' % n)
