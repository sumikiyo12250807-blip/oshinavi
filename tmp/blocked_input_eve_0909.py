# -*- coding: utf-8 -*-
"""夕方のヒールでブロックされたidを適用ログから拾い、refresh_deadlines の入力を書き出す。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

log = io.open('tmp/heal_apply_0909eve.txt', encoding='utf-8').read()
sec = log.split('🛡️', 1)[1].split('🚨 買える枠ゼロ', 1)[0]
ids = {int(x) for x in re.findall(r'^\s*id=(\d+)', sec, re.M)}
rows = json.load(io.open('tmp/heal_stale.json', encoding='utf-8'))
out = [{'id': r['id'], 'tickets': r['tickets']} for r in rows
       if r.get('id') in ids and r.get('status') == 'convert']
print('ブロック %d件 / heal_stale.json から拾えた %d件' % (len(ids), len(out)))
json.dump(out, io.open('tmp/blocked_built_eve_0909.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
