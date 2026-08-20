# 新着プール(genre:new)を人間が目視できる形でUTF-8ファイルに書き出す。
# コンソールに日本語を出すと化けて誤読するので必ずファイル経由（feedback_no_mojibake_japanese_read）。
import io, json, os, re, sys, urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from build_ai_page import extract_events_array  # 既存の抽出器を再利用

OUT = os.path.join(os.path.dirname(__file__), 'newpool_0730.txt')

events = extract_events_array(os.path.join(os.path.dirname(__file__), '..', 'index.html'))
news = [e for e in events if e.get('genre') == 'new']

lines = []
lines.append('新着プール genre:new = %d 件' % len(news))
lines.append('')
for e in news:
    lines.append('=' * 78)
    lines.append('id%s  %s' % (e.get('id'), e.get('artist')))
    if e.get('name') != e.get('artist'):
        lines.append('  name違い: %s' % e.get('name'))
    lines.append('  ev.date=%s  県=%s  会場=%s' % (e.get('date'), e.get('prefecture'), e.get('venue')))
    lines.append('  dateLabel: %s' % e.get('dateLabel'))
    lines.append('  下書きジャンル _genre=%s  extra=%s  _piaSub=%s' % (
        e.get('_genre'), e.get('_extraGenres'), e.get('_piaSub')))
    lk = e.get('links') or {}
    for k in ('pia', 'rakuten', 'eplus', 'lawson', 'official'):
        if lk.get(k):
            lines.append('  link.%s: %s' % (k, lk[k]))
    if lk.get('amazon'):
        m = re.search(r'[?&]k=([^&]*)', lk['amazon'])
        q = urllib.parse.unquote(m.group(1)) if m else '(k無し)'
        lines.append('  amazon検索語: %s' % q)
    else:
        lines.append('  amazon: なし')
    if e.get('price'):
        lines.append('  price: %s' % e.get('price'))
    for i, t in enumerate(e.get('tickets') or [], 1):
        lines.append('  枠%d type=%s' % (i, t.get('type')))
        lines.append('      date=%s  startDate=%s%s' % (
            t.get('date'), t.get('startDate'),
            '  ★単日形(date==startDate)' if t.get('date') == t.get('startDate') else ''))
        for k, v in t.items():
            if k not in ('type', 'date', 'startDate'):
                lines.append('      %s=%s' % (k, v))
lines.append('=' * 78)

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote %s (%d entries, %d lines)' % (OUT, len(news), len(lines)))
