# TIGET 4,167件から「公演がこれから」の分を取り、音楽を先に500件だけ切り出す（重さの実測用）
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('tmp/x0919/built_tiget_all.json', encoding='utf-8'))
items = [x for x in d['entries'] if x.get('date', '') >= '2026-09-19']
MUSIC = {'jpop', 'rock', 'idol', 'anime', 'kpop', 'yougaku', 'jazz', 'classic', 'hougaku', 'vocaloid', 'fes', 'enka'}
def key(x):
    return (0 if x.get('_genre') in MUSIC else 1, x.get('date', ''))
items.sort(key=key)
first, rest = items[:500], items[500:]
json.dump({'entries': first, 'skipped': []}, open('tmp/x0919/built_tiget_500.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump({'entries': rest, 'skipped': []}, open('tmp/x0919/built_tiget_rest.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('これから', len(items), '/ 500件', len(first), '/ 残り', len(rest))
