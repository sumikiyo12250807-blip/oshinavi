# -*- coding: utf-8 -*-
"""「同じ公演日の古い発売の枠」が印なしで残っている形に売り切れの印を付ける（2026-09-16）。
soldbadge_add_0916 が「もう枠がある＝足さない」とした行のうち、その枠が
  ・M/D HH:MM発売 の古い形で、締切（date）が今日より前＝画面から消えている隠れ枠
  ・印がまだ無い
  ・券種の頭の言葉（一般発売・先行…）と、紙/電子の別がぴあの「予定枚数終了」の行と同じ
なら soldout を付ける（feedback_soldout_keep_visible＝startDate==date の隠れ枠で当日完売したものは印を付けて出す）。
ぴあの行は tmp/sb_cache_0916（soldbadge_list_0916 が読んだキャッシュ）から読む＝ぴあは叩かない。
使い方: python tmp/mark_hidden_sold_0916.py [--apply]
"""
import datetime
import glob
import io
import json
import re
import shutil
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
P = 'index.html'


def nf(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or ''))


def pref_short(p):
    p = p or ''
    return p if p == '北海道' else re.sub(r'[都府県]$', '', p)


def md(d):
    y, m, dd = d.split('-')
    return ('R9年 ' if y == '2027' else '') + '%d/%d' % (int(m), int(dd))


def head_word(s):
    return re.split(r'[＜<【\[（(／/\s]', nf(s))[0]


def kind(s):
    s = nf(s)
    return '紙' if '紙' in s else ('電子' if '電子' in s else '')


items = []
for ln in io.open('tmp/soldbadge_in_0916.txt', encoding='utf-8').read().splitlines():
    m = re.match(r'^id(\d+) 印なし: ぴあ「予定枚数終了」公演([\d\-]+)「(.*)」 (https?://\S+)$', ln.strip())
    if m:
        items.append((int(m.group(1)), m.group(2), m.group(3)))

src = io.open(P, encoding='utf-8', newline='').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(mm.group(2))
by = {e['id']: e for e in events}
marked = []
for eid, pdate, title in items:
    e = by.get(eid)
    if not e:
        continue
    core_day = md(pdate)
    for t in e['tickets']:
        ty = t.get('type') or ''
        if t.get('soldout') or not re.search(r'\d{1,2}:\d{2}発売$', ty) or (t.get('date') or '') >= TODAY:
            continue
        cm = re.search(r'（([^（）]*?) ((?:R\d+年\s*)?\d{1,2}/\d{1,2})(?:〜[^（）]*)?公演）', ty)
        if not cm or cm.group(2) != core_day:
            continue
        if head_word(ty) != head_word(title) or kind(ty) != kind(title):
            continue
        t['soldout'] = True
        t['soldoutSince'] = TODAY
        marked.append((eid, ty))
        print('🔴 id%-5s %s → 予定枚数終了の印（ぴあ「%s」）' % (eid, ty[:52], title[:30]))
print('印を付けた %d枠' % len(marked))
if '--apply' in sys.argv and marked:
    shutil.copyfile(P, 'index.html.bak_0916_hiddensold')
    out = src[:mm.start()] + mm.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + mm.group(3) + src[mm.end():]
    io.open(P, 'w', encoding='utf-8', newline='').write(out)
    print('書き込んだ')
