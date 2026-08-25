# -*- coding: utf-8 -*-
"""id=5181 劇団四季『ロボット・イン・ザ・ガーデン』
8/24に1月分(eventCd=2626471)を2月分のエントリへ畳んだのに、
artist/name/dateLabel が「2027年2月」のままで1月公演が説明から落ちていた。
実ページ確認済＝1月分は 受付中・公演2027/1/1〜1/31・締切2027/1/29（自由劇場）。
長期公演は1エントリ・dateは千秋楽（[[feedback_longrun_event]]）。
"""
import io, re, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

path = 'index.html'
s = io.open(path, encoding='utf-8', newline='').read()

m = re.search(r'"id":\s*5181\s*,', s)
assert m
i = s.rfind('{', 0, m.start())
depth = 0
for j in range(i, len(s)):
    if s[j] == '{': depth += 1
    elif s[j] == '}':
        depth -= 1
        if depth == 0: break
block = s[i:j + 1]

W = '月火水木金土日'
def lab(d):
    dt = datetime.date.fromisoformat(d)
    return '%d年%d月%d日(%s)' % (dt.year, dt.month, dt.day, W[dt.weekday()])

old_name = '劇団四季『ロボット・イン・ザ・ガーデン』2027年2月／東京'
new_name = '劇団四季『ロボット・イン・ザ・ガーデン』／東京'
assert block.count(old_name) == 2, block.count(old_name)
block2 = block.replace(old_name, new_name)

old_dl = '"dateLabel": "2027年2月2日(火)〜2027年2月12日(金) 東京 自由劇場"'
new_dl = '"dateLabel": "%s〜%s 東京 自由劇場"' % (lab('2027-01-01'), lab('2027-02-12'))
assert old_dl in block2, '既存のdateLabelが違う'
block2 = block2.replace(old_dl, new_dl)

s2 = s[:i] + block2 + s[j + 1:]
assert '\r\r\n' not in s2
io.open(path, 'w', encoding='utf-8', newline='').write(s2)
print('name  :', new_name)
print('label :', new_dl)
print('CRLF', s2.count('\r\n'), 'bareLF', len(re.findall(r'(?<!\r)\n', s2)))
