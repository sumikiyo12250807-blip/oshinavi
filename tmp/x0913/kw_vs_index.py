# -*- coding: utf-8 -*-
"""X投稿に出す名前でぴあを検索した結果（tmp/x0913/kw_<n>.txt）の公演が、OSHINAVIに登録されているかを eventCd で見る（読むだけ）。
夜の便の「投稿に出した公演の取りこぼしを潰す」（.claude/skills/day 第4便の8）のため。
登録あり＝どこかのエントリの links.pia か ticket.url に同じ eventCd がある。
使い方: python tmp/x0913/kw_vs_index.py
出力: 画面 ＋ tmp/x0913/kw_vs_index.txt
"""
import glob
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
cd2id = {}
for e in ev:
    for u in [(e.get('links') or {}).get('pia') or ''] + [t.get('url') or '' for t in e.get('tickets') or []]:
        for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', u):
            cd2id.setdefault(c, e['id'])
out = []
for f in sorted(glob.glob('tmp/x0913/kw_[0-9].txt')):
    txt = io.open(f, encoding='utf-8').read()
    kw = re.search(r'検索語: (.+)', txt).group(1).strip()
    blocks = re.findall(r'^\[(.+?)\] (.+?)\n\s+公演日: (.+?)\n\s+会場\s*: (.+?)\n\s+URL\s*: (\S+)\n\s+検出フィルタ: (.+)$', txt, re.M)
    miss = [(st, nm, d, v, u, flt) for st, nm, d, v, u, flt in blocks
            if (re.search(r'event(?:Bundle)?Cd=(\w+)', u) or [None, None])[1] not in cd2id]
    out.append('■ %s … ぴあ %d件 ／ OSHINAVIに無い %d件' % (kw, len(blocks), len(miss)))
    for st, nm, d, v, u, flt in miss:
        out.append('   [%s] %s | %s | %s | %s | %s' % (st, nm, d, v, flt, u))
io.open('tmp/x0913/kw_vs_index.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
