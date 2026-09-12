# -*- coding: utf-8 -*-
"""ヒール適用の前後で「画面に出ていた枠」が減ったエントリを数える（memory feedback_heal_flattens_ticket_types）。
ヒール自身の安全弁は公演単位でしか比べないので、同じ公演の券種違い（阪神の車椅子席など）が
丸ごと消えても気づかない。だから HEAD と現物を突き合わせる。

使い方: python tmp/heal_diff_0913.py [比較元のgitリビジョン(既定HEAD)]
出力: tmp/heal_diff_0913.txt
"""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-13'
REV = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'


def events(text):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))}


def visible(t):
    """index.html の表示ルール＝売り切れ/在庫限りは常に出す。それ以外は締切が今日以降なら出す。"""
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date') or ''
    return not ((not sd or sd <= TODAY) and d < TODAY)


def key(t):
    """券種名から日付部分を落として突き合わせる（「9/1 10:00発売」→「〜12/20 23:59」の書き換えを
    『消えた』と数えないため）。飛び先URLも見るので、売り場ごと消えた型は拾える。"""
    ty = re.sub(r'R9年\s*', '', t.get('type') or '')
    ty = re.sub(r'\d{1,2}/\d{1,2}(\s*\d{1,2}:\d{2})?', '', ty)
    ty = re.sub(r'[〜~]\s*', '', ty).strip()
    return (ty, t.get('url') or '')


old = events(subprocess.run(['git', 'show', '%s:index.html' % REV], capture_output=True).stdout.decode('utf-8'))
new = events(io.open('index.html', encoding='utf-8').read())

lines = []
lost_total = 0
for i, e in old.items():
    if i not in new:
        continue
    a = {key(t) for t in (e.get('tickets') or []) if visible(t)}
    b = {key(t) for t in (new[i].get('tickets') or []) if visible(t)}
    lost = a - b
    if lost:
        lost_total += len(lost)
        lines.append('id%-5s %s（見えていた %d → %d）' % (i, (e.get('name') or '')[:34], len(a), len(b)))
        for k in sorted(lost):
            lines.append('     消えた: %s | %s' % (k[0] or '(名前なし)', k[1] or 'URLなし'))

head = ['=== ヒール前後で画面から消えた枠（比較元 %s・today=%s）===' % (REV, TODAY),
        '消えたエントリ %d件 / 消えた枠 %d本' % (len(lines and [l for l in lines if l.startswith('id')]), lost_total), '']
io.open('tmp/heal_diff_0913.txt', 'w', encoding='utf-8').write('\n'.join(head + lines) + '\n')
print('\n'.join(head[:2]))
print('\n'.join(lines[:40]))
