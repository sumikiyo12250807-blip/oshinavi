import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = [e for e in json.loads(m.group(2)) if e.get('genre') == 'new']

print('genre:new', len(EV), '件\n')
cnt = collections.Counter(e.get('_genre') for e in EV)
print('下書き_genreの内訳:', dict(cnt), '\n')

print('=== 人の判断が要る子（_piaSub が空 or 音楽その他）===')
need = 0
for e in EV:
    sub = e.get('_piaSub')
    if not sub or 'その他' in str(sub):
        need += 1
        print('  id=%s | %s | _genre=%s | _piaSub=%r | %s' % (
            e.get('id'), e.get('artist') or e.get('name'), e.get('_genre'), sub, e.get('name')))
print('  →', need, '件\n')

print('=== 全49件（id / 下書き / piaSub / 名前）===')
for e in EV:
    print('  %s | %-8s | %-14s | %s' % (e.get('id'), e.get('_genre'), e.get('_piaSub') or '-', (e.get('name') or '')[:44]))
    if e.get('_extraGenres'):
        print('        extra:', e.get('_extraGenres'))
