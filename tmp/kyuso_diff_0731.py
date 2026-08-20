# -*- coding: utf-8 -*-
"""キュウソネコカミのkw検索15件が、index.htmlに登録済みか（eventCd単位）を突き合わせる。"""
import re, json, io

HITS = [
    ('2612708', 'キュウソネコカミ', '岩手10/23・宮城10/25・秋田10/30', '先行抽選'),
    ('2626778', '風雲！大阪城音泉', '大阪10/4', '一般発売'),
    ('2627362', 'キュウソネコカミ', '新潟11/18', '先行抽選'),
    ('2627363', 'キュウソネコカミ', '石川11/20', '先行抽選'),
    ('2612932', 'キュウソネコカミ', '北海道11/23・11/25', '先行抽選'),
    ('b2668940', 'MASTERPIECE 2026', '岐阜11/28・11/29', '先行抽選'),
    ('b2667337', 'DAIENKAI 2026', '東京7/31〜8/2', '一般発売'),
    ('b2668300', 'TENDOUJI', '千葉8/2', '一般発売'),
    ('b2670060', 'SWEET LOVE SHOWER', '山梨8/28', '一般発売'),
    ('b2667358', "LuckyFes'26", '茨城8/8〜8/11', '一般発売'),
    ('b2669704', 'TREASURE05X 2026', '愛知9/12・9/13', '一般発売'),
    ('2626502', 'キュウソネコカミ', '京都9/23 磔磔', '一般発売'),
    ('b2667790', 'ベリテンライブ2026 Special', '栃木9/5・9/6', '一般発売'),
    ('2628908', 'キュウソネコカミ', '静岡 R9年1/16', '先行抽選'),
    ('2627249', 'キュウソネコカミ', '高知 R9年1/30', '先行抽選'),
]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(const\s+EVENTS\s*=\s*)(\[.*?\])(;\s*\n)', h, re.S)
E = json.loads(m.group(2))

cd2ev = {}
for e in E:
    urls = [(e.get('links') or {}).get('pia')] + [t.get('url') for t in e.get('tickets', [])]
    for u in urls:
        mm = re.search(r'event(?:Bundle)?Cd=(\w+)', u or '')
        if mm:
            cd2ev.setdefault(mm.group(1), e)

out = io.open('tmp/kyuso_diff_0731.md', 'w', encoding='utf-8')
out.write('# キュウソネコカミ kw検索 15件 の登録状況\n\n')
for cd, nm, when, st in HITS:
    ev = cd2ev.get(cd)
    mark = '✅登録済み: %s (id%d)' % (ev.get('name'), ev['id']) if ev else '🚨未登録'
    out.write('- [%s] %s / %s / %s → %s\n' % (st, nm, when, cd, mark))

out.write('\n## 既存 キュウソネコカミ エントリ\n')
for e in E:
    if 'キュウソネコカミ' in (e.get('name') or '') or 'キュウソネコカミ' in (e.get('artist') or ''):
        out.write('\nid=%d %s\n' % (e['id'], e.get('name')))
        out.write('  date=%s  dateLabel=%s\n  venue=%s  pref=%s  genre=%s\n' % (
            e.get('date'), e.get('dateLabel'), e.get('venue'), e.get('prefecture'), e.get('genre')))
        out.write('  links.pia=%s\n' % ((e.get('links') or {}).get('pia')))
        for t in e.get('tickets', []):
            out.write('   - %s | date=%s start=%s url=%s\n' % (
                t.get('type'), t.get('date'), t.get('startDate'), t.get('url')))
out.close()
print('wrote tmp/kyuso_diff_0731.md')
