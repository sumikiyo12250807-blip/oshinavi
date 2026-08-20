# -*- coding: utf-8 -*-
"""2866 The BONEZ／SHADOWS の裏取りできない枠を落とす（エントリは残す）。
登録の「一般発売 8/15 10:00発売」は4ルートで確認できなかった＝
  ぴあ b2669921（プレリザーブ受付終了のみ）／e+キーワード検索／公式ニュース／e+特設 eplus.jp/dys-tour/
公演(9/1盛岡・9/3仙台)は実在するので、将来一般発売が出たら拾い直せるようエントリは残す。
  python tmp/fix_2866.py [--apply]
"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

h = open('index.html', encoding='utf-8').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(mm.group(2))
e = {x['id']: x for x in EVENTS}[2866]

before = len(e['tickets'])
e['tickets'] = [t for t in e['tickets'] if '8/15 10:00発売' not in (t.get('type') or '')]
print('2866 枠 %d → %d' % (before, len(e['tickets'])))
e['unverifiedNote'] = '一般発売の告知がぴあ/e+/公式のいずれにも無いため枠を保留（2026-08-15確認）'

if APPLY:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:mm.start()] + mm.group(1) + new_arr + mm.group(3) + h[mm.end():])
    print('適用しました')
