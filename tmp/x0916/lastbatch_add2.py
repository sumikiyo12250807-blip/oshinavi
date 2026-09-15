# -*- coding: utf-8 -*-
"""9/15夜にローチケから新着へ入れた 10762 新日本プロレス 赤磐 11/1 を .claude/state/last_batch.json に記録する。
翌朝の「前夜の新着の再チェック」で使う（ぴあ以外＝振り分けはユーザーの確認のあと）。
使い方: python tmp/x0916/lastbatch_add2.py [--apply]
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
IDS = [10762]
raw = io.open(P, encoding='utf-8').read()
d = json.loads(raw)
rec = {
    'date': '2026-09-15',
    'slot': 'evening',
    'id_from': 10762,
    'id_to': 10762,
    'count': 1,
    'ids': IDS,
    'source': 'ローチケ（実ブラウザで購入ページ2枚を読んだ）・X投稿の主役②新日本プロレスの取りこぼしチェック（公式の日程 njpw.co.jp と突き合わせ）',
    'assigned': False,
    'rechecked': False,
    'note': 'ぴあ以外＝振り分けはユーザーの確認のあと。プレリク先行 9/13 12:00〜9/19 23:59（発売中）＋一般 9/20 10:00発売。'
            '公式にあって売り場にまだ無い＝石狩10/17・後楽園10/25/26・藤沢11/21・横浜武道館11/23・東京ドームR9年1/4（9/19・9/26 の朝に見直す）',
}
if any(b.get('ids') == IDS and b.get('date') == rec['date'] for b in d.get('batches', [])):
    print('もう記録してある')
    sys.exit(0)
d['batches'].append(rec)
print('足す: %s %s id%s %d件' % (rec['date'], rec['slot'], rec['id_from'], rec['count']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in raw else '\n'
io.open(P, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=2).replace('\n', nl) + nl)
print('書き込み完了')
