import re, json

NL = '\r\n'
AMZ = "https://www.amazon.co.jp/s?k=%E3%82%B3%E3%83%96%E3%82%AF%E3%83%AD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"

def entry(eid, name, date, dateLabel, venue, pref, pia, ticket_type, start, tdate):
    lines = [
        "  {",
        f'    "id": {eid},',
        '    "artist": "コブクロ",',
        f'    "name": "{name}",',
        f'    "date": "{date}",',
        f'    "dateLabel": "{dateLabel}",',
        f'    "venue": "{venue}",',
        f'    "prefecture": "{pref}",',
        '    "genre": "new",',
        '    "price": null,',
        '    "links": {',
        '      "rakuten": null,',
        '      "lawson": null,',
        f'      "pia": "{pia}",',
        '      "eplus": null,',
        f'      "amazon": "{AMZ}"',
        '    },',
        '    "tickets": [',
        '      {',
        f'        "type": "{ticket_type}",',
    ]
    if start:
        lines.append(f'        "startDate": "{start}",')
    lines += [
        f'        "date": "{tdate}"',
        '      }',
        '    ],',
        '    "verified": true,',
        '    "verifiedAt": "2026-06-17"',
        "  }",
    ]
    return NL.join(lines)

e937 = entry(937, "コブクロ（石川公演）KOBUKURO LIVE TOUR 2026", "2026-08-01",
             "2026年7月31日(金)・8月1日(土) 石川県 本多の森北電ホール", "本多の森北電ホール", "石川",
             "https://t.pia.jp/pia/event/event.do?eventCd=2620913",
             "一般発売（石川 7/31・8/1公演）6/20 10:00発売", "2026-06-20", "2026-06-20")
e938 = entry(938, "コブクロ（広島公演）KOBUKURO LIVE TOUR 2026", "2026-09-05",
             "2026年9月4日(金)・9月5日(土) 広島県 広島文化学園HBGホール", "広島文化学園HBGホール", "広島",
             "https://t.pia.jp/pia/event/event.do?eventCd=2623253",
             "CANDY ROOM会員限定抽選（広島 9/4・9/5公演）〜6/21 23:59", None, "2026-06-21")
e939 = entry(939, "コブクロ（香川公演）KOBUKURO LIVE TOUR 2026", "2026-09-25",
             "2026年9月24日(木)・9月25日(金) 香川県 レクザムホール 大ホール", "レクザムホール 大ホール", "香川",
             "https://t.pia.jp/pia/event/event.do?eventCd=2619864",
             "2次プレリザーブ先行抽選（香川 9/24・9/25公演）〜6/29 23:59", None, "2026-06-29")

raw = open('index.html', encoding='utf-8', newline='').read()

anchor = '  }\r\n];;;;;;;;'
assert raw.count(anchor) == 1, raw.count(anchor)
insertion = '  },' + NL + e937 + ',' + NL + e938 + ',' + NL + e939 + NL + '];;;;;;;;'
raw = raw.replace(anchor, insertion, 1)

# NEW_ORDER append
raw, n = re.subn(r'(const NEW_ORDER = \[[0-9,]*?)\];',
                 r'\g<1>,937,938,939];', raw)
assert n == 1, n

# validate JSON
arr = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', raw, re.S).group(1))
assert len(arr) == 678, len(arr)
for eid in (937, 938, 939):
    assert any(e['id'] == eid for e in arr), eid
assert len(re.findall(r'(?<!\r)\n', raw)) == 0, 'lone LF!'

open('index.html', 'w', encoding='utf-8', newline='').write(raw)
print('OK total entries:', len(arr))
EOF_GUARD = None
