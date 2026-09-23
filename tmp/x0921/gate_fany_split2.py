# -*- coding: utf-8 -*-
"""gate_fany_report.txt の食い違いを、只ページ側／只登録側 × 今日以前／これからの公演 で数える（読むだけ・9/21夜・投入後）。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = (9, 21)
blocks = re.split(r'\n(?=--- )', io.open('tmp/gate_fany_report.txt', encoding='utf-8').read().split('\n=== 一覧から落ちた')[0])
cnt = {}
fut_blocks = []
for b in blocks[1:]:
    fut = []
    for l in b.split('\n'):
        l = l.strip()
        if not l.startswith('只'):
            continue
        side = 'page' if l.startswith('只ページ') else 'reg'
        m = re.search(r'（\S+ (R\d+年 )?(\d{1,2})/(\d{1,2})', l)
        if not m:
            k = (side, 'unknown')
        elif m.group(1) or (int(m.group(2)), int(m.group(3))) > TODAY:
            k = (side, 'future')
        else:
            k = (side, 'past_or_today')
        cnt[k] = cnt.get(k, 0) + 1
        if k[1] != 'past_or_today':
            fut.append(l)
    if fut:
        fut_blocks.append((b.split('\n')[0], fut))
print('lines:', cnt)
print('blocks total %d / with future-or-unknown lines %d' % (len(blocks) - 1, len(fut_blocks)))
for head, fut in fut_blocks:
    print(head)
    for l in fut:
        print('   ', l)
