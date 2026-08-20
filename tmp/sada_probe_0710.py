# -*- coding: utf-8 -*-
"""さだまさし ぴあ bundle + アーティストページのeventCd を機械パース（調査のみ・投入しない）。"""
import sys, json, time
sys.path.insert(0, 'tools')
from build_pia_entries import build

URLS = [
    'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667141',
    'https://t.pia.jp/pia/event/event.do?eventCd=2548143',
    'https://t.pia.jp/pia/event/event.do?eventCd=2603976',
    'https://t.pia.jp/pia/event/event.do?eventCd=2616472',
    'https://t.pia.jp/pia/event/event.do?eventCd=2616473',
    'https://t.pia.jp/pia/event/event.do?eventCd=2618254',
    'https://t.pia.jp/pia/event/event.do?eventCd=2620025',
]
out = []
for n, url in enumerate(URLS):
    cand = {'newid': 90000 + n, 'artist': 'さだまさし', 'urls': [url]}
    try:
        ne = build(cand)
    except Exception as ex:
        print(f'ERROR {url} {str(ex)[:80]}'); time.sleep(1.5); continue
    if ne is None:
        print(f'買える枠ゼロ  {url}')
    else:
        print(f'>>> {ne.get("name","")}')
        print(f'    会場 {ne.get("venue","")} / 公演日 {ne.get("date")} / {ne.get("prefecture")}')
        for t in ne['tickets']:
            print(f'    {t.get("startDate")} -> {t.get("date")} | {t.get("type")}')
        out.append({'url': url, 'entry': ne})
    print()
    time.sleep(1.5)
json.dump(out, open('tmp/sada_probe_0710.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('=== 買える公演', len(out), '件 ===')
