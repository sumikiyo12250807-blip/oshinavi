# -*- coding: utf-8 -*-
"""9/15夜に新着へ入れた「X投稿のライブの取りこぼし」16件を .claude/state/last_batch.json に記録する。
翌朝の「前夜の新着の再チェック」で使う（inject 後に必ず更新する決まり）。
使い方: python tmp/x0916/lastbatch_add.py [--apply]
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
IDS = [10723, 10724, 10728, 10730, 10731, 10732, 10733, 10735, 10736, 10740, 10741, 10744, 10745, 10754, 10759, 10760]
raw = io.open(P, encoding='utf-8').read()
d = json.loads(raw)
rec = {
    'date': '2026-09-15',
    'slot': 'evening',
    'id_from': min(IDS),
    'id_to': max(IDS),
    'count': len(IDS),
    'ids': IDS,
    'source': 'ぴあ・X投稿（9/16発売）に出したアーティスト名での総ざらい（tmp/x0916/audit_posts.py・audit_posts2.py）→公演名・公演日で絞った本当の抜け',
    'assigned': False,
    'rechecked': False,
    'note': '本当の抜け49件 → 組み上がり25（24件は買える枠0＝載せない）→ 新規16件＋既存に畳んだ9枠'
            '（WHITE JAM 8145×4・イルカ 620・インデアミューレ 2468・ジゼル 2243・TSUKEMEN 8404×2）。飛び番＝組み上がらなかった分',
}
if any(b.get('ids') == IDS for b in d.get('batches', [])):
    print('もう記録してある')
    sys.exit(0)
d['batches'].append(rec)
print('足す: %s %s id%s〜%s %d件' % (rec['date'], rec['slot'], rec['id_from'], rec['id_to'], rec['count']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in raw else '\n'
io.open(P, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=2).replace('\n', nl) + nl)
print('書き込み完了')
