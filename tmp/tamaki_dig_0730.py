# -*- coding: utf-8 -*-
"""玉置浩二の生きた枠を探す
 ①e+親ページから /sf/word/ を抽出 → wordページで全公演を列挙
 ②登録済み-Pページの兄弟券種(P021002…)を総当たりで探す
 ③各ページの窓状態を parse_blocks で判定
"""
import io, re, sys, time
sys.path.insert(0, 'tools')
from eplus_harvest import fetch
from reconcile_eplus import parse_blocks
import datetime

TODAY = datetime.date.today()
BASE = 'https://eplus.jp/sf/detail/0011860001'
out = ['today=%s' % TODAY]

def show(url, tag=''):
    try:
        h = fetch(url)
    except Exception as ex:
        out.append('  ❌ %s %s' % (url, str(ex)[:70]))
        return None
    blocks = parse_blocks(h)
    alive = [b for b in blocks if b['status'] in ('open', 'before') and b['ed'] >= TODAY]
    out.append('  %s %s  窓%d件 / 買える%d件' % (tag, url, len(blocks), len(alive)))
    for b in blocks:
        out.append('      %s %s〜%s %s status=%s' % (b['sd'], b['st'], b['ed'], b['et'], b['status']))
    return h

# ① 親ページ
h = show(BASE, '[親]')
if h:
    words = sorted(set(re.findall(r'/sf/word/(\d+)', h)))
    out.append('■ wordリンク: %s' % words)
    for w in words[:6]:
        wu = 'https://eplus.jp/sf/word/%s' % w
        try:
            wh = fetch(wu)
        except Exception as ex:
            out.append('  ❌ word %s %s' % (wu, str(ex)[:60]))
            continue
        ids = sorted(set(re.findall(r'/sf/detail/([0-9A-Za-z\-]+)', wh)))
        # ページ内のテキストから公演名らしき見出しを拾う
        txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', wh))
        hit = '玉置浩二' in txt
        out.append('  word %s → detail %d件 玉置浩二表記=%s' % (wu, len(ids), hit))
        out.append('     %s' % ', '.join(ids[:30]))
        time.sleep(0.6)

# ② 兄弟券種の総当たり（登録は P0030579P021001 系）
out.append('■ 兄弟券種の探索')
for perf in ('P0030579', 'P0030580', 'P0030581', 'P0030582', 'P0030583'):
    for n in range(1, 4):
        u = '%s-%sP02100%d' % (BASE, perf, n)
        show(u, '[券種]')
        time.sleep(0.5)

io.open('tmp/out_tamaki_dig.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('wrote tmp/out_tamaki_dig.txt')
