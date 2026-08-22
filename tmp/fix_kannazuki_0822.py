# -*- coding: utf-8 -*-
"""神奈月 ソロライブツアーが3エントリに割れていたのを1つに畳む（2026-08-22・ユーザー指示「神奈月は畳んで」）。

割れていたもの＝4419(bundle・愛知/大阪プレリザーブ)／4628(名古屋 11/15)／4965(大阪 11/7・新着プール)。
3つとも別の販売枠を持っていたので、**3つのURL全部を渡して build_pia_entries でゼロから再導出**した
（[[feedback_bundle_full_rederive]]／[[feedback_tour_consolidate]]＝ツアーは1エントリ）。

再導出の副産物＝**東京公演（日経ホール 11/21〜11/22・一般発売 10/3 10:00）がどこにも登録されていなかった**
のを回収。枠は 3 → 5 に増える。枠ごとに飛び先URLを持たせる（[[feedback_tour_per_ticket_url]]）。
name は既存の分かりやすい表記を残す（buildが返す "神奈月" では何の公演か分からない）。
"""
import json
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

built = json.load(open('tmp/kan_built.json', encoding='utf-8'))[0]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

e = by[4419]
print('統合前: 4419 枠%d / 4628 枠%d / 4965 枠%d'
      % (len(e['tickets']), len(by[4628]['tickets']), len(by[4965]['tickets'])))

e['tickets'] = built['tickets']
for k in ('venue', 'prefecture', 'date', 'dateLabel'):
    e[k] = built[k]
e['verifiedAt'] = '2026-08-22'
print('統合後: 4419 枠%d / 千秋楽 %s / %s' % (len(e['tickets']), e['date'], e['venue']))
for t in e['tickets']:
    print('  -', t['type'])

shutil.copyfile('index.html', 'index.html.bak_0822_kannazuki')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])

# 畳んだ2件は欠番にする（idは詰めない＝[[feedback_new_list_order_lock]]）
r = subprocess.run([sys.executable, 'tools/delete_entries.py', '--file', 'index.html',
                    '--ids', '4628,4965'], capture_output=True, text=True, encoding='utf-8')
print(r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr)
