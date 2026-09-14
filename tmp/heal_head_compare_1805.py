# -*- coding: utf-8 -*-
"""ヒールのあと、HEAD と現物でエントリごとに「画面に出る枠」を突き合わせる（2026-09-14 夜）。
feedback_heal_flattens_ticket_types の手順どおり。券種名の日付部分（〜M/D・M/D発売）を落とし、
飛び先は売り場の番号で比べる＝「発売」→「〜締切」に書き換わっただけの枠は消えたと数えない。
出るのは「HEADで出ていて現物で消えた枠」があるエントリだけ。
使い方: python tmp/heal_head_compare_1805.py
"""
import datetime
import json
import re
import subprocess
import sys

sys.path.insert(0, 'tools')
import heal_stale_deadlines as H

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()


def events(text):
    return {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))}


head = events(subprocess.run(['git', 'show', 'HEAD:index.html'], capture_output=True).stdout.decode('utf-8'))
now = events(open('index.html', encoding='utf-8').read())
bad = 0
for i, e in sorted(head.items()):
    v_old = [t for t in e.get('tickets') or [] if H.visible_slot(t, TODAY)]
    n = now.get(i)
    if n is None:
        print('id%-5s %s ｜エントリごと無くなった（HEADで出ていた枠 %d）' % (i, (e.get('name') or '')[:30], len(v_old)))
        bad += 1
        continue
    v_new = [t for t in n.get('tickets') or [] if H.visible_slot(t, TODAY)]
    kn = {H.slot_key(t) for t in v_new}
    gone = [t for t in v_old if H.slot_key(t) not in kn]
    if gone:
        bad += 1
        print('id%-5s %s ｜%d枠→%d枠' % (i, (e.get('name') or '')[:30], len(v_old), len(v_new)))
        for t in gone:
            print('   - %s ｜%s%s' % (t.get('type'), H._url_id(t.get('url')), '｜売り切れ' if t.get('soldout') else ''))
print('\n枠が消えたエントリ %d件（全 %d件中）' % (bad, len(head)))
