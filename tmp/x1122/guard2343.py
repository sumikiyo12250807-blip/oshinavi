# -*- coding: utf-8 -*-
# 11/22 23:43 番人の確認（x1121/guard2343.py の形）
import io
s = io.open('C:/Users/user/oshinavi/tmp/x1121/guard2343.py', encoding='utf-8').read()
for a, b in (("tmp/x1121/", "tmp/x1122/"), ("'tmp/x1122/' ", "'tmp/x1122/' "), ("night_1121", "night_1122"), ("night_collect21", "night_collect22"),
             ("night_chain21", "night_chain22"), ("night_word9", "night_word10"), ("nassign_n/", "nassign22n/"), ("overnight_1121", "overnight_1122")):
    s = s.replace(a, b)
s = s.replace("for f in ['night_1122.done'", "for f in ['eve22_chain.done', 'night_1122.done'")
s = s.replace("D + 'nassign22n/log.txt'", "D + 'nassign22n/log.txt', D + 'eve22_chain.txt'")
exec(compile(s, 'g', 'exec'))
