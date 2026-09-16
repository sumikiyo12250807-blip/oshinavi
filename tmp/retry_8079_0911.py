# -*- coding: utf-8 -*-
"""混雑ページで落ちた id8079 を、元の候補（アーティスト名つき）のまま単独で取り直す候補ファイルを作る。"""
import io, json
c = [x for x in json.load(io.open('tmp/cand_uk2_0911.json', encoding='utf-8')) if x['newid'] == 8079]
json.dump(c, io.open('tmp/cand_8079_0911.json', 'w', encoding='utf-8'), ensure_ascii=False)
print(c)
