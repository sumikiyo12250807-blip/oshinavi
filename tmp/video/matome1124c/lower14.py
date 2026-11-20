# -*- coding: utf-8 -*-
# 11/14 すちこ「検索するのは小文字だから小文字で表示して」＝画面に出る歌詞の塊の 'OSHINAVI+.jp' を 'oshinavi+.jp' に（set_chunks・set_1114 も＝次の日の写しに残さない）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
out = []
for f in ('set_chunks.py', 'set_1114.py'):
    s = io.open(D + f, encoding='utf-8').read()
    n = s.count("('OSHINAVI+.jp")
    s = s.replace("('OSHINAVI+.jp", "('oshinavi+.jp")
    io.open(D + f, 'w', encoding='utf-8').write(s)
    out.append('%s %d' % (f, n))
io.open(D + 'lower14.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
