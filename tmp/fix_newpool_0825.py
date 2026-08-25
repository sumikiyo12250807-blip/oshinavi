# -*- coding: utf-8 -*-
"""新着プールの個別直し（id据え置き・並び順に触らない）。
1) id5155 きゃりーぱみゅぱみゅ … prefecture が「全国」＝エリアの書き方として禁止
   （[[feedback_kaigai_is_area]]「全国」は使わない）。バッジ側は7県を正しく列挙できている。
   ＋ぴあのbundleページの隠しinput `genreCd=0100102`＝音楽/J-POP・ROCK → _genre を jpop に。
2) id5158 GOODWARP … 同じく genreCd=0100102 → _genre を jpop に（名前fallbackで engeki に倒れていた）。
3) id5097 SHINJUKU LOFT 50th … 会場が「全国ツアー（…）」だが公演は全部 東京。
   「／他／新宿LOFT」の重複も落として実態に合わせる。
"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'index.html'
s = io.open(path, encoding='utf-8', newline='').read()


def block_of(eid):
    m = re.search(r'"id":\s*%d\s*,' % eid, s)
    assert m, eid
    i = s.rfind('{', 0, m.start())
    depth = 0
    for j in range(i, len(s)):
        if s[j] == '{': depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0: return i, j + 1
    raise AssertionError(eid)


def patch(eid, pairs):
    global s
    i, j = block_of(eid)
    b = s[i:j]
    for old, new in pairs:
        assert b.count(old) == 1, 'id%d: %r が %d回' % (eid, old, b.count(old))
        b = b.replace(old, new)
    s = s[:i] + b + s[j:]
    print('id%d 直した' % eid)


PREFS = '北海道・東京・神奈川・愛知・大阪・広島・福岡'
patch(5155, [
    ('"prefecture": "全国"', '"prefecture": "%s"' % PREFS),
    ('"_genre": "engeki"', '"_genre": "jpop"'),
    ('"_piaSub": ""', '"_piaSub": "音楽/J-POP・ROCK"'),
])
patch(5158, [
    ('"_genre": "engeki"', '"_genre": "jpop"'),
    ('"_piaSub": ""', '"_piaSub": "音楽/J-POP・ROCK"'),
])
patch(5097, [
    ('"venue": "全国ツアー（Zepp Shinjuku／新宿LOFT／他／新宿LOFT）"',
     '"venue": "Zepp Shinjuku／新宿LOFT"'),
])

assert '\r\r\n' not in s
io.open(path, 'w', encoding='utf-8', newline='').write(s)
print('CRLF', s.count('\r\n'), 'bareLF', len(re.findall(r'(?<!\r)\n', s)))
