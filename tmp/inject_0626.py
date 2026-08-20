# -*- coding: utf-8 -*-
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
entries = json.load(open('tmp/entries_0626_patched.json', encoding='utf-8'))

# 既存idと衝突しないか
existing_ids = set(int(x) for x in re.findall(r'"id":\s*(\d+),', src))
new_ids = [e['id'] for e in entries]
dup = [i for i in new_ids if i in existing_ids]
assert not dup, ('id衝突', dup)

# EVENTS配列の終端 "\n];" を探す
ev_start = src.index('const EVENTS')
close = src.index('\n];', ev_start)
# close位置の直前は最後のエントリの "  }"

# 各エントリを 2スペース基準({が2スペース・キーが4スペース)で整形
def fmt(e):
    j = json.dumps(e, ensure_ascii=False, indent=2)
    return '\n'.join('  ' + line for line in j.split('\n'))

block = ',\n' + ',\n'.join(fmt(e) for e in entries)
new_src = src[:close] + block + src[close:]

# NEW_ORDER 更新
new_src = re.sub(r'const NEW_ORDER = \[[^\]]*\];',
                 'const NEW_ORDER = [' + ', '.join(str(i) for i in new_ids) + '];',
                 new_src, count=1)

# 妥当性: EVENTS配列をパースできるか
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', new_src, re.S)
arr = json.loads(m.group(1))
assert len(arr) == len(existing_ids) + len(entries), ('件数不一致', len(arr))

open('index.html', 'w', encoding='utf-8').write(new_src)
print('投入完了: +', len(entries), '件 / 総EVENTS:', len(arr))
print('NEW_ORDER:', new_ids)
