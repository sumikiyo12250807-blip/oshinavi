# -*- coding: utf-8 -*-
# 寺尾聰2件の TIGET カテゴリを今朝の収集から写して見張りリストに入れる
import io, json
root = 'C:/Users/user/oshinavi/'
D = json.load(io.open(root + 'tmp/tiget_1001.json', encoding='utf-8'))
cats = {str(e['id']): e.get('cats') or [] for e in D['events']}
p = root + 'tools/tiget_watch.json'
W = json.load(io.open(p, encoding='utf-8'))
for w in W:
    w['cats'] = cats.get(w['id'], w['cats'])
json.dump(W, io.open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print([(w['id'], w['cats']) for w in W])
