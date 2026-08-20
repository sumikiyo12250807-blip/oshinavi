# -*- coding: utf-8 -*-
import re, io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = open('index.html', encoding='utf-8').read()

# 各エントリの "tickets": [ ... ] を新しい配列で置換する
NEW = {
 1352: [
   {"type": "一般発売（岩手 7/25公演）〜7/16 23:59", "date": "2026-07-16"},
   {"type": "一般発売（岩手 7/26公演）〜7/16 23:59", "date": "2026-07-16"},
 ],
 1338: [
   {"type": "一般発売（愛知 6/27公演）〜6/26 23:59", "date": "2026-06-26"},
   {"type": "当日引換券販売（大阪 6/28公演）〜6/27 23:59", "date": "2026-06-27"},
   {"type": "一般発売（宮城 7/4公演）〜7/3 23:59", "date": "2026-07-03"},
   {"type": "一般発売（福岡 7/10公演）〜7/1 23:59", "date": "2026-07-01"},
   {"type": "一般発売（千葉 7/12公演）〜7/2 23:59", "date": "2026-07-02"},
   {"type": "一般発売（東京 7/19公演）〜7/9 23:59", "date": "2026-07-09"},
   {"type": "一般発売（広島 7/25公演）〜7/16 23:59", "date": "2026-07-16"},
 ],
 1347: [
   {"type": "一般発売〈夏祭り〉（東京 8/1〜8/12公演）〜8/12 16:00", "date": "2026-08-12"},
   {"type": "一般発売〈夜祭り 特撮ジャズバー〉（東京 8/3〜8/9公演）6/26 18:00発売",
    "startDate": "2026-06-26", "date": "2026-06-26"},
 ],
}

def entry_span(id):
    m = re.search(r'\{\s*"id":\s*%d,' % id, src)
    i = m.start(); d = 0; j = i
    while True:
        if src[j] == '{': d += 1
        elif src[j] == '}':
            d -= 1
            if d == 0: return (i, j+1)
        j += 1

def fmt_tickets(tks):
    # 6スペースで各要素(エントリは4スペースキー、ticketは6スペース)
    out = ['      "tickets": [']
    for k, t in enumerate(tks):
        j = json.dumps(t, ensure_ascii=False, indent=2)
        body = '\n'.join('        ' + ln for ln in j.split('\n'))
        out.append(body + (',' if k < len(tks)-1 else ''))
    out.append('      ]')
    return '\n'.join(out)

# 高いidから処理(オフセット維持)
for id in sorted(NEW, reverse=True):
    s, e = entry_span(id)
    blk = src[s:e]
    # blk内の "tickets": [ ... ] を置換 (bracket counting)
    tm = re.search(r'\n\s*"tickets":\s*\[', blk)
    ts = tm.start()
    # find matching ]
    p = blk.index('[', tm.start()); depth = 0; q = p
    while True:
        if blk[q] == '[': depth += 1
        elif blk[q] == ']':
            depth -= 1
            if depth == 0: break
        q += 1
    newblk = blk[:ts] + '\n' + fmt_tickets(NEW[id]) + blk[q+1:]
    src = src[:s] + newblk + src[e:]
    print('fixed', id)

# 妥当性
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', src, re.S)
arr = json.loads(m.group(1))
print('EVENTS parse OK, 件数', len(arr))
open('index.html', 'w', encoding='utf-8').write(src)
