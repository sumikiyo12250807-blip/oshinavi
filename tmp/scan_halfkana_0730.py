# 表示テキスト(artist/name/venue/dateLabel/ticket.type)に半角カナが混ざっているエントリを洗い出す。
# 楽天由来のデータで見つかった型（id3516 Cｹﾞｰﾄ）。norm_fw は半角カナを触らないので素通りする。
import io, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from build_ai_page import extract_events_array

HALF_KANA = re.compile(r'[｡-ﾟ]+')  # 半角カナ・半角句読点
OUT = os.path.join(os.path.dirname(__file__), 'halfkana_0730.txt')

events = extract_events_array(os.path.join(os.path.dirname(__file__), '..', 'index.html'))
lines = []
hit = 0
for e in events:
    found = []
    for k in ('artist', 'name', 'venue', 'dateLabel'):
        v = e.get(k) or ''
        for m in HALF_KANA.findall(v):
            found.append('%s: %s' % (k, m))
    for i, t in enumerate(e.get('tickets') or [], 1):
        for m in HALF_KANA.findall(t.get('type') or ''):
            found.append('枠%d.type: %s' % (i, m))
    if found:
        hit += 1
        lines.append('id%s (genre=%s) %s' % (e.get('id'), e.get('genre'), e.get('name')))
        for f in found:
            lines.append('    ' + f)

lines.insert(0, '半角カナを含むエントリ: %d 件 / 全 %d 件' % (hit, len(events)))
io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote %s (%d hit / %d events)' % (OUT, hit, len(events)))
