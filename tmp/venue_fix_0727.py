# -*- coding: utf-8 -*-
"""空カッコ会場3件(3272/3285/3286)の会場名を、ぴあ生HTMLから機械抽出する。
   WebFetchの要約は使わない（関連公演の会場を混ぜる恐れ＝memory: feedback_no_fake_info）。
"""
import sys, json, re
sys.path.insert(0, 'tools')
import build_pia_entries as B

TARGETS = {
    3272: 'https://t.pia.jp/pia/event/event.do?eventCd=2628891',
    3285: 'https://t.pia.jp/pia/event/event.do?eventCd=2629085',
    3286: 'https://t.pia.jp/pia/event/event.do?eventCd=2626459',
}
out = {}
for eid, url in TARGETS.items():
    h = B.fetch(url)
    cards = B.parse_cards(h)
    out[eid] = {
        'url': url,
        'cards': [{'state': c.get('state'), 'title': c.get('title'),
                   'venue': c.get('venue'), 'prefs': c.get('prefs'),
                   'perfdate': c.get('perfdate'), 'perf_end': c.get('perf_end'),
                   'when': c.get('when')} for c in cards],
    }
    # 会場名が生HTMLのどこにあるかも見る（パーサが拾えていない場所を特定するため）
    vs = re.findall(r'eventDetail-2024__place[^>]*>(.*?)<', h, re.S)
    out[eid]['place_raw'] = [re.sub(r'\s+', ' ', v).strip() for v in vs][:10]

with open('tmp/venue_fix.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('→ tmp/venue_fix.json')
