# -*- coding: utf-8 -*-
"""新着プール（genre:"new"）の投入後QC。
 ① 全角ローマ字/数字が残っていないか（feedback_newpool_fullwidth_halfwidth・（）／〜は保護）
 ② NEW_ORDER が新着idを全部持っているか（feedback_new_order_array）
 ③ CRLF・件数
"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
new = [e for e in E if e.get('genre') == 'new']
print('総件数 %d / genre:new %d件' % (len(E), len(new)))

FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')
bad = []
for e in new:
    for key in ('artist', 'name', 'venue', 'dateLabel'):
        if FW.search(e.get(key) or ''):
            bad.append((e['id'], key, e[key][:50]))
    for t in e.get('tickets') or []:
        if FW.search(t.get('type') or ''):
            bad.append((e['id'], 'ticket', t['type'][:50]))
print('全角ローマ字/数字の残り: %d件' % len(bad))
for b in bad[:20]:
    print('   id%s %s %s' % b)

mo = re.search(r'const NEW_ORDER = (\[[^\]]*\])', h)
order = json.loads(mo.group(1)) if mo else []
ids = [e['id'] for e in new]
missing = [i for i in ids if i not in order]
print('NEW_ORDER %d件 / 新着で未登録 %d件 %s' % (len(order), len(missing), missing[:10]))
print('NEW_ORDERは id昇順か:', order == sorted(order))

d = open('index.html', 'rb').read()
print('CRLF %d / LFonly %d' % (d.count(b'\r\n'), d.count(b'\n') - d.count(b'\r\n')))
