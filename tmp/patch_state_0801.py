# -*- coding: utf-8 -*-
"""監査stateに flumpool と 初音ミク を「育成対象」として足す。

この2件は取りこぼしが**登録済みバンドルURLの中**にあるので、キーワード検索型の監査
（未登録eventCdを探す）には出てこない。だが grow_from_audit は対象エントリの
pia_urls（links.pia＝バンドル）から作り直すので、対象に入れさえすれば全公演を拾える。
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'audit_11_state.json')

ADD = {
    'flumpool': 'https://ticket.pia.jp/pia/event.do?eventBundleCd=b2666817',
    '初音ミク「マジカルミライ 2026」': 'https://ticket.pia.jp/pia/event.do?eventBundleCd=b2666462',
}

state = json.load(io.open(STATE, encoding='utf-8'))
results = state.setdefault('results', {})
for kw, url in ADD.items():
    results[kw] = {
        'hits': 1,
        'missing': [{
            'code': url.split('=')[-1], 'url': url, 'title': kw,
            'status': '発売前', 'perfdate': '', 'venue': '', 'rlsdate': '',
            'own_name': True,
        }],
    }

json.dump(state, io.open(STATE, 'w', encoding='utf-8'), ensure_ascii=False)
print('patched', STATE, 'keys=', len(results))
