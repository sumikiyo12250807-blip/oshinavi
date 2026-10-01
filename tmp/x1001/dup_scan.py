# -*- coding: utf-8 -*-
"""同じ日・同じ会場で、名前から時刻・数字・部の印・回の印を外すと同じになる組を洗い出す（読むだけ）→ tmp/x1001/dup_scan.txt
FANY（1公演1エントリ）とスポーツ（ホーム/アウェイ）は外す"""
import io, json, re, sys, unicodedata
from collections import defaultdict
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import fold_parts as FP
s = io.open(r'C:\Users\user\oshinavi\index.html', encoding='utf-8').read()
i = s.index('const EVENTS = [') + len('const EVENTS = ')
E, _ = json.JSONDecoder().raw_decode(s[i:])


def key_name(n):
    n = unicodedata.normalize('NFKC', n or '')
    n = FP.PART.sub('', n)
    n = re.sub(r'\d{1,2}[:：]\d{2}', '', n)
    n = re.sub(r'(昼|夜|朝|午前|午後|マチネ|ソワレ|第?\d+回目?|回|部|①|②|③|④|⑤|1st|2nd|3rd|part\.?\d+|vol\.?\d+|day\s*\d+)', '', n, flags=re.I)
    n = re.sub(r'[\d\s　〜～~\-－・/／()（）【】\[\]「」『』<>＜＞:：!！?？.,、。]', '', n)
    return n.lower()


g = defaultdict(list)
for e in E:
    if FP.is_fany(e) or e.get('genre') == 'sports':
        continue
    k = key_name(e.get('name'))
    if len(k) < 4:
        continue
    g[(k, e.get('date'), (e.get('venue') or '').strip())].append(e)
out = io.open(r'C:\Users\user\oshinavi\tmp\x1001\dup_scan.txt', 'w', encoding='utf-8')
n = 0
for k, v in sorted(g.items(), key=lambda kv: kv[1][0]['id']):
    if len(v) < 2:
        continue
    n += 1
    out.write(f"== 組{n} {k[1]} {k[2][:30]}\n")
    for e in sorted(v, key=lambda e: e['id']):
        out.write(f"   {e['id']} [{e.get('genre')}] {e.get('name')} | {e.get('dateLabel')}\n")
out.write(f'組 {n}\n')
print(n)
