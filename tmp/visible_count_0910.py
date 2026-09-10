# -*- coding: utf-8 -*-
"""ヒールの前後で「画面に出ている枠」の数を数えて突き合わせる。

[[feedback_heal_flattens_ticket_types]]＝ヒール自身の安全弁は
「同じ公演の券種違いが丸ごと消える」型を拾えない。だから外から数える。
🚨券種名の日付部分だけ書き換わった枠を「消えた」と数えない。
"""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = '2026-09-10'


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '9999') < TODAY)


def skel(ty):
    """日付・時刻を落として券種の骨だけにする"""
    s = re.sub(r'(?:R\d+年\s*)?\d{1,2}/\d{1,2}', '', ty or '')
    s = re.sub(r'\d{1,2}:\d{2}', '', s)
    return re.sub(r'[〜～\s発売開始予定]', '', s)


def load(text):
    ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))
    return {e['id']: e for e in ev}


def counts(d):
    out = {}
    for i, e in d.items():
        vs = [t for t in (e.get('tickets') or []) if visible(t)]
        out[i] = (len(vs), sorted(skel(t.get('type')) + '|' + (t.get('url') or '') for t in vs))
    return out


base = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
old = load(subprocess.run(['git', 'show', base + ':index.html'],
                          capture_output=True).stdout.decode('utf-8', 'replace'))
new = load(io.open('index.html', encoding='utf-8').read())
co, cn = counts(old), counts(new)

lost = []
for i, (n, keys) in co.items():
    if i not in cn:
        lost.append((i, n, 0, ['(エントリごと消えた)']))
        continue
    n2, keys2 = cn[i]
    gone = [k for k in keys if k not in keys2]
    if gone:
        lost.append((i, n, n2, gone))

print('比較元 %s / 対象 %d件' % (base, len(co)))
if not lost:
    print('OK: 画面に出ていた枠が消えたエントリは 0 件')
else:
    print('🚨 枠が消えたエントリ %d件' % len(lost))
    for i, a, b, gone in lost[:25]:
        e = new.get(i) or old.get(i)
        print('  id%-5d %d→%d  %s' % (i, a, b, (e.get('name') or '')[:36]))
        for g in gone[:6]:
            print('        - %s' % g[:110])
