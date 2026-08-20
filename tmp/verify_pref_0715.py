#!/usr/bin/env python3
"""県誤検出4件をぴあ実ページの __region で裏取り（推測しない）"""
import sys
sys.path.insert(0, 'tools')
import build_pia_entries as bpe   # import時にstdoutをUTF-8ラップ

TARGETS = {
    1097: 'https://t.pia.jp/pia/event/event.do?eventCd=2617427',
    2134: 'https://t.pia.jp/pia/event/event.do?eventCd=2623365',
    2300: 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667295',
    2338: 'https://t.pia.jp/pia/event/event.do?eventCd=2623354',
}

for i, url in TARGETS.items():
    try:
        h = bpe.fetch(url)
    except Exception as ex:
        print(f'id={i} 取得失敗 {ex}')
        continue
    rows = bpe.parse_cards(h)
    print(f'\nid={i} {url}')
    seen = set()
    for r in rows:
        key = (r['perfdate'], r['venue'], tuple(r['prefs']), r['state'])
        if key in seen:
            continue
        seen.add(key)
        print(f"   [{r['state']}] 公演{r['perfdate']} | 会場「{r['venue']}」 | 修正後prefs={r['prefs']} | {r['title'][:36]}")
