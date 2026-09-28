# -*- coding: utf-8 -*-
"""last_batch.json に9/28夜のぴあ発売前スイープ新規35件を1件足す（既存の形＝indent 1・ensure_ascii False）。"""
import io, json
p = '.claude/state/last_batch.json'
raw = io.open(p, encoding='utf-8', newline='').read()
d = json.loads(raw)
if any(b.get('date') == '2026-09-28' and b.get('id_from') == 25250 for b in d['batches']):
    print('既にある'); raise SystemExit
d['batches'].append({
    'date': '2026-09-28',
    'slot': 'night',
    'id_from': 25250,
    'id_to': 25284,
    'count': 35,
    'source': 'ぴあ 発売前スイープ rlsStatus=0102+0202（7ジャンル・9/28 19:36〜）の未登録54件',
    'assigned': False,
    'rechecked': False,
    'note': '54件→bundle重複8（中身が既存と同じ窓）・build skip4（買える/発売前の枠0）・既存5件に6ページ7枠を足し込み（2338石川さゆり三重・3471宇都宮隆 横浜/東京・3406反田恭平 仙台・23644 Predawn大阪・22537佐々木亮介 大阪/京都）HEAD突合で消えた枠0・Chevon大阪は新規25269に同居。新規35件41枠 全件発売前の枠あり。check_badges OK・reconcile --ids 40件 OK39/MISSING0/DROP0/STALE1(2338の既存東京枠)/FETCH0（QC 57/59枠照合）・CRLF LFだけ0・NEW_ORDERずれ0',
})
nl = '\r\n' if '\r\n' in raw else '\n'
io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=1).replace('\n', nl) + ('' if not raw.endswith(('\n',)) else nl))
print('追記した')
