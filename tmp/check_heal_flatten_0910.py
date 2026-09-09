# -*- coding: utf-8 -*-
"""ヒール適用の前後で「画面に出る枠」の数を突合する（DELETE_GATE 5章）。

heal_stale_deadlines.py --apply の安全弁は**公演単位**でしか比べないので、
同じ公演の券種違いを丸ごと潰しても気づかない（2026-09-01 阪神×広島が12枠→1枠）。
券種名は「9/1 10:00発売」→「〜12/20 23:59」に書き換わるので、**日付部分を落として**数える。
"""
import datetime
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()


def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'):
        return True
    sd, d = t.get('startDate'), t.get('date')
    return not ((not sd or sd <= TODAY) and (d or '') < TODAY)


def load(text):
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', text, re.S)
    return {e['id']: e for e in json.loads(m.group(2))}


def main():
    base = sys.argv[1] if len(sys.argv) > 1 else 'HEAD'
    old_txt = subprocess.run(['git', 'show', '%s:index.html' % base],
                             capture_output=True).stdout.decode('utf-8', 'replace')
    old = load(old_txt)
    new = load(open('index.html', encoding='utf-8').read())

    rows = []
    for i, e in old.items():
        if i not in new:
            continue
        a = sum(1 for t in (e.get('tickets') or []) if visible(t))
        b = sum(1 for t in (new[i].get('tickets') or []) if visible(t))
        if b < a:
            rows.append((i, e.get('artist') or e.get('name'), a, b))

    rows.sort(key=lambda r: r[2] - r[3], reverse=True)
    print('%s と比べて「画面に出る枠」が減ったエントリ: %d件' % (base, len(rows)))
    for i, n, a, b in rows[:40]:
        print('  id=%-5s %-34s %d枠 → %d枠 (-%d)' % (i, (n or '')[:34], a, b, a - b))
    tot_old = sum(1 for e in old.values() for t in (e.get('tickets') or []) if visible(t))
    tot_new = sum(1 for e in new.values() for t in (e.get('tickets') or []) if visible(t))
    print('\n全体の見える枠: %d → %d' % (tot_old, tot_new))


if __name__ == '__main__':
    main()
