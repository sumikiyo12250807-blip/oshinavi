# -*- coding: utf-8 -*-
"""削除した237件の記録を logs/removed_2026-09-20.md に残す（URLは機械抽出・手で書かない）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-20'

h = io.open('index.html.bak_0920_del', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
by = {e['id']: e for e in json.loads(m.group(2))}
ids = [int(x) for x in io.open('tmp/x0920/del_ids.txt', encoding='utf-8').read().split(',') if x]

with io.open('logs/removed_%s.md' % TODAY, 'w', encoding='utf-8') as f:
    f.write('# %s 朝の便で削除したエントリ %d件\n\n' % (TODAY, len(ids)))
    f.write('理由＝**公演日が過ぎた**（買える枠も1つも残っていない）。\n')
    f.write('別エージェントの独立再導出（「削除は誤りという前提で」）と結論が完全一致。\n')
    f.write('🚨消さずに残したもの＝id1904 劇団かもめんたる（配信が10/4まで生きている）／'
            'id6253 政則十番勝負（配信が9/23〜9/25まで生きている）／'
            'id3683 ムビチケ『超かぐや姫!』（ユーザーが9/19に「残す」と決定）。\n\n')
    for i in ids:
        e = by.get(i)
        if not e:
            f.write('- id=%s （バックアップに無し）\n' % i)
            continue
        ls = e.get('links') or {}
        url = (ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson')
               or next((t.get('url') for t in (e.get('tickets') or []) if t.get('url')), ''))
        f.write('- id=%s %s ／ %s（公演 %s）\n'
                % (i, (e.get('artist') or '')[:60], (e.get('name') or '')[:70], e.get('date')))
        if url:
            f.write('  - %s\n' % url)
print('wrote logs/removed_%s.md (%d件)' % (TODAY, len(ids)))
