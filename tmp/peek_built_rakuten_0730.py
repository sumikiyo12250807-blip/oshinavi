# -*- coding: utf-8 -*-
"""楽天ビルド結果をUTF-8ファイルに一覧化（統合漏れの確認用）。"""
import json

d = json.load(open('tmp/built_rakuten_0730.json', encoding='utf-8'))
out = [f'エントリ {len(d)}件']
for e in d:
    out.append('')
    out.append(f"id={e['id']}  artist={e.get('artist')}")
    out.append(f"  venue={e.get('venue')}")
    out.append(f"  date={e.get('date')}  dateLabel={e.get('dateLabel')}")
    out.append(f"  genre={e.get('genre')} _genre={e.get('_genre')}")
    out.append(f"  links={e.get('links')}")
    for t in e.get('tickets') or []:
        out.append(f"    枠: {t.get('type')}")
        out.append(f"        date={t.get('date')} start={t.get('startDate')} unknownEnd={t.get('saleEndUnknown')}")
        out.append(f"        url={(t.get('url') or '-')[:110]}")
open('tmp/peek_built_rakuten_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/peek_built_rakuten_0730.txt')
