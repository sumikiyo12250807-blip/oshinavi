# -*- coding: utf-8 -*-
"""8/12投稿のユーザー報告実測を tools/x_log.json に追記する。"""
import json
import os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'x_log.json')
with open(P, 'r', encoding='utf-8') as f:
    log = json.load(f)

log['posts'].append({
    "posted": "2026-08-12",
    "title": "キュウソネコカミ DMCC REAL ONEMAN TOUR 2026-2027",
    "cat": "ロック(バンド)",
    "measured": "2026-08-12",
    "measured_h": 10,
    "imp": 107,
    "like": 0,
    "rt": 0,
    "reply": 0,
    "eng": 0,
    "detail_cl": 0,
    "profile": 0,
    "link_cl": None,
    "link": True,
    "tone": "おねえ",
    "followers": 280900,
    "note": "ユーザー報告のスクショ実測。10時間後の暫定値＝台帳の12〜13時間値と並べると中位。"
            "リンククリック欄はスクショに写っていないので未取得(本文にURLありなので存在するはず)"
})

with open(P, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(log, f, ensure_ascii=False, indent=1)
print('posts %d' % len(log['posts']))
