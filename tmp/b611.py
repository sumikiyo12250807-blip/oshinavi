# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,'tmp')
from reformat import run
B="https://t.pia.jp/pia/event/event.do?eventBundleCd=b2665502"
updates=[
 {'id':611,'venue':'全国ツアー','pref':'全国','date':'2026-08-15','dateLabel':'2026年6月27日〜8月15日 全国ツアー','tickets':[
   {'type':'一般発売（東京・神田明神 7/18公演）〜6/16 23:59','date':'2026-06-16','url':B},
   {'type':'一般発売（長野 7/25公演）〜6/23 23:59','date':'2026-06-23','url':B},
   {'type':'一般発売（京都 6/27公演）〜6/26 23:59','date':'2026-06-26','url':B},
   {'type':'一般発売（東京・渋谷 8/1公演）〜6/29 23:59','date':'2026-06-29','url':B},
   {'type':'一般発売（愛知 7/4公演）〜7/3 23:59','date':'2026-07-03','url':B},
   {'type':'一般発売（北海道 8/8公演）〜7/6 23:59','date':'2026-07-06','url':B},
   {'type':'一般発売（大阪 8/15公演）〜7/13 23:59','date':'2026-07-13','url':B}]},
]
run(updates)
