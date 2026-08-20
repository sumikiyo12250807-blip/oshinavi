# -*- coding: utf-8 -*-
"""再生成後の検算：予定枚数終了の行が末尾に正しい文言で入っているか／除外22件の内訳。"""
import re, sys, datetime
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_ai_page as B

today = datetime.date.today()
h = open('index.html', encoding='utf-8').read()
ssr = h[h.index('<!-- AI_SSR_START -->'):h.index('<!-- AI_SSR_END -->')]
lis = re.findall(r'<li>(.*?)</li>', ssr, re.S)
print('li総数', len(lis))

so = [(i, s) for i, s in enumerate(lis) if '予定枚数終了' in s]
print('予定枚数終了の行数', len(so), '／ 位置', [i for i, _ in so][:25])
print('--- 実文言(先頭3) ---')
for _, s in so[:3]:
    print(' ', s[:140])

print('--- 末尾5行 ---')
for s in lis[-5:]:
    print(' ', s[:100])

# 除外された子の内訳
evs = B.extract_events_array('index.html')
excl = [e for e in evs
        if B.next_action(e, today) is None and not B.soldout_visible(e, today)]
print('--- SSR除外', len(excl), '件（販売終了・公演日過ぎ） ---')
for e in excl[:25]:
    print(' id%-5s date=%-11s soldout枠=%d %s' % (
        e.get('id'), e.get('date'),
        sum(1 for t in (e.get('tickets') or []) if t.get('soldout')),
        (e.get('name') or e.get('artist'))[:38]))
