# -*- coding: utf-8 -*-
"""id307 リアル恐竜ショー: 7月公演が終わり、生きている枠は8/1〜8/16の全国10公演だけ。
ev.date=7/31 のままだと画面から消える（reconcile ❌QC-EVDATE）ので千秋楽を8/16へ。
name「7月公演」/ venue「関東〜東北ツアー」/ dateLabel「7/18〜7/31 全9会場」も実態と食い違う
（大阪・福岡・兵庫・広島まで入った）ので実態に合わせる。"""
import re, json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

hit = 0
for e in E:
    if e['id'] != 307:
        continue
    print('before name=%s / date=%s / dateLabel=%s / venue=%s' % (e['name'], e['date'], e['dateLabel'], e['venue']))
    e['name'] = 'リアル恐竜ショー 恐竜パーク'
    e['date'] = '2026-08-16'
    e['dateLabel'] = '2026年8月1日(土)〜8月16日(日) 全10公演'
    e['venue'] = '全国ツアー'
    print('after  name=%s / date=%s / dateLabel=%s / venue=%s' % (e['name'], e['date'], e['dateLabel'], e['venue']))
    hit += 1

if hit != 1:
    print('!! 対象が %d 件。中止' % hit); sys.exit(1)

bak = 'index.html.bak_%s_fix307' % datetime.date.today().strftime('%m%d')
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== 適用 (backup: %s) ===' % bak)
