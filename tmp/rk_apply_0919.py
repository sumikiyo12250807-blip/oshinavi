# 9/19 楽天：新規2件を新着に投入＋既存5件へ楽天の枠を足す（アニーは既存の先行枠にURLを入れるだけ）
#   python tmp/rk_apply_0919.py          … 見るだけ
#   python tmp/rk_apply_0919.py --apply  … 書き込む
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
b = json.load(io.open('tmp/built_rakuten_0919.json', encoding='utf-8'))
b = b if isinstance(b, list) else b['entries']
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by = {e['id']: e for e in events}

def find(key):
    return [x for x in b if key in x['name']][0]

NEW = ['ウルトラヒーローズ THE LIVE 〜英雄への道〜', 'キックオフPARTY']
MERGE = {'GLAY［福岡］': 4436, 'さだまさし［大阪': 1, 'ディズニー・オン・クラシック': 1722, 'ディズニー・オン・アイス': 52}

def same(t, u):
    return t.get('type') == u.get('type') and t.get('date') == u.get('date')

nid = max(by) + 1
added_new = []
for k in NEW:
    x = dict(find(k))
    x['id'] = nid
    nid += 1
    events.append(x)
    added_new.append(x['id'])
    print(f"新規 id{x['id']} {x['name']} 枠{len(x['tickets'])}")
for k, i in MERGE.items():
    x = find(k)
    e = by[i]
    for t in x['tickets']:
        if any(same(t, u) for u in e['tickets']):
            print(f"  id{i} 既にある: {t['type']}")
            continue
        e['tickets'].append(t)
        print(f"  id{i} {e['name'][:24]} ＋ {t['type']}")
    if not e['links'].get('rakuten'):
        e['links']['rakuten'] = x['links']['rakuten']
# アニー：既存の「先行（東京 12/12公演）〜9/23 23:59」は楽天の先行抽選と同じ締切でURLが空＝楽天のURLを入れる
annie = find('アニークリスマス')
e = by[7886]
for u in e['tickets']:
    if u['date'] == '2026-09-23' and not u.get('url'):
        u['url'] = annie['tickets'][0]['url']
        print(f"  id7886 URLを入れた: {u['type']}")
if not e['links'].get('rakuten'):
    e['links']['rakuten'] = annie['links']['rakuten']
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
mo = re.search(r'(NEW_ORDER\s*=\s*)\[([0-9,\s]*)\]', out)
arr = [int(v) for v in re.findall(r'\d+', mo.group(2))] + added_new
out = out[:mo.start()] + mo.group(1) + '[' + ', '.join(map(str, arr)) + ']' + out[mo.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了 NEW_ORDER', len(arr))
