# -*- coding: utf-8 -*-
"""9/22朝の投入を .claude/state/last_batch.json に記録する（翌朝の再チェック用）。"""
import io, json, re

P = '.claude/state/last_batch.json'
b = json.load(io.open(P, encoding='utf-8'))
src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
fany_new = sorted(e['id'] for e in ev if e.get('genre') == 'new' and e['id'] > 20960
                  and 'fany' in json.dumps(e.get('links') or {}))
b['batches'].append({
    'date': '2026-09-22', 'slot': 'morning-zaiko', 'id_from': 20926, 'id_to': 20960, 'count': 35,
    'source': 'ZAIKO zaiko_harvest --detail（未登録41件→投入35・既存と同じ公演の疑い6件は保留）',
    'assigned': False, 'rechecked': False,
    'note': '番人 gate_zaiko_slots→heal_zaiko --apply 済み（残り2件は印付き枠だけ）'})
if fany_new:
    b['batches'].append({
        'date': '2026-09-22', 'slot': 'morning-fany', 'id_from': fany_new[0], 'id_to': fany_new[-1],
        'count': len(fany_new),
        'source': 'FANY fany_harvest 9/22〜3/22（投入13・URL重複2783・要確認63）',
        'assigned': False, 'rechecked': False,
        'note': 'heal_fany 96件202枠を当てた。番人の残り11件は9/21公演'})
io.open(P, 'w', encoding='utf-8').write(json.dumps(b, ensure_ascii=False, indent=1))
print('記録した', len(b['batches']), 'fany', fany_new[:3], len(fany_new))
