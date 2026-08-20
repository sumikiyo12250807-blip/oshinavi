# -*- coding: utf-8 -*-
"""空カッコ会場3件のvenueだけを、直したビルダーの出力で置き換える。
   tickets/dateLabel/日付は触らない（並び順・バッジを動かさない）。
   memory: feedback_new_list_order_lock / feedback_index_html_crlf_preserve
   使い方: python tmp/apply_venue_0727.py [--apply]
"""
import sys, io, re, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PATH = 'index.html'
apply = '--apply' in sys.argv
built = json.load(open('tmp/revenue.json', encoding='utf-8'))['built']

src = open(PATH, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in src else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
by_id = {e['id']: e for e in events}

for k, b in built.items():
    eid = int(k)
    e = by_id[eid]
    assert e.get('genre') == 'new', f'id{eid} は新着でない'
    # 安全確認: 公演期間とチケット枠数が一致していること（別物を上書きしない）
    assert e['date'] == b['date'], f'id{eid} 公演日が違う {e["date"]} != {b["date"]}'
    assert len(e['tickets']) == len(b['tickets']), f'id{eid} 枠数が違う'
    print(f"  id{eid} {e['name'][:34]}")
    print(f"    旧 venue: {e['venue']}")
    print(f"    新 venue: {b['venue']}")
    e['venue'] = b['venue']

if not apply:
    print('\n(--apply で書き込み)')
    sys.exit(0)

dumped = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
open(PATH, 'w', encoding='utf-8', newline='').write(src[:m.start(2)] + dumped + src[m.end(2):])
print('\n書き込み完了')
