# -*- coding: utf-8 -*-
"""built4 から「一般発売（立見）（長野 10/25公演）〜10/8 23:59」を外す（2026-09-16 夜）。

ぴあの長野10/25のページ（eventCd=2629395）は「販売期間中」のカードが2枚＝指定席と立見が両方買える。
けれどうちの**枠の単位は「締切」**で、突き合わせは券種名でなく「県・公演日・締切」（feedback_capture_all_deadlines_on_add）。
既存「一般発売（長野 10/25公演）〜10/8 23:59」と3つとも同じなので、足すと画面に同じ締切が2行並ぶ。
＝この1件は保留にしてユーザーに相談する。残りの3枠は足す。

出力: tmp/x0917/built4b.json
使い方: python tmp/x0917/drop_tachimi.py
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
DROP = '一般発売（立見）（長野 10/25公演）〜10/8 23:59'

data = json.load(io.open('tmp/x0917/built4.json', encoding='utf-8'))
n = 0
for e in data:
    keep = [t for t in e['tickets'] if t.get('type') != DROP]
    n += len(e['tickets']) - len(keep)
    e['tickets'] = keep
data = [e for e in data if e['tickets']]
assert n == 1, n
json.dump(data, io.open('tmp/x0917/built4b.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('dropped=%d entries=%d slots=%d' % (n, len(data), sum(len(e['tickets']) for e in data)))
