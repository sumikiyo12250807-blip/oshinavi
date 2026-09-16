# -*- coding: utf-8 -*-
"""9/12〜9/14発売でどこにも無かった分（ぴあ）を新着に入れる候補にまとめる。
桂文珍独演会(8149)は既存も会場ごとの独立エントリなので、神戸も別の新着として入れる。"""
import io, json
b = json.load(io.open('tmp/built_missD_0911.json', encoding='utf-8-sig'))
keep = [e for e in b if e['id'] in (8149, 8150, 8151, 8153)]
json.dump(keep, io.open('tmp/inject_missD_0911.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(keep), [e['id'] for e in keep])
