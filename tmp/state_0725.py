import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

TODAY = '2026-07-25'
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

print('総件数', len(EV))

news = [e for e in EV if e.get('genre') == 'new']
print('genre:new プール', len(news), '件')
for e in news[:60]:
    print('  id=%s %s' % (e.get('id'), e.get('artist') or e.get('name')))

mo = re.search(r'const NEW_ORDER\s*=\s*(\[[^\]]*\])', h)
if mo:
    try:
        print('NEW_ORDER', len(json.loads(mo.group(1))), '件')
    except Exception as ex:
        print('NEW_ORDER パース不可', ex)

# 7/15・7/24 の残り隠れ枠（今日発売でないもの）を名指しで
print('\n=== 残り隠れ枠のうち「今日発売でない」もの ===')
for e in EV:
    for t in e.get('tickets', []):
        sd, d = t.get('startDate'), t.get('date')
        if sd and sd == d and d <= TODAY and not t.get('saleUntilSoldOut') and sd != TODAY:
            print('  id=%s %s | %s | 発売%s' % (e.get('id'), e.get('artist') or e.get('name'), t.get('type'), sd))
