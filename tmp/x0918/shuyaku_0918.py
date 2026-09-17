import io, json, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
PICK = [('GLAY', lambda a: a == 'GLAY'), ('角野隼斗', lambda a: '角野隼斗' in a), ('世良公則', lambda a: a.startswith('世良公則'))]
out = []
for label, f in PICK:
    for e in ev:
        if not f(e.get('artist', '')) or e.get('genre') == 'new':
            continue
        out.append('## 主役枠：%s（id%s）' % (e['artist'], e['id']))
        out.append('名前＝%s ／ 会期＝%s ／ 会場＝%s ／ genre=%s' % (e['artist'], e.get('dateLabel'), e.get('venue'), e.get('genre')))
        for t in e.get('tickets', []):
            if t.get('soldout') or (t.get('date', '') < '2026-09-18'):
                continue
            out.append('  枠: %s ／ 締切または発売日 %s' % (t['type'], t['date']))
        out.append('')
io.open('tmp/x0918/shuyaku.md', 'w', encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))
