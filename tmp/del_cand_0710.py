# -*- coding: utf-8 -*-
"""7/10 削除候補の確認用リスト（公演名・会場・公演日・確認用URL）。
convert_0710.json(期限切れtriage) と heal_hidden_0710.json(隠れ枠ヒール) の
status=delete を統合。ユーザーOK前は絶対に削除しない。"""
import re, json, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ids = {}
for f in ('tmp/convert_0710.json', 'tmp/heal_hidden_0710.json'):
    if not os.path.exists(f):
        continue
    for o in json.load(open(f, encoding='utf-8')):
        if o.get('status') == 'delete':
            ids[o['id']] = f
# WebFetch で裏取り済みの非ぴあ／DROP系を手動追加
MANUAL = {217: 'e+ 生HTML「受付は全て終了しました」全公演', 1200: 'ぴあ 全枠販売終了(セブン先行=本サイト取扱なし)'}
for i, why in MANUAL.items():
    ids.setdefault(i, 'manual:' + why)

h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in E}

print(f'== 削除候補 {len(ids)}件（ユーザーチェック用） ==\n')
for n, i in enumerate(sorted(ids), 1):
    e = byid.get(i)
    if not e:
        print(f'{n}. id={i} ★DB内に無い'); continue
    L = e.get('links') or {}
    url = L.get('pia') or L.get('eplus') or L.get('rakuten') or L.get('lawson') or L.get('official') or ''
    if not url:
        for t in e.get('tickets', []):
            if t.get('url'): url = t['url']; break
    vendor = 'ぴあ' if 'pia' in url else 'e+' if 'eplus' in url else '楽天' if 'rakuten' in url else 'その他'
    src = ids[i]
    mark = '  ⚠️非ぴあ' if vendor != 'ぴあ' else ''
    print(f'{n}. {e.get("artist","")} 『{e.get("name","")}』')
    print(f'   {e.get("venue","")}（{e.get("prefecture","")}）公演日 {e.get("date","")}{mark}')
    print(f'   [{vendor}で確認]({url})')
    if src.startswith('manual:'):
        print(f'   裏取り: {src[7:]}')
    print()
print('IDS =', sorted(ids))
