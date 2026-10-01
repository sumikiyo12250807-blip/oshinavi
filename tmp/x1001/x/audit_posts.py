# -*- coding: utf-8 -*-
"""9/29夜のX投稿（9/30発売＝pick_1002.json の215件）に出したライブのアーティスト名で、
ぴあを名前で総ざらいして、どのエントリにも登録の無い公演（取りこぼし）を拾う（読むだけ）。
day の第4便8。tools/pia_missing_audit.py の関数を借りる。x0928/x/audit_posts.py の日付違い。
使い方: python tmp/x1001/x/audit_posts.py
出力: tmp/x1001/x/audit_posts.txt（報告）／tmp/x1001/x/audit_keywords.txt（引いた名前・外した名前）
"""
import datetime
import importlib.util
import io
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.getcwd()
spec = importlib.util.spec_from_file_location('pma', os.path.join(ROOT, 'tools', 'pia_missing_audit.py'))
pma = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(pma)

B = 'tmp/x1001/x/'
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()
pick_ids = set(p['id'] for p in json.load(io.open(B + 'pick_1002.json', encoding='utf-8')))

kws, skipped, seen = [], [], set()
for e in evs:
    if e.get('id') not in pick_ids:
        continue
    a = (e.get('artist') or '').strip()
    if not a or a in seen:
        continue
    seen.add(a)
    (kws if pma.good_keyword(a) else skipped).append(a)

io.open(B + 'audit_keywords.txt', 'w', encoding='utf-8').write(
    '引く名前 %d\n%s\n\n外した名前（公演名そのもの・長すぎる・短すぎる欧文）%d\n%s\n' % (
        len(kws), '\n'.join(kws), len(skipped), '\n'.join(skipped)))
print('引く名前 %d ／ 外した名前 %d → %saudit_keywords.txt' % (len(kws), len(skipped), B))
pma.audit(kws, reg, excl, 5, B + 'audit_state.json', B + 'audit_posts.txt', prior=None, rls_from=None, today=TODAY)
print('→ %saudit_posts.txt' % B)
