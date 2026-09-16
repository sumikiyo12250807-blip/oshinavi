# -*- coding: utf-8 -*-
"""ぴあで「予定枚数終了」なのに、OSHINAVI にその公演日の枠が1つも無い＝売り切れの表示がどこにも出ていない枠を、
売り切れの印付きで足す（2026-09-16朝（今日版＝入力は tmp/soldbadge_list_0916.py）・push 前の独立の読み直しの「参考」＝16件43カード）。
売り切れは消さずに出す（feedback_soldout_keep_visible）＝「最初から載っていなかった」に見えないように。
入力＝別エージェントの洗い出し（scratchpad の v6_soldbadge.txt・1行1カード）
ぴあの券種は tools/pia_tickets.py <URL> --all --json で1本ずつ読む（1.5秒あけて・読んだものは tmp/x0916/sb_cache に残し、2回目は読まない）。
足す条件＝その行の公演日・県・紙/電子の別が同じ枠が、そのエントリにまだ無い時だけ（もうある＝足さない）。
足す形＝{"type": "一般発売（県 M/D公演）", "date": 公演日, "url": その公演のページ, "soldout": true, "soldoutSince": 今日}
使い方: python tmp/x0916/soldbadge_add.py [--apply]
"""
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
TODAY = datetime.date.today().isoformat()
V6 = 'tmp/soldbadge_in_0916.txt'
CACHE = 'tmp/sb_cache_0916'
os.makedirs(CACHE, exist_ok=True)


def nf(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or ''))


def fetch(url):
    p = os.path.join(CACHE, hashlib.md5(url.encode()).hexdigest()[:12] + '.json')
    if os.path.exists(p):
        return json.load(io.open(p, encoding='utf-8'))
    out = subprocess.run([sys.executable, 'tools/pia_tickets.py', url, '--all', '--json'], capture_output=True)
    time.sleep(1.5)
    txt = out.stdout.decode('utf-8', 'replace').strip()
    try:
        rows = json.loads(txt)
    except Exception:
        print('  ❌ 読めなかった（混雑ページかも）: %s' % url)
        return None
    io.open(p, 'w', encoding='utf-8').write(json.dumps(rows, ensure_ascii=False, indent=1))
    return rows


def pref_short(p):
    p = p or ''
    if p == '北海道':
        return p
    return re.sub(r'[都府県]$', '', p)


def md(d):
    y, m, dd = d.split('-')
    return ('R9年 ' if y == '2027' else '') + '%d/%d' % (int(m), int(dd))


items = []
for ln in io.open(V6, encoding='utf-8').read().splitlines():
    m = re.match(r'^id(\d+) 印なし: ぴあ「予定枚数終了」公演([\d\-,]+)「(.*)」 (https?://\S+)$', ln.strip())
    if m:
        items.append((int(m.group(1)), m.group(2).split(',')[0], m.group(3), m.group(4)))
print('洗い出しの行 %d' % len(items))

src = open('index.html', encoding='utf-8', newline='').read()
mm = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(mm.group(2))
byid = {e['id']: e for e in events}

added, skipped, unread = 0, 0, 0
for eid, pdate, title, url in items:
    rows = fetch(url)
    if rows is None:
        unread += 1
        continue
    hit = [r for r in rows if r.get('statustext') == '予定枚数終了' and r.get('perfdate') == pdate and nf(r.get('title')) == nf(title)]
    if len(hit) != 1:
        print('  ⚠️ id%s %s「%s」＝ぴあの行が %d 本（足さない）' % (eid, pdate, title[:30], len(hit)))
        skipped += 1
        continue
    r = hit[0]
    pref = pref_short(r.get('pref'))
    span = md(pdate) + ('〜' + md(r['perf_end']).replace('R9年 ', '') if r.get('perf_end') and r['perf_end'] != pdate else '')
    t = nf(title)
    kind = '【紙チケット】' if '紙' in t else ('【電子チケット】' if '電子' in t else '')
    core = '（%s %s公演）' % (pref, span)
    e = byid[eid]
    same = [x for x in e['tickets'] if core in x['type'] and (not kind or kind.strip('【】')[:2] in x['type'])]
    if same:
        print('  ・id%s %s はもう枠がある（%s）＝足さない' % (eid, core, same[0]['type'][:40]))
        skipped += 1
        continue
    ecd = re.search(r'eventCd=(\d+)', r.get('url') or '')
    turl = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % ecd.group(1) if ecd else url
    e['tickets'].append({'type': '一般発売%s%s' % (kind, core), 'date': pdate, 'url': turl, 'soldout': True, 'soldoutSince': TODAY})
    added += 1
    print('  ＋ id%s %s 一般発売%s%s（予定枚数終了）' % (eid, (e.get('name') or '')[:16], kind, core))
print('足す %d ／ 足さない %d ／ 読めなかった %d' % (added, skipped, unread))
if not APPLY or added == 0:
    print('（--apply で書き込み）' if not APPLY else '（足すものが無い）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:mm.start()] + mm.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + mm.group(3) + src[mm.end():]
open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
