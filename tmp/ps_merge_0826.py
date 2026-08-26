"""発売前スイープ7ジャンルの新規候補をまとめ、発売日が遠い順（=カウントダウン優先）に並べる"""
import json, datetime, os, re

LGNAME = {'01': '音楽', '02': '演劇', '03': 'スポーツ', '04': '映画',
          '05': 'アート', '06': 'イベント', '07': 'クラシック'}
TODAY = datetime.date(2026, 8, 26)


def parse_rls(s):
    """rlsdate 'TODAY' / '2026/8/8' / '' → date or None"""
    if not s:
        return None
    if s == 'TODAY':
        return TODAY
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', s)
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


flat = []
seen = set()
for lg in sorted(LGNAME):
    p = r'C:\Users\user\oshinavi\tmp\presale_%s_0803.json' % lg
    if not os.path.exists(p):
        continue
    d = json.load(open(p, encoding='utf-8'))
    for it in d.get('new', []):
        u = it.get('url')
        if u in seen:          # 同じ公演が複数ジャンルに出る（演劇×クラシック等）
            continue
        seen.add(u)
        rd = parse_rls(it.get('rlsdate'))
        days = (rd - TODAY).days if rd else None
        flat.append({'lg': lg, 'days': days, 'rls': it.get('rlsdate') or '',
                     'artist': it.get('artist'), 'perf': it.get('perfdate') or '',
                     'venue': it.get('venue') or '', 'pref': it.get('pref') or '',
                     'url': u})


# 発売まで4日以上を最優先 → 次に日数降順 → 発売日不明(=先行等)は中段
def key(r):
    d = r['days']
    if d is None:
        return (1, 0)
    return (0, -d) if d >= 4 else (2, -d)


flat.sort(key=key)

lines = ['=== 発売前スイープ 新規候補 %d件 (today=%s / 発売まで4日以上を先頭) ===' % (len(flat), TODAY)]
for n, r in enumerate(flat, 1):
    lines.append('%3d | %s | 発売%s(%s) | %s | %s | %s | %s' % (
        n, LGNAME[r['lg']], r['rls'] or '不明',
        ('あと%d日' % r['days']) if r['days'] is not None else '-',
        r['artist'], r['perf'], r['pref'] or r['venue'], r['url']))

open(r'C:\Users\user\oshinavi\tmp\ps_merge_0826.txt', 'w', encoding='utf-8').write('\n'.join(lines))
json.dump(flat, open(r'C:\Users\user\oshinavi\tmp\ps_merge_0826.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print('rows', len(flat))
