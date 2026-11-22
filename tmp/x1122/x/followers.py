# -*- coding: utf-8 -*-
import io, json, glob, os
os.chdir('C:/Users/user/oshinavi')
d = json.load(io.open('tmp/x_media_log.json', encoding='utf-8'))
out = io.open('tmp/x1122/x/followers.txt', 'w', encoding='utf-8')
out.write('keys %s\n' % list(d.keys()) if isinstance(d, dict) else 'list\n')
f = d.get('_followers') if isinstance(d, dict) else None
out.write(json.dumps(f, ensure_ascii=False, indent=0)[:3000] + '\n')
rows = d.get('rows') or []
out.write('rows %d\n' % len(rows))
for r in rows[-6:]:
    out.write(json.dumps(r, ensure_ascii=False)[:200] + '\n')
out.write('csv %s\n' % sorted(glob.glob('tmp/x_content_*.csv'))[-5:])
out.write('analysis %s\n' % sorted(glob.glob('tmp/x_analysis_*.md'))[-3:])
