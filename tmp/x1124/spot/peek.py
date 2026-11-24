# -*- coding: utf-8 -*-
import io, json, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import compact_events as C
E = C.load(io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8', newline='').read())
by = {e['id']: e for e in E}
out = io.open('C:/Users/user/oshinavi/tmp/x1124/spot/peek.txt', 'w', encoding='utf-8')
for i in (57757, 33595, 48862, 4507, 4194, 7140, 5158, 48625):
    out.write(json.dumps(by[i], ensure_ascii=False, indent=1) + '\n\n')
