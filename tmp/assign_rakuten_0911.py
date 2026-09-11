# -*- coding: utf-8 -*-
"""楽天の新着2件（7838 Meychan配信／7839 WTA250女子）だけを振り分ける（ユーザー「楽天チケットOOK」9/11夜）。
ほかの新着（7840〜8157＝明日の朝に再チェックする分）は振り分けない＝それ以外を全部 --exclude に入れて
恒久ツール assign_genres.py を呼ぶ。引数: --apply で書き込み。"""
import json, re, sys
sys.path.insert(0, 'tools')
ONLY = {7838, 7839}
src = open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
for e in ev:
    if e['id'] in ONLY:
        print('id%s %s | genre=%s → _genre=%s extra=%s' % (e['id'], e['name'], e.get('genre'), e.get('_genre'), e.get('_extraGenres')))
skip = [e['id'] for e in ev if e.get('genre') == 'new' and e['id'] not in ONLY]
import assign_genres
sys.argv = ['assign_genres.py', '--exclude', ','.join(map(str, skip))] + (['--apply'] if '--apply' in sys.argv else [])
# 除外の一覧を長々と出さないよう、出力を後ろだけに絞るのは呼び出し側でやる
sys.exit(assign_genres.main())
