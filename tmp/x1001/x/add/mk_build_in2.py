# -*- coding: utf-8 -*-
# 8 取りこぼし総ざらい（audit_posts）の本命7公演 → build_pia_entries の入力（build_in2.json）
import io, json
C = [('ハク。', 'https://t.pia.jp/pia/event/event.do?eventCd=2637883'),
     ('ハク。', 'https://t.pia.jp/pia/event/event.do?eventCd=2637884'),
     ('ハク。', 'https://t.pia.jp/pia/event/event.do?eventCd=2634990'),
     ('柳家喬太郎', 'https://t.pia.jp/pia/event/event.do?eventCd=2626686'),
     ('空気階段', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667670'),
     ('純烈', 'https://t.pia.jp/pia/event/event.do?eventCd=2635249'),
     ('花江夏樹', 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2671264')]
out = [{'newid': 91001 + i, 'artist': a, 'urls': [u]} for i, (a, u) in enumerate(C)]
json.dump(out, io.open('C:/Users/user/oshinavi/tmp/x1001/x/add/build_in.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out))
