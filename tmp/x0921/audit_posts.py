# -*- coding: utf-8 -*-
"""9/14夜のX投稿に出したライブ（明日9/15〜9/17に発売が始まる・振り分け済みのエントリ）のアーティスト名で、
ぴあを名前で総ざらいして、どのエントリにも登録の無い公演（取りこぼし）を拾う（読むだけ）。
day の第4便8＝「投稿に出したアーティスト名でぴあを検索して枠を全部出し、登録と突合する」。
ぴあのツアーまとめページに出てこない公演がある（feedback_pia_bundle_hides_shows）ので、名前で引く。
中身は tools/pia_missing_audit.py の関数を借りる（登録済みコードの集め方・対象外リスト・キーワードの良し悪し・報告の形）。
使い方: python tmp/x0921/audit_posts.py
出力: tmp/x0921/audit_posts.txt（報告）／tmp/x0921/audit_keywords.txt（引いた名前・外した名前）
"""
import datetime
import importlib.util
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.getcwd()
spec = importlib.util.spec_from_file_location('pma', os.path.join(ROOT, 'tools', 'pia_missing_audit.py'))
pma = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(pma)

DAYS = ('2026-09-22', '2026-09-23', '2026-09-24')
TODAY = datetime.date.today().isoformat()
evs = pma.load_events()
reg = pma.registered_cds(evs)
excl = pma.load_excluded()

kws, skipped, seen = [], [], set()
for e in evs:
    if e.get('genre') == 'new':
        continue
    if not any(t.get('startDate') in DAYS and not t.get('soldout') for t in e.get('tickets') or []):
        continue
    a = (e.get('artist') or '').strip()
    if not a or a in seen:
        continue
    seen.add(a)
    (kws if pma.good_keyword(a) else skipped).append(a)

io.open('tmp/x0921/audit_keywords.txt', 'w', encoding='utf-8').write(
    '引く名前 %d\n%s\n\n外した名前（公演名そのもの・長すぎる・短すぎる欧文）%d\n%s\n' % (
        len(kws), '\n'.join(kws), len(skipped), '\n'.join(skipped)))
print('引く名前 %d ／ 外した名前 %d → tmp/x0921/audit_keywords.txt' % (len(kws), len(skipped)))
pma.audit(kws, reg, excl, 5, 'tmp/x0921/audit_state.json', 'tmp/x0921/audit_posts.txt', prior=None, rls_from=None, today=TODAY)
print('→ tmp/x0921/audit_posts.txt')
