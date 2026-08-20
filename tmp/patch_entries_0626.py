# -*- coding: utf-8 -*-
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

entries = json.load(open('tmp/entries_0626.json', encoding='utf-8'))

# 1337 大橋ちっぽけ = 当日券大阪6/26のみ(今夜19:00〆・明日pushでは期限切れ) → 除外
entries = [e for e in entries if e['id'] != 1337]

# 空だった4件に pia_tickets 実態からチケット追加
add = {
  1343: {"type": "当日引換券販売（大阪 6/28公演）〜6/27 23:59", "date": "2026-06-27"},
  1351: {"type": "一般発売（鹿児島 7/20公演）〜7/19 23:59", "date": "2026-07-19"},
  1355: {"type": "当日引換券販売（大阪 6/28公演）〜6/27 23:59", "date": "2026-06-27"},
  1361: {"type": "一般発売（愛知 8/15公演）〜8/14 23:59", "date": "2026-08-14"},
}
for e in entries:
    if e['id'] in add and not e['tickets']:
        e['tickets'] = [add[e['id']]]

# 全エントリ: 「一般発売.」等の販売種別末尾ピリオド除去（〇〇発売.（→〇〇発売（）
period_fixes = 0
for e in entries:
    for t in e['tickets']:
        old = t['type']
        new = re.sub(r'発売\.', '発売', old)
        if new != old:
            t['type'] = new
            period_fixes += 1

json.dump(entries, open('tmp/entries_0626_patched.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
empties = [e['id'] for e in entries if not e['tickets']]
print('最終エントリ数:', len(entries))
print('ピリオド除去:', period_fixes, '件')
print('まだ空のエントリ:', empties or 'なし')
print('id一覧:', [e['id'] for e in entries])
