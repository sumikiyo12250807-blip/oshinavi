# -*- coding: utf-8 -*-
"""gate_fany_report.txt の食い違いを「今日(9/21)以前の公演だけの話」と「これからの公演に関わる話」に分ける（読むだけ・9/21夜）。
今日の公演の分＝売り場が夕方に販売終了へ変えただけ・明朝の削除で消える。これからの公演の分＝本当に直す枠。"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = (9, 21)
blocks = re.split(r'\n(?=--- )', io.open('tmp/gate_fany_report.txt', encoding='utf-8').read())
past, future = [], []
for b in blocks[1:]:
    lines = [l for l in b.split('\n') if l.strip().startswith('只')]
    fut = []
    for l in lines:
        m = re.search(r'（\S+ (?:R\d+年 )?(\d{1,2})/(\d{1,2})', l)
        if m and (int(m.group(1)), int(m.group(2))) > TODAY:
            fut.append(l.strip())
        elif m and int(m.group(1)) < 9 and 'R9' in l:
            fut.append(l.strip())
    (future if fut else past).append((b.split('\n')[0], fut))
print('今日以前の公演だけ %d件 ／ これからの公演に関わる %d件' % (len(past), len(future)))
for head, fut in future:
    print(head)
    for l in fut:
        print('   ', l)
