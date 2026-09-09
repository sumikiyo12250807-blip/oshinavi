# -*- coding: utf-8 -*-
"""統合で dateLabel の会期が**縮んでいない**かを、コミット前と突き合わせて確かめる。

🚨ラベルの後ろ側は「〜12月25日」と年を書かないことがあるので、
   年つきしか読まない実装だと千秋楽を読み落として会期を縮める
   （[[feedback_show_true_dates_not_sellable_range]]＝事実の会期を縮めない）。
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = sys.argv[1] if len(sys.argv) > 1 else 'HEAD~1'


def load(text):
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', text, re.S)
    return {e['id']: e for e in json.loads(m.group(2))}


def days(lbl):
    out, y = [], None
    for a, b, c in re.findall(r'(?:(\d{4})年)?\s*(\d{1,2})月(\d{1,2})日', lbl or ''):
        if a:
            y = int(a)
        if y:
            out.append('%04d-%02d-%02d' % (y, int(b), int(c)))
    return out


old = load(subprocess.run(['git', 'show', '%s:index.html' % BASE],
                          capture_output=True).stdout.decode('utf-8', 'replace'))
new = load(open('index.html', encoding='utf-8').read())

bad = []
for i, e in old.items():
    if i not in new:
        continue
    a, b = days(e.get('dateLabel')), days(new[i].get('dateLabel'))
    if not a or not b:
        continue
    if max(b) < max(a) or min(b) > min(a):
        bad.append((i, e.get('name', '')[:34], e.get('dateLabel'), new[i].get('dateLabel')))

print('%s と比べて会期が縮んだエントリ: %d件' % (BASE, len(bad)))
for i, n, o, w in bad:
    print('  id=%-5s %s\n     前: %s\n     後: %s' % (i, n, o, w))
