"""8/2朝の救済修正
 id=1477 セカンドバッカー: ツアー終了→残るのは 8/29 群馬 前橋 DYVER の1公演のみ
 id=966  神戸新開地・喜楽館 8月【昼席】: 千秋楽8/31へ・8/1〜8/2の死んだ枠を削除
CRLF保持のためバイナリで読み書きし、文字列の直接置換だけを行う。
"""
import shutil

SRC = r'C:\Users\user\oshinavi\index.html'
BAK = SRC + '.bak_0802_fix_1477_966'

text = open(SRC, 'rb').read().decode('utf-8')
before_crlf = text.count('\r\n')


def entry_span(text, eid):
    key = '"id": %d,' % eid
    i = text.index(key)
    start = text.rindex('{', 0, i)
    depth = 0
    for j in range(start, len(text)):
        c = text[j]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return start, j + 1
    raise RuntimeError('end not found for %d' % eid)


def edit_entry(text, eid, fn):
    s, e = entry_span(text, eid)
    return text[:s] + fn(text[s:e]) + text[e:]


def sub1(block, old, new, tag):
    assert block.count(old) == 1, '%s: %r hits %d' % (tag, old, block.count(old))
    return block.replace(old, new)


# --- id=1477 ---
def fix1477(b):
    b = sub1(b, '"date": "2026-08-02"', '"date": "2026-08-29"', '1477.date')
    b = sub1(b, '"dateLabel": "2026年7月10日(金)〜2026年8月2日(日) 全国ツアー"',
             '"dateLabel": "2026年8月29日(土) 群馬 前橋 DYVER"', '1477.dateLabel')
    b = sub1(b, '"venue": "全国ツアー（水戸ライトハウス／F.A.D YOKOHAMA／KYOTO MUSE／梅田BananaHall）"',
             '"venue": "前橋 DYVER"', '1477.venue')
    b = sub1(b, '"prefecture": "全国"', '"prefecture": "群馬"', '1477.pref')
    return b


text = edit_entry(text, 1477, fix1477)


# --- id=966 ---
def fix966(b):
    nl = '\r\n' if '\r\n' in b else '\n'
    dead = ('      {' + nl +
            '        "type": "一般発売（兵庫 8/1〜8/2公演）〜8/1 23:59",' + nl +
            '        "date": "2026-08-01"' + nl +
            '      },' + nl)
    b = sub1(b, dead, '', '966.deadticket')
    head_end = b.index('"tickets"')
    head, tail = b[:head_end], b[head_end:]
    head = sub1(head, '"date": "2026-08-01"', '"date": "2026-08-31"', '966.date')
    head = sub1(head, '"dateLabel": "2026年8月1日〜8月23日 兵庫 神戸新開地・喜楽館【昼席】"',
                '"dateLabel": "2026年8月3日〜8月31日 兵庫 神戸新開地・喜楽館【昼席】"', '966.dateLabel')
    return head + tail


text = edit_entry(text, 966, fix966)

after_crlf = text.count('\r\n')
assert after_crlf == before_crlf - 4,'CRLF 想定外: %d -> %d' % (before_crlf, after_crlf)

shutil.copyfile(SRC, BAK)
open(SRC, 'wb').write(text.encode('utf-8'))
print('OK backup=%s CRLF %d -> %d' % (BAK, before_crlf, after_crlf))
