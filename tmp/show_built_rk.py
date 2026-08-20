import json, sys
sys.stdout.reconfigure(encoding='utf-8')
rows = json.load(open('tmp/built_rakuten_0725.json', encoding='utf-8'))
print('構築', len(rows), '件\n')
for e in rows:
    print('id=%s %s | %s | %s | genre下書き=%s' % (e['id'], e['name'][:40], e['dateLabel'][:50], e['prefecture'], e['_genre'] or '-'))
    for t in e['tickets']:
        print('     %s | date=%s%s%s' % (t['type'], t['date'],
              ' start=' + t['startDate'] if t.get('startDate') else '',
              ' [締切不明]' if t.get('saleEndUnknown') else ''))
print('\n--- ログ ---')
print(open('tmp/built_rakuten_log.txt', encoding='utf-8', errors='replace').read()[-600:])
