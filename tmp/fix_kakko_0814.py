# -*- coding: utf-8 -*-
"""〈〉化けバッジの修復。
「一般発売〈11【13（金）公演〉】（東京 11/13公演）」→「一般発売（東京 11/13公演）」
化けた囲みは公演日の重複表示でしかない（正しい公演日は（県 M/D公演）側に入っている）。
真因はツール側で修正済（_kenshu_base に 〈…〉 を追加・selftest 3ケース）。ここは既存データの後始末。
index.html は CRLF なので newline='' で読み書きする（memory: feedback_index_html_crlf_preserve）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

# 〈 数字 【 数字 （曜日）? 公演 〉 】 の形だけを狙い撃ち（正常な〈1日券〉〈動画配信〉は触らない）
BAD = re.compile(r'〈[0-9]{1,2}【[0-9]{1,2}(?:（[月火水木金土日祝]）)?公演〉】')

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))

fixed = []
for e in EV:
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        if BAD.search(ty):
            new = BAD.sub('', ty)
            new = re.sub(r'\s{2,}', ' ', new).strip()
            fixed.append((e['id'], e.get('name'), ty, new))
            t['type'] = new

print('修復', len(fixed), '件')
for r in fixed:
    print('  id%-5s %s' % (r[0], (r[1] or '')[:34]))
    print('     旧:', r[2])
    print('     新:', r[3])

if fixed and '--apply' in sys.argv:
    # inject_built.py と同じ書き戻し方式（EVENTS配列まるごとjson.dumps・改行はNLに揃える）
    NL = '\r\n' if '\r\n' in h else '\n'
    new_arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
    open('index.html.bak_0814_kakko', 'w', encoding='utf-8', newline='').write(h)
    open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('→ index.html に適用（backup index.html.bak_0814_kakko）')
else:
    print('（--apply で適用）')
