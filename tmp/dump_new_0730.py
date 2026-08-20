# -*- coding: utf-8 -*-
"""新着50件の全文ダンプ（目視チェック用）＋_piaSub一覧"""
import io, json, re

raw = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[.*?\]);', raw, re.S)
NEW = [e for e in json.loads(m.group(1)) if e.get('genre') == 'new']

out = []
for ev in NEW:
    lk = {k: v for k, v in (ev.get('links') or {}).items() if v}
    out.append('── id=%s  _genre=%s  _piaSub=%r  _srcgenre=%r' % (
        ev['id'], ev.get('_genre'), ev.get('_piaSub'), ev.get('_srcgenre')))
    out.append('   artist : %s' % ev.get('artist'))
    out.append('   name   : %s' % ev.get('name'))
    out.append('   会場   : %s ／ %s' % (ev.get('venue'), ev.get('prefecture')))
    out.append('   期間   : %s  (ev.date=%s)' % (ev.get('dateLabel'), ev.get('date')))
    for t in ev.get('tickets', []):
        out.append('   枠 : %s' % t.get('type'))
        out.append('        date=%s%s%s' % (
            t.get('date'),
            '  startDate=' + t['startDate'] if t.get('startDate') else '',
            '  url=' + t['url'] if t.get('url') else ''))
    out.append('   売り場: %s' % ', '.join('%s=%s' % (k, v) for k, v in lk.items()))
    out.append('')

io.open('tmp/out_dump_new_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_dump_new_0730.txt  (%d件)' % len(NEW))
