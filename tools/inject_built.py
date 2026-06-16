# -*- coding: utf-8 -*-
"""完成済みエントリ(tmp/all_new.json)をindex.htmlのEVENTS配列末尾に投入し、
NEW_ORDERを投入id昇順で更新する。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

allnew = json.load(open('tmp/all_new2.json', encoding='utf-8'))
src = open('index.html', encoding='utf-8').read()

# 各エントリを2スペース余分にインデントして直列化（既存と同じ字下げ）
def ser(e):
    body = json.dumps(e, ensure_ascii=False, indent=2)
    return '\n'.join('  ' + ln for ln in body.split('\n'))

entries_text = ',\n'.join(ser(e) for e in allnew)

anchor = '  }\n];;;;;;;;'
assert src.count(anchor) == 1, 'anchor count=%d' % src.count(anchor)
src = src.replace(anchor, '  },\n' + entries_text + '\n];;;;;;;;')

new_ids = sorted(e['id'] for e in allnew)
no_new = '[' + ', '.join(str(i) for i in new_ids) + ']'
src, n = re.subn(r'(NEW_ORDER\s*=\s*)\[[0-9,\s]*\]', r'\g<1>' + no_new, src, count=1)
assert n == 1, 'NEW_ORDER replaced=%d' % n

open('index.html', 'w', encoding='utf-8').write(src)
print('投入 %d件 id%d..%d / NEW_ORDER更新(%d件)' % (len(allnew), new_ids[0], new_ids[-1], len(new_ids)))
