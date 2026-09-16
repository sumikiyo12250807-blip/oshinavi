# -*- coding: utf-8 -*-
"""取り直した2件を、既存に足す分(6524 髪結いの亭主)と新着に入れる分(8152 すすきのめぐり酒)に分ける。"""
import io, json
b = json.load(io.open('tmp/built_retry_0911.json', encoding='utf-8-sig'))
json.dump([e for e in b if e['id'] == 6524], io.open('tmp/built_retry_add_0911.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump([e for e in b if e['id'] == 8152], io.open('tmp/built_retry_new_0911.json', 'w', encoding='utf-8'), ensure_ascii=False)
print('ok')
