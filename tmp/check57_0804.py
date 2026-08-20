# -*- coding: utf-8 -*-
"""新着プール57件の独立チェック（8/4）。

A) 独立再取得＝別系統 tools/pia_tickets.py で実ページを引き直し、登録値と突合
   （投入値にアンカリングしない＝[[feedback_verify_independent_not_anchored]]）
B) 静的QC＝①全角ローマ字/数字の残り ②空カッコ会場 ③締切>公演日のcap逆転
   ④公演日が過去 ⑤既存エントリとの名前重複 ⑥ジャンル下書きが空/ぴあカテゴリ無し

結果はUTF-8ファイルに出す（コンソールに日本語を出さない＝[[feedback_no_mojibake_japanese_read]]）。
"""
import io
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
new = [e for e in EVENTS if e.get('genre') == 'new']
old = [e for e in EVENTS if e.get('genre') != 'new']

CACHE_F = os.path.join(ROOT, 'tmp', 'indep_cache_0804.json')
cache = json.load(io.open(CACHE_F, encoding='utf-8')) if os.path.exists(CACHE_F) else {}


def fetch(u):
    if u in cache:
        return cache[u]
    r = subprocess.run([sys.executable, 'tools/pia_tickets.py', u, '--json'],
                       capture_output=True, cwd=ROOT)
    try:
        d = json.loads(r.stdout.decode('utf-8'))
    except Exception:
        d = [{'_error': (r.stdout + r.stderr).decode('utf-8', 'replace')[:200]}]
    cache[u] = d
    time.sleep(1.2)
    return d


DT = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*(?:朝|昼|夜|夕|深夜)?\s*(\d{1,2}):(\d{2})')


def md(m):
    return '%d/%d' % (int(m.group(2)), int(m.group(3)))


def mdhm(m):
    return '%d/%d %d:%02d' % (int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5)))


def real_window(w):
    ms = list(DT.finditer(w))
    if not ms:
        return None, None
    if '～' in w or '〜' in w:
        head = w.split('～')[0].split('〜')[0]
        if DT.search(head):
            return mdhm(ms[0]), (md(ms[1]) if len(ms) > 1 else None)
        return None, md(ms[0])
    if 'より発売' in w or '発売' in w:
        return mdhm(ms[0]), None
    return None, md(ms[0])


def reg_window(t):
    typ = t.get('type', '')
    m = re.search(r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})\s*(?:発売開始|発売予定|発売|販売開始|受付開始)\s*$', typ)
    start = '%d/%d %d:%02d' % tuple(int(x) for x in m.groups()) if m else None
    end_badge = re.search(r'〜\s*(\d{1,2})/(\d{1,2})(?:\s+\d{1,2}:\d{2})?\s*$', typ)
    dd = t.get('date') or ''
    dm = '%d/%d' % (int(dd[5:7]), int(dd[8:10])) if len(dd) == 10 else None
    return start, dm, (end_badge is not None)


BUY = ('受付中', '発売前', '販売期間中', '抽選受付', '先着')
TODAY = '2026-08-04'
FW = re.compile(r'[Ａ-Ｚａ-ｚ０-９]')


def norm_name(s):
    return re.sub(r'[\s　]+', '', unicodedata.normalize('NFKC', s or '')).lower()


exist_names = {}
for e in old:
    exist_names.setdefault(norm_name(e.get('artist')), []).append(e['id'])

ngA, ngB, lines = [], [], []
lines.append('=== A) 独立再取得での突合（別系統 pia_tickets.py） ===')
for e in new:
    urls = []
    p = (e.get('links') or {}).get('pia')
    if p:
        urls.append(p)
    for t in e.get('tickets') or []:
        if t.get('url') and t['url'] not in urls:
            urls.append(t['url'])
    got, err = [], []
    for u in urls:
        d = fetch(u)
        if d and isinstance(d[0], dict) and d[0].get('_error'):
            err.append(d[0]['_error'])
            continue
        for c in d:
            if any(b in (c.get('state') or '') for b in BUY):
                k = (c.get('title'), c.get('when'), c.get('perfdate'), c.get('pref'))
                if k not in [g[0] for g in got]:
                    got.append((k, c))
    regs = e.get('tickets') or []
    msgs = []
    if err:
        msgs.append('取得エラー %s' % err[0][:60])
    if len(got) != len(regs):
        msgs.append('枠数 登録%d ⇄ 実%d' % (len(regs), len(got)))
    real = sorted(str(real_window(c.get('when') or '')) for _, c in got)
    reg = []
    for t in regs:
        s, dm, has_end = reg_window(t)
        reg.append(str((s, dm if (has_end or s is None) else (dm if dm != (s.split(' ')[0] if s else None) else None))))
    if real != sorted(reg):
        msgs.append('日時 登録%s ⇄ 実%s' % (sorted(reg), real))
    if msgs:
        ngA.append(e['id'])
        lines.append('')
        lines.append('❌ id%d %s' % (e['id'], (e.get('name') or '')[:40]))
        for m in msgs:
            lines.append('     ' + m)
        for _, c in got:
            lines.append('     [実] %s | %s | %s' % (c.get('state'), (c.get('title') or '')[:40], c.get('when')))
        for t in regs:
            lines.append('     [登] %s | date=%s start=%s' % (t.get('type', '')[:60], t.get('date'), t.get('startDate')))
    else:
        lines.append('OK id%d %s | %d枠一致' % (e['id'], (e.get('name') or '')[:30], len(regs)))

lines.append('')
lines.append('=== B) 静的QC ===')
for e in new:
    bad = []
    if FW.search(e.get('artist') or '') or FW.search(e.get('name') or ''):
        bad.append('全角ローマ字/数字が残っている')
    if re.search(r'[（(]\s*[)）]', (e.get('venue') or '') + (e.get('dateLabel') or '')):
        bad.append('空カッコ')
    if (e.get('date') or '') < TODAY:
        bad.append('公演日が過去 date=%s' % e.get('date'))
    for t in e.get('tickets') or []:
        if (t.get('date') or '') > (e.get('date') or '9999'):
            bad.append('締切>公演日 (%s > %s)' % (t.get('date'), e.get('date')))
    dupe = exist_names.get(norm_name(e.get('artist')))
    if dupe:
        bad.append('既存に同名 id=%s' % dupe)
    if not e.get('_genre'):
        bad.append('ジャンル下書きが空')
    if not e.get('_piaSub'):
        bad.append('ぴあカテゴリ無し(_piaSub空)＝人が決める枠')
    if bad:
        ngB.append(e['id'])
        lines.append('⚠️ id%d %s ： %s' % (e['id'], (e.get('name') or '')[:34], ' / '.join(bad)))

lines.append('')
lines.append('=== C) ジャンル下書きの内訳（振り分けの下準備） ===')
by = {}
for e in new:
    by.setdefault(e.get('_genre') or '(空)', []).append(e['id'])
for g in sorted(by, key=lambda k: -len(by[k])):
    lines.append('%-12s %2d件  %s' % (g, len(by[g]), ','.join(str(i) for i in by[g])))

lines.append('')
lines.append('=== 集計: A不一致 %d件 %s / B要目視 %d件 %s / 対象 %d件 ==='
             % (len(ngA), ngA, len(ngB), ngB, len(new)))

json.dump(cache, io.open(CACHE_F, 'w', encoding='utf-8'), ensure_ascii=False)
io.open(os.path.join(ROOT, 'tmp', 'check57_0804.txt'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('wrote tmp/check57_0804.txt  target=%d  mismatchA=%d  flagB=%d' % (len(new), len(ngA), len(ngB)))
