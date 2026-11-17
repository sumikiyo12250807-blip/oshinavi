# -*- coding: utf-8 -*-
import io, json, sys
D = 'C:/Users/user/oshinavi/tmp/x1117/art17/'
out = io.open(D + 'show.txt', 'w', encoding='utf-8')
for slug in ('minamikousetsu', 'danseiburanko', 'hikawakiyoshi'):
    for e in json.load(io.open(D + slug + '_entries.json', encoding='utf-8')):
        out.write('## %s %s ｜%s ｜%s ｜%s ｜%s %s\n' % (slug, e['id'], e.get('name'), e.get('artist'), e.get('venue'), e.get('prefecture'), e.get('dateText') or e.get('dateLabel') or e.get('date')))
        out.write('links %s\n' % json.dumps(e.get('links'), ensure_ascii=False))
        for t in e.get('tickets') or []:
            if (t.get('date') or '') >= '2026-11-17':
                out.write('  - %s ｜発売%s ｜締切%s ｜%s %s\n' % (t.get('type'), t.get('startDate'), t.get('date'), t.get('url'), '売切' if t.get('soldout') else ''))
