# -*- coding: utf-8 -*-
"""「音楽/演歌・邦楽」で enka に落ちた新着について、ぴあの実ページ本文に
雅楽・邦楽など和楽器の語が出るかを機械で確認する。読み取り専用。"""
import json, sys, io, os, re, time, urllib.request, html as _html
sys.stdout = io.TextIOWrapper(open(sys.__stdout__.fileno(), 'wb', closefd=False), encoding='utf-8')

IDX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
src = open(IDX, encoding='utf-8').read()
i = src.index('const EVENTS = [')
start = src.index('[', i)
depth, j, instr, esc = 0, start, False, False
while j < len(src):
    c = src[j]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
    else:
        if c == '"': instr = True
        elif c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0: break
    j += 1
events = json.loads(src[start:j+1])
new = [e for e in events if e.get('genre') == 'new']

KW = ['雅楽', '邦楽', '和楽器', '篳篥', '笙', '龍笛', '和太鼓', '三味線', '箏', '尺八', '民謡', '演歌', '歌謡']
tg = [e for e in new if '演歌・邦楽' in (e.get('_piaSub') or '')]
print('対象 %d件' % len(tg))
for e in tg:
    u = (e.get('links') or {}).get('pia') or ''
    print('--- id%s %s ｜_genre=%s ｜%s' % (e.get('id'), e.get('artist'), e.get('_genre'), u))
    if not u:
        continue
    try:
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
        h = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')
    except Exception as ex:
        print('    FETCH失敗', ex); continue
    txt = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    txt = re.sub(r'\s+', ' ', _html.unescape(txt))
    # ヘッダ/フッタの共通メニュー分を除くため、公演名以降に限定
    hit = [k for k in KW if k in txt]
    print('    本文に出た語:', ' '.join(hit) if hit else '(なし)')
    for k in ['雅楽', '篳篥', '和太鼓', '三味線']:
        if k in txt:
            p = txt.index(k)
            print('      [%s] …%s…' % (k, txt[max(0, p-70):p+70]))
    time.sleep(2)
