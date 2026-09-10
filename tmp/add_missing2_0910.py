# -*- coding: utf-8 -*-
"""push直前の reconcile_pia --new で出た MISSING 2件を埋める。

  id7731 海宝直人        … ぴあに「プレリザーブ」9/12 11:00発売（〜9/16）があるのに登録に無い
  id7753 「僕らの時代じゃない」… ぴあに「一般発売」9/13 10:00発売があるのに登録に無い

🚨MISSINGの「受付中」を鵜呑みにしない（[[reference_reconcile_pia_tool]]）＝
   足す前に生HTMLの状態テキストを読んで、本当に買える枠かを確かめる。
"""
import io
import json
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pia_statustext import statuses  # noqa: E402

CODES = {7731: '2635479', 7753: 'b2670567'}

for i, cd in CODES.items():
    url = ('https://t.pia.jp/pia/event/event.do?event'
           + ('BundleCd=' if cd.startswith('b') else 'Cd=') + cd)
    print('== id%d %s' % (i, url))
    try:
        for st, cls, ctx in statuses(url):
            print('   [%s] %s' % (st, cls))
            print('        %s' % ctx.replace('\n', ' ')[:150])
    except Exception as e:
        print('   取得できなかった: %s' % e)
    print()
