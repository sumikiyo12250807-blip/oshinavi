# 組み上がった楽天7件が、別の売り場（ぴあ等）で既に載っていないかを名前の芯で当てる
import json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')
b = json.load(open('tmp/built_rakuten_0919.json', encoding='utf-8'))
b = b if isinstance(b, list) else b.get('entries', b)
h = open('index.html', encoding='utf-8').read()
E = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\n\]);', h, re.S).group(1))
def core(s):
    s = unicodedata.normalize('NFKC', s or '')
    s = re.sub(r'[\[［【(（].*?[\]］】)）]', '', s)
    return re.sub(r'\s+', '', s)[:8]
for x in b:
    c = core(x['name'])
    hits = [e for e in E if c and (c in core(e.get('name')) or c in core(e.get('artist')))]
    print(f"■ {x['name']} / {x['date']} / {x['prefecture']} / 枠{len(x['tickets'])}")
    for t in x['tickets']: print('     ', t['type'])
    for e in hits[:6]:
        print(f"   既存 id{e['id']} [{e['genre']}] {e['name'][:40]} {e['date']} {e.get('prefecture')}")
