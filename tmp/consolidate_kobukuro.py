import re, json

NL = '\r\n'
AMZ = "https://www.amazon.co.jp/s?k=%E3%82%B3%E3%83%96%E3%82%AF%E3%83%AD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"

consolidated = NL.join([
    "  {",
    '    "id": 874,',
    '    "artist": "コブクロ",',
    '    "name": "コブクロ KOBUKURO LIVE TOUR 2026",',
    '    "date": "2026-09-30",',
    '    "dateLabel": "2026年7/31・8/1 石川／9/4・5 広島／9/24・25 香川／9/29・30 北海道",',
    '    "venue": "全国ツアー",',
    '    "prefecture": "石川・広島・香川・北海道",',
    '    "genre": "new",',
    '    "price": null,',
    '    "links": {',
    '      "rakuten": null,',
    '      "lawson": null,',
    '      "pia": "https://t.pia.jp/pia/event/event.do?eventCd=2620913",',
    '      "eplus": null,',
    f'      "amazon": "{AMZ}"',
    '    },',
    '    "tickets": [',
    '      {',
    '        "type": "一般発売（石川 7/31・8/1公演）6/20 10:00発売",',
    '        "startDate": "2026-06-20",',
    '        "date": "2026-06-20",',
    '        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2620913"',
    '      },',
    '      {',
    '        "type": "CANDY ROOM会員限定抽選（広島 9/4・9/5公演）〜6/21 23:59",',
    '        "date": "2026-06-21",',
    '        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2623253"',
    '      },',
    '      {',
    '        "type": "2次プレリザーブ先行抽選（香川 9/24・9/25公演）〜6/29 23:59",',
    '        "date": "2026-06-29",',
    '        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2619864"',
    '      },',
    '      {',
    '        "type": "3次プレリザーブ先行抽選（北海道 9/29・9/30公演）〜6/29 11:00",',
    '        "date": "2026-06-29",',
    '        "url": "https://t.pia.jp/pia/event/event.do?eventCd=2617470"',
    '      }',
    '    ],',
    '    "verified": true,',
    '    "verifiedAt": "2026-06-17"',
    "  }",
])

raw = open('index.html', encoding='utf-8', newline='').read()

def block_span(raw, N):
    s = raw.index(f'  {{{NL}    "id": {N},')
    e = raw.index(f'{NL}  }}', s) + len(f'{NL}  }}')
    return s, e

# 1) replace 874 with consolidated
s, e = block_span(raw, 874)
raw = raw[:s] + consolidated + raw[e:]

# 2) delete 873, 937, 938, 939
for N in (873, 937, 938, 939):
    s, e = block_span(raw, N)
    if raw[e:e+1] == ',':            # not last -> drop trailing ",\r\n"
        assert raw[e:e+3] == ',' + NL, repr(raw[e:e+5])
        raw = raw[:s] + raw[e+3:]
    else:                            # last entry -> drop preceding ",\r\n"
        assert raw[s-3:s] == ',' + NL, repr(raw[s-5:s])
        raw = raw[:s-3] + raw[e:]

# 3) NEW_ORDER: drop 873,937,938,939 (keep 874)
m = re.search(r'const NEW_ORDER = \[([0-9,]*)\];', raw)
ids = [int(x) for x in m.group(1).split(',') if x]
ids = [i for i in ids if i not in (873, 937, 938, 939)]
raw = raw[:m.start()] + 'const NEW_ORDER = [' + ','.join(map(str, ids)) + '];' + raw[m.end():]

# validate
arr = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', raw, re.S).group(1))
assert len(arr) == 674, len(arr)
kob = [e for e in arr if e['artist'] == 'コブクロ']
assert len(kob) == 1 and kob[0]['id'] == 874, [e['id'] for e in kob]
assert len(kob[0]['tickets']) == 4
for did in (873, 937, 938, 939):
    assert all(e['id'] != did for e in arr), did
assert len(re.findall(r'(?<!\r)\n', raw)) == 0, 'lone LF!'

open('index.html', 'w', encoding='utf-8', newline='').write(raw)
print('OK total:', len(arr), '| コブクロ tickets:', len(kob[0]['tickets']))
