# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'tmp')
from reformat import run
B="https://t.pia.jp/pia/event/event.do?eventBundleCd=%s"
E="https://t.pia.jp/pia/event/event.do?eventCd=%s"
updates=[
 {'id':641,'date':'2026-09-27','tickets':[{'type':'一般発売（広島 9/27公演）6/20 10:00発売','startDate':'2026-06-20','date':'2026-06-20','url':E%'2621292'}]},
 {'id':642,'date':'2026-09-24','tickets':[
    {'type':'3次プレリザーブ先行（愛知 9/24公演）〜6/14 23:59','date':'2026-06-14','url':E%'2614382'},
    {'type':'一般発売（愛知 9/24公演）6/27 10:00発売','startDate':'2026-06-27','date':'2026-06-27','url':E%'2614382'}]},
 {'id':643,'venue':'全国ツアー','pref':'全国','date':'2026-11-13','dateLabel':'2026年10月24日〜11月13日 全国ツアー','tickets':[{'type':'一般発売（東京・大阪・愛知 10/24〜11/13公演）6/12 10:00発売','startDate':'2026-06-12','date':'2026-06-12','url':B%'b2668066'}]},
 {'id':644,'date':'2026-10-31','tickets':[{'type':'一般発売（福岡 10/31公演）6/12 10:00発売','startDate':'2026-06-12','date':'2026-06-12','url':E%'2617392'}]},
 {'id':645,'artist':'菊池桃子','name':'菊池桃子 2026','date':'2026-06-13','tickets':[{'type':'当日引換券（兵庫 6/13公演）〜6/12 23:59','date':'2026-06-12','url':E%'2623449'}]},
 {'id':646,'date':'2026-09-18','tickets':[{'type':'一般発売（静岡 9/18公演）〜9/17 23:59','date':'2026-09-17','url':E%'2622475'}]},
]
run(updates)
