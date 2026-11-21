# -*- coding: utf-8 -*-
# 11/21 記事3本の登録を書き出す（宝塚 雪組 Monte-Cristo・渡辺美里と京フィル・リーディングアクト 一富士茄子牛焦げルギー）＋ get.py を写す
import io, json, sys, shutil
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
keys = ['Monte-Cristo', '渡辺美里', '一富士茄子牛焦げルギー']
out = io.open(root + 'tmp/x1121/art21/dump.txt', 'w', encoding='utf-8')
n = 0
for e in E:
    nm = (e.get('name') or '') + ' ' + (e.get('artist') or '')
    if any(k in nm for k in keys):
        out.write(json.dumps(e, ensure_ascii=False, indent=1) + '\n\n'); n += 1
out.write('件数 %d\n' % n)
out.close()
shutil.copy(root + 'tmp/x1120/art20/get.py', root + 'tmp/x1121/art21/get.py')
print(n)
