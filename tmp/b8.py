# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'tmp')
from reformat import run
B="https://t.pia.jp/pia/event/event.do?eventBundleCd=%s"
E="https://t.pia.jp/pia/event/event.do?eventCd=%s"
updates=[
 {'id':647,'pref':'大阪','date':'2026-06-13','tickets':[{'type':'当日引換券（大阪なんばHatch 6/13公演）〜6/12 23:59','date':'2026-06-12','url':B%'b2665886'}]},
 {'id':648,'date':'2026-08-27','tickets':[{'type':'一般発売（宮城 8/27公演）6/27 10:00発売','startDate':'2026-06-27','date':'2026-06-27','url':E%'2622461'}]},
 {'id':649,'name':'君島大空 夜会ツアー2026「SUPER BLUE TRANQUILIZER」','venue':'全国ツアー','pref':'全国','date':'2026-09-16','dateLabel':'2026年8月20日〜9月16日 全国ツアー','tickets':[
    {'type':'オフィシャル先行抽選（全公演）〜6/14 23:59','date':'2026-06-14','url':B%'b2668602'},
    {'type':'一般発売（大阪9/4・東京9/15-16公演）6/27 10:00発売','startDate':'2026-06-27','date':'2026-06-27','url':B%'b2668602'}]},
 {'id':650,'date':'2026-08-29','tickets':[{'type':'一般発売（神奈川 8/29公演）6/27 10:00発売','startDate':'2026-06-27','date':'2026-06-27','url':E%'2623261'}]},
 {'id':651,'date':'2026-08-05','tickets':[{'type':'一般発売（福岡 8/5公演）6/20 18:00発売','startDate':'2026-06-20','date':'2026-06-20','url':E%'2623402'}]},
]
run(updates)
