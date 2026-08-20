"""id=40 ジブリパーク展 大阪 の是正
実態(e+機械パース 2026-08-02)：
  大阪南港ATCギャラリー 2026/8/1〜9/26 開催・日時指定券が各公演前日23:59まで受付中
  登録は「9/5〜」「8/1 10:00発売(=9/5分の発売日)」で止まっており、隠れ枠化していた
"""
import shutil

SRC = r'C:\Users\user\oshinavi\index.html'
BAK = SRC + '.bak_0802_fix_40'

text = open(SRC, 'rb').read().decode('utf-8')
before_crlf = text.count('\r\n')


def entry_span(text, eid):
    i = text.index('"id": %d,' % eid)
    start = text.rindex('{', 0, i)
    depth = 0
    for j in range(start, len(text)):
        if text[j] == '{':
            depth += 1
        elif text[j] == '}':
            depth -= 1
            if depth == 0:
                return start, j + 1
    raise RuntimeError('end not found')


s, e = entry_span(text, 40)
b = text[s:e]
nl = '\r\n' if '\r\n' in b else '\n'


def sub1(block, old, new, tag):
    assert block.count(old) == 1, '%s: hits %d' % (tag, block.count(old))
    return block.replace(old, new)


b = sub1(b, '"date": "2026-09-05"', '"date": "2026-09-26"', '40.date')
b = sub1(b, '"dateLabel": "2026年9月5日(土)〜"',
         '"dateLabel": "2026年8月1日(土)〜9月26日(土) 大阪 大阪南港ATCギャラリー"', '40.dateLabel')
b = sub1(b, '"eplus": "https://eplus.jp/sf/detail/4516460001-P0030050P021017"',
         '"eplus": "https://eplus.jp/sf/detail/4516460001"', '40.link')

old_t = ('    "tickets": [' + nl +
         '      {' + nl +
         '        "type": "前売券（大阪 9/5〜開催）8/1 10:00発売",' + nl +
         '        "startDate": "2026-08-01",' + nl +
         '        "date": "2026-08-01"' + nl +
         '      }' + nl +
         '    ],')
new_t = ('    "tickets": [' + nl +
         '      {' + nl +
         '        "type": "日時指定券（大阪 8/1〜9/26公演）〜各公演前日 23:59",' + nl +
         '        "date": "2026-09-25",' + nl +
         '        "url": "https://eplus.jp/sf/detail/4516460001"' + nl +
         '      }' + nl +
         '    ],')
b = sub1(b, old_t, new_t, '40.tickets')

text = text[:s] + b + text[e:]
after_crlf = text.count('\r\n')
assert after_crlf == before_crlf, 'CRLF 想定外: %d -> %d' % (before_crlf, after_crlf)

shutil.copyfile(SRC, BAK)
open(SRC, 'wb').write(text.encode('utf-8'))
print('OK backup=%s CRLF %d' % (BAK, after_crlf))
