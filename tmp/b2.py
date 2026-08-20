# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'tmp')
from reformat import run
B="https://t.pia.jp/pia/event/event.do?eventBundleCd=%s"
E="https://t.pia.jp/pia/event/event.do?eventCd=%s"
updates=[
 {'id':611,'date':'2026-07-11','tickets':[{'type':'一般発売（栃木 7/11公演）〜7/10 23:59','date':'2026-07-10','url':B%'b2665502'}]},
 {'id':612,'date':'2026-10-10','tickets':[{'type':'一般発売（茨城 10/10公演）〜10/6 23:59','date':'2026-10-06','url':E%'2615165'}]},
 {'id':613,'date':'2026-11-01','tickets':[{'type':'一般発売（埼玉 11/1公演）6/25 10:00発売','startDate':'2026-06-25','date':'2026-06-25','url':E%'2615172'}]},
 {'id':614,'date':'2026-09-02','tickets':[{'type':'一般発売（愛知 9/2公演）7/3 10:00発売','startDate':'2026-07-03','date':'2026-07-03','url':E%'2623358'}]},
 {'id':615,'date':'2026-09-05','tickets':[{'type':'一般発売（埼玉 9/5公演）6/19 10:00発売','startDate':'2026-06-19','date':'2026-06-19','url':E%'2619393'}]},
 {'id':616,'date':'2026-09-12','tickets':[
    {'type':'先行抽選（東京 9/12公演）〜6/14 23:59','date':'2026-06-14','url':E%'2621066'},
    {'type':'一般発売（東京 9/12公演）7/2 10:00発売','startDate':'2026-07-02','date':'2026-07-02','url':E%'2621066'}]},
]
run(updates)
