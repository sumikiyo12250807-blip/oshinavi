# -*- coding: utf-8 -*-
"""484 / 2231 の venue・prefecture・dateLabel・date を既存ビルダーで再導出（UTF-8ファイル出力）"""
import io, json, sys
sys.path.insert(0, 'tools')
import build_pia_entries as B

TARGETS = [
    (484,  'KOYABU SONIC 2026', ['https://t.pia.jp/pia/event/event.do?eventCd=2620581']),
    (2231, '舞台『キュー』', ['https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668891']),
]

out = []
for eid, art, urls in TARGETS:
    try:
        ev = B.build({'newid': eid, 'artist': art, 'urls': urls})
    except Exception as ex:
        out.append('id=%d ERROR %s' % (eid, ex))
        continue
    if not ev:
        out.append('id=%d 買える枠ゼロ' % eid)
        continue
    keep = {k: ev.get(k) for k in ('date', 'dateLabel', 'venue', 'prefecture', 'name', 'artist')}
    out.append('id=%d\n%s' % (eid, json.dumps(keep, ensure_ascii=False, indent=1)))
    out.append('tickets:\n%s' % json.dumps(ev.get('tickets'), ensure_ascii=False, indent=1))
    out.append('')

io.open('tmp/out_rederive_0730.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_rederive_0730.txt')
