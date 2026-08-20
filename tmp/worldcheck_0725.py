import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

KEY = ('民音', '韓国', '韓楽', 'ケルト', 'フラメンコ', 'ガムラン', '民族', 'ワールド', '国楽', 'アイリッシュ')
for e in EV:
    blob = json.dumps(e, ensure_ascii=False)
    hit = [k for k in KEY if k in blob]
    if hit:
        print('%s | genre=%-8s extra=%-20s | %s | %s' % (
            e.get('id'), e.get('genre'), str(e.get('extraGenres') or ''), ','.join(hit), (e.get('name') or '')[:40]))
