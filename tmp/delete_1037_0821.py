# -*- coding: utf-8 -*-
"""1037 おどる絵本『みえるとか みえないとか』を削除する（ユーザー判断 2026-08-21「消していいよ」）。

朝の削除ゲートでは「水戸芸術館9/5-6が残っている」ので保留にしたが、
**販売終了日がどこにも明記されていない**（一般発売6/6 9:30〜としか書かれていない）ため
チケット枠を作れず、「カードは出るが買える枠0」の状態になる。
状況を説明したうえでユーザーが「消していい」と判断した。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
gone = [e for e in EVENTS if e['id'] == 1037]
assert len(gone) == 1
print('削除 id=1037 %s | %s | %s' % (gone[0].get('name'), gone[0].get('venue'), gone[0].get('date')))
KEEP = [e for e in EVENTS if e['id'] != 1037]

io.open('tmp/deleted_1037.json', 'w', encoding='utf-8').write(json.dumps(gone, ensure_ascii=False, indent=1))
shutil.copyfile('index.html', 'index.html.bak_0821_del1037')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(KEEP, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== %d件 → %d件 ===' % (len(EVENTS), len(KEEP)))
