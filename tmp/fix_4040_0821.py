# -*- coding: utf-8 -*-
"""4040 WILD BLUE の県・会場の誤登録を直す。

発覚＝バッジ0の番人 → reconcile が「福岡 9/27 の一般発売」を MISSING で出したが、
登録側は同じ公演を「東京 9/27公演」として持っていた。
ぴあの実ページ（eventCd=2628178）＝**福岡県 福岡国際会議場 メインホール**。
キーワード検索でも WILD BLUE 名義の公演は 福岡9/27 と 広島10/12 の2つだけで、
登録 venue にあった「浜離宮朝日ホール」（東京）は実在しない混入だった。
  https://ticket.pia.jp/pia/event.do?eventCd=2628178
  https://t.pia.jp/pia/event/event.do?eventCd=2627191 （広島 10/12・受付終了）
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] != 4040:
        continue
    print('before venue     :', e.get('venue'))
    print('before prefecture:', e.get('prefecture'))
    e['venue'] = '全国ツアー（福岡国際会議場 メインホール／ウッドワンさくらぴあ 大ホール）'
    e['prefecture'] = '福岡・広島'
    for t in e['tickets']:
        if '東京 9/27公演' in (t.get('type') or ''):
            print('  ticket:', t['type'], '→ 福岡へ')
            t['type'] = t['type'].replace('東京 9/27公演', '福岡 9/27公演')
    e['verifiedAt'] = '2026-08-21'
    print('after  venue     :', e['venue'])
    print('after  prefecture:', e['prefecture'])
    for t in e['tickets']:
        print('   -', t['type'], '|', t.get('date'))
    n += 1

assert n == 1
shutil.copyfile('index.html', 'index.html.bak_0821_4040pref')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
