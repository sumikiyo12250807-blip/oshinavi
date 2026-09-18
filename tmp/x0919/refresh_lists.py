# -*- coding: utf-8 -*-
"""post04〜09 のリスト部分だけを、作り直した素材で置き換える（2026-09-18 夜）。

なぜ＝振り分け2,032件とぴあの足し込みで**まとめの対象が増えた**ので、
Fableが書いた時点のリストには無い行が64行出た。**投稿に無い行＝着地しても見つからない行**。
文章（前置き・リスト直後の一言・締め）は1文字も触らない。**入れ替えるのはリストの行だけ。**

🚨「?」（発売時刻が読めない行）は、**同じ名前が時刻付きで同じブロックに居るなら捨てる**
   ＝同じ枠の別表記なので二重に出る（クーザ／名古屋港水族館／KAZUYOSHI SAITOで実際に出た）。
   時刻付きが居ない場合は残す（落とすと本当に消える）。

  python tmp/x0919/refresh_lists.py [--apply]
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

LINE = re.compile(r'^((?:\d{1,2}:\d{2})|時刻未定|\?) (.+)／([^／]+?)(（先行）)?$')
DAYHEAD = re.compile(r'^【(\d+/\d+)\([日月火水木金土]\)発売】')
MAP = {1: 'post04', 2: 'post05', 3: 'post06', 4: 'post07', 5: 'post08', 6: 'post09'}

mat = io.open('tmp/x0919/material.md', encoding='utf-8').read()
blocks, cur, day = {}, None, None
for ln in mat.split('\n'):
    m = re.match(r'## まとめ枠 (\d+)：', ln)
    if m:
        cur, day = int(m.group(1)), None
        blocks[cur] = {}
        continue
    m = DAYHEAD.match(ln)
    if m:
        day = m.group(1)
        if cur is not None:
            blocks[cur][day] = []
        continue
    if cur is not None and day and LINE.match(ln):
        blocks[cur][day].append(ln)


def drop_dup_unknown(rows):
    """時刻付きで同じ名前が居る「?」行を捨てる。"""
    unknown = ('?', '時刻未定')
    timed = {LINE.match(r).group(2) for r in rows if LINE.match(r).group(1) not in unknown}
    return [r for r in rows
            if not (LINE.match(r).group(1) in unknown and LINE.match(r).group(2) in timed)]


total_add, total_del = 0, 0
for gi, days in sorted(blocks.items()):
    path = 'tmp/x0919/%s.txt' % MAP[gi]
    lines = io.open(path, encoding='utf-8').read().split('\n')
    out, i, day = [], 0, None
    while i < len(lines):
        ln = lines[i]
        m = DAYHEAD.match(ln)
        if m:
            day = m.group(1)
            out.append(ln)
            i += 1
            # 続くリスト行を読み捨てて、素材の行に差し替える
            old = []
            while i < len(lines) and LINE.match(lines[i]):
                old.append(lines[i])
                i += 1
            new = drop_dup_unknown(blocks[gi].get(day, old))
            out += new
            total_add += len([r for r in new if r not in old])
            total_del += len([r for r in old if r not in new])
            continue
        out.append(ln)
        i += 1
    txt = '\n'.join(out)
    print('%s ｜足した %d行・外した %d行' % (MAP[gi],
                                        len([1 for r in out if LINE.match(r)]) - len([1 for r in lines if LINE.match(r)]),
                                        0))
    if APPLY:
        io.open(path, 'w', encoding='utf-8', newline='').write(txt)

print('\n差し替えた行＝足し %d / 外し %d （--apply で書き込み）' % (total_add, total_del)
      if not APPLY else '\n書き込み完了（足し %d / 外し %d）' % (total_add, total_del))
