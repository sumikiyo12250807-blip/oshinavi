# -*- coding: utf-8 -*-
# 記事3本の登録（OSHINAVI の EVENTS）を書き出す＝係が発売日時・締切・会場を確かめる材料
import io, json, sys
root = 'C:/Users/user/oshinavi/'
sys.path.insert(0, root + 'tools')
import compact_events as C
E = C.load(io.open(root + 'index.html', encoding='utf-8', newline='').read())
ids = [53957, 43234, 55045]
out = io.open(root + 'tmp/x1124/art24/dump.txt', 'w', encoding='utf-8')
for e in E:
    if e['id'] in ids:
        out.write(json.dumps(e, ensure_ascii=False, indent=1) + '\n\n')
print('ok')
