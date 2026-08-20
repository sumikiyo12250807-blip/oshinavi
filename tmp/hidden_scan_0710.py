# -*- coding: utf-8 -*-
"""startDate==date かつ date<today = renderCard 49011行で非表示になる枠。
親エントリが「他に生きた枠あり」なら check_expired に出ず永久に隠れる。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-07-10'
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))

def visible(t):
    """renderCard 49011行の再現: 非表示ならFalse"""
    sd = t.get('startDate'); d = t.get('date')
    if t.get('saleUntilSoldOut'):
        return True
    if (not sd or sd <= TODAY) and d < TODAY:
        return False
    return True

hidden_entries = []
for e in EVENTS:
    ts = e.get('tickets', [])
    hid = [t for t in ts if (t.get('startDate') and t['startDate'] == t.get('date')
                             and t['date'] < TODAY and not t.get('saleUntilSoldOut'))]
    if not hid:
        continue
    alive = [t for t in ts if visible(t)]
    piaurl = (e.get('links') or {}).get('pia', '')
    has_pia = bool(piaurl and 'pia' in piaurl) or any('pia' in (t.get('url') or '') for t in ts)
    hidden_entries.append({
        'id': e['id'], 'artist': e.get('artist', '')[:30], 'genre': e.get('genre'),
        'n_hidden': len(hid), 'n_alive': len(alive), 'n_tickets': len(ts),
        'has_pia': has_pia,
        'orphan': len(alive) == 0,
    })

tot_hidden = sum(x['n_hidden'] for x in hidden_entries)
orphans = [x for x in hidden_entries if x['orphan']]
survivors = [x for x in hidden_entries if not x['orphan']]
nopia = [x for x in hidden_entries if not x['has_pia']]

print(f'== 非表示枠を持つエントリ {len(hidden_entries)}件 / 非表示枠 {tot_hidden}枠 ==')
print(f'  A. 全枠死亡(check_expiredが拾う) : {len(orphans)}件')
print(f'  B. 他に生きた枠あり(永久に隠れる) : {len(survivors)}件  ← 買えるのに見えない')
print(f'  うち ぴあURL無し(要WebFetch)     : {len(nopia)}件')
print('\n-- B. 永久に隠れてる枠を持つエントリ --')
for x in sorted(survivors, key=lambda v: -v['n_hidden']):
    p = '' if x['has_pia'] else ' [非ぴあ]'
    print('  id=%-5d %-32s 隠れ%d/全%d枠 [%s]%s' % (x['id'], x['artist'], x['n_hidden'], x['n_tickets'], x['genre'], p))
print('\nIDS_B =', sorted(x['id'] for x in survivors))
if orphans:
    print('\nIDS_A(全枠死亡) =', sorted(x['id'] for x in orphans))
