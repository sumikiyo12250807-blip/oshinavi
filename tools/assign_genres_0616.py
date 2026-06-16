# -*- coding: utf-8 -*-
"""新着32件(id755-804)に正式ジャンルを振り分け、genre:"new"を解消。
両方式5件はextraGenresを付与。完了後NEW_ORDERを空にリセット。"""
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# id -> (genre, extraGenres or None)
G = {
    755:('rock',None), 759:('rock',None), 763:('rock',None), 771:('rock',None),
    778:('rock',None), 779:('rock',None), 791:('rock',None), 792:('rock',None),
    800:('rock',None), 803:('rock',None),
    756:('jpop',None), 761:('jpop',None), 769:('jpop',None), 787:('jpop',None),
    788:('jpop',None), 795:('jpop',None), 796:('jpop',None), 801:('jpop',None),
    762:('enka',None), 764:('enka',None), 775:('enka',None), 784:('enka',None), 799:('enka',None),
    793:('kpop',None), 760:('idol',None), 772:('jazz',None), 768:('classic',None),
    # 両方式（主＋extraGenres）
    767:('dento',['jpop']), 780:('jazz',['rock']), 785:('classic',['dento']),
    802:('jpop',['engeki']), 804:('youtuber',['jazz']),
}

src = open('index.html', encoding='utf-8').read()
OLD = '"genre": "new",'
done = 0
for eid, (g, extra) in G.items():
    idx = src.find('"id": %d,' % eid)
    assert idx != -1, 'id%d not found' % eid
    gpos = src.find(OLD, idx)
    assert gpos != -1 and gpos - idx < 600, 'genre:new not found near id%d' % eid
    # 行頭のインデント取得
    line_start = src.rfind('\n', 0, gpos) + 1
    indent = src[line_start:gpos]
    if extra:
        ex = ', '.join('"%s"' % x for x in extra)
        new = '"genre": "%s",\n%s"extraGenres": [%s],' % (g, indent, ex)
    else:
        new = '"genre": "%s",' % g
    src = src[:gpos] + new + src[gpos + len(OLD):]
    done += 1

# NEW_ORDER を空にリセット
src, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>[]', src, count=1)
assert n == 1, 'NEW_ORDER not reset'

open('index.html', 'w', encoding='utf-8').write(src)
print('ジャンル振り分け %d件完了 / NEW_ORDER空にリセット' % done)
