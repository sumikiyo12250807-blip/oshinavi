# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'tmp')
from reformat import run
E="https://t.pia.jp/pia/event/event.do?eventCd=%s"
updates=[
 {'id':623,'venue':'セカンド・クラッチ／YEBISU YA PRO','pref':'広島・岡山','date':'2026-11-08','dateLabel':'2026年10月4日(広島)・11月8日(岡山)','tickets':[{'type':'一般発売（広島10/4・岡山11/8公演）7/4 10:00発売','startDate':'2026-07-04','date':'2026-07-04','url':E%'2622040'}]},
 {'id':624,'venue':'長野CLUB JUNK BOX／新潟CLUB RIVERST','pref':'長野・新潟','date':'2026-11-01','dateLabel':'2026年10月31日(長野)・11月1日(新潟)','tickets':[{'type':'一般発売（長野10/31・新潟11/1公演）7/4 10:00発売','startDate':'2026-07-04','date':'2026-07-04','url':E%'2622480'}]},
 {'id':625,'venue':'club change WAVE／仙台Rensa','pref':'岩手・宮城','date':'2026-11-15','dateLabel':'2026年11月14日(岩手)・15日(宮城)','tickets':[{'type':'一般発売（岩手11/14・宮城11/15公演）7/4 10:00発売','startDate':'2026-07-04','date':'2026-07-04','url':E%'2622635'}]},
 {'id':626,'date':'2026-12-19','tickets':[{'type':'一般発売（東京 12/19公演）7/4 10:00発売','startDate':'2026-07-04','date':'2026-07-04','url':E%'2621924'}]},
 {'id':627,'date':'2026-11-14','tickets':[
    {'type':'プレリザーブ先行（福岡 11/14公演）〜6/14 23:59','date':'2026-06-14','url':E%'2619532'},
    {'type':'一般発売（福岡 11/14公演）6/27 10:00発売','startDate':'2026-06-27','date':'2026-06-27','url':E%'2619532'}]},
 {'id':628,'date':'2026-11-29','tickets':[
    {'type':'先行抽選（京都 11/29公演）〜6/14 23:59','date':'2026-06-14','url':E%'2619533'},
    {'type':'一般発売（京都 11/29公演）6/27 10:00発売','startDate':'2026-06-27','date':'2026-06-27','url':E%'2619533'}]},
]
run(updates)
