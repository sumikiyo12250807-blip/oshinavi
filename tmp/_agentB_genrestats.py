# -*- coding: utf-8 -*-
import re, io, json, collections

s = io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8').read()
i = s.find('const EVENTS')
i = s.find('[', i)
data, _end = json.JSONDecoder().raw_decode(s[i:])
out = io.open('C:/Users/user/oshinavi/tmp/_agentB_genrestats.txt', 'w', encoding='utf-8')
c = collections.Counter(e.get('genre') for e in data)
out.write('total %d\n' % len(data))
for k, v in c.most_common():
    out.write('%s\t%d\n' % (k, v))

# look up specific artists
targets = ['Versailles', 'NoGoD', 'vistlip', 'DEZERT', 'MUCC', 'HIZAKI', '蜈蚣', '透明少女',
           'Sick2', 'ホタル', 'マキナ', '中村佳穂', '藤川千愛', '羽多野', 'go!go!vanillas',
           'フレデリック', 'LIL LEAGUE', '上田正樹', 'DADAROMA', 'アルルカン', 'ゴールデンボンバー',
           'the GazettE', 'BUCK-TICK', 'Plastic Tree', 'キズ', 'ジグザグ']
out.write('\n=== lookups ===\n')
for t in targets:
    for e in data:
        blob = (e.get('artist', '') or '') + ' ' + (e.get('name', '') or '')
        if t.lower() in blob.lower():
            out.write('%s | %s | %s | genre=%s extra=%s\n' % (
                t, e.get('artist'), (e.get('name') or '')[:50], e.get('genre'), e.get('extraGenres')))
out.close()
print('ok')
