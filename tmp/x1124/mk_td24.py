# -*- coding: utf-8 -*-
# 11/24 朝 すちこ「TicketDive 42件・B.LEAGUE 9件　これはこれで全部なの？」＝TicketDive は --max-events 100 で打ち切っていた（見つけた710・残り281・出演者ページ604は未読）
# → 上限なしで読む版を作る（夜の吉本の売り切れの印つけが終わってから＝重い道具を同時2本まで）
import io, os
os.chdir('C:/Users/user/oshinavi')
s = io.open('tmp/x1123/night_word11/td_night.py', encoding='utf-8').read()
reps = [("D = 'tmp/x1115/ticketdive/'", "D = 'tmp/x1124/td/'\nos.makedirs(D, exist_ok=True)\nwhile not os.path.exists('tmp/x1123/night_chain23.done'):\n    time.sleep(60)"),
        ("'--max-events', '100', ", ""),
        ("b'td_inject'", "b'td24'"),
        ("'tmp/x1115/msg_td2.txt'", "D + 'msg.txt'"),
        ("11/22 夜通し（commit だけ）：TicketDive の新しい公演を集めて新着の先頭へ", "11/24 朝（commit だけ）：すちこ「これはこれで全部なの？」＝TicketDive を上限なし（前は100公演で打ち切り）で集め直して新着の先頭へ")]
for a, b in reps:
    assert a in s, a
    s = s.replace(a, b)
io.open('tmp/x1124/td24.py', 'w', encoding='utf-8').write(s)
print('ok')
