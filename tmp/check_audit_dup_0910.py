# -*- coding: utf-8 -*-
"""X投稿に出す3組の「未登録」13件が、本当に未登録かを確かめる。

🚨eventCd が違うだけで**同じ公演が既に載っている**ことがある
（[[feedback_tour_individual_url_dup]]／[[feedback_check_duplicates]]）。
公演日＋会場で突き合わせてから拾う。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
audit = json.load(io.open('tmp/x_audit_0911.json', encoding='utf-8'))


def norm(s):
    return re.sub(r'[\s　]', '', s or '')


def to_iso(d):
    m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', d or '')
    return '%s-%02d-%02d' % (m.group(1), int(m.group(2)), int(m.group(3))) if m else ''


for nm, hits in audit.items():
    miss = [x for x in hits if not x['registered']]
    if not miss:
        continue
    print('=' * 74)
    print('■ %s … ぴあで未登録に見えるもの %d件' % (nm, len(miss)))
    for x in miss:
        iso = to_iso(x['date'])
        venue = norm(re.sub(r'[（(].*', '', x['venue']))
        same = []
        for e in EVENTS:
            # 同じ公演日を持っているか（date か dateLabel か ticket.type に出る）
            blob = norm((e.get('name') or '') + (e.get('venue') or '')
                        + (e.get('dateLabel') or ''))
            if venue and venue[:8] in blob:
                same.append(e)
        mark = '❓すでに載っているかも' if same else '🚨ほんとうに未登録'
        print('  %s  %s / %s' % (mark, x['name'][:38], x['date'][:22]))
        print('      会場 %s' % x['venue'][:40])
        print('      %s' % x['url'])
        for e in same[:3]:
            print('      … 似ているエントリ id%-5d %s（公演%s）'
                  % (e['id'], (e.get('name') or '')[:30], e.get('date')))
    print()
