# -*- coding: utf-8 -*-
"""ヒールの安全弁でブロックされたidを適用ログから拾い、
   heal_stale.json の該当行だけを refresh_deadlines の入力として書き出す。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

log = io.open('tmp/heal_apply_0909noon.txt', encoding='utf-8').read()
sec = log.split('🛡️', 1)[1].split('🚨 買える枠ゼロ', 1)[0]
ids = [int(x) for x in re.findall(r'^\s*id=(\d+)', sec, re.M)]
print('ブロックされたid %d件' % len(ids))

rows = json.load(io.open('tmp/heal_stale.json', encoding='utf-8'))
out = [r for r in rows if r.get('id') in set(ids) and r.get('status') == 'convert']
print('heal_stale.json から拾えた %d件' % len(out))
json.dump([{'id': r['id'], 'tickets': r['tickets']} for r in out],
          io.open('tmp/blocked_built_0909.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('→ tmp/blocked_built_0909.json')
