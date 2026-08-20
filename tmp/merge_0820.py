# -*- coding: utf-8 -*-
"""同じ興行だった5件を既存エントリへ統合する（新規登録せず、既存に枠を足す/差し替える）。
枠を足すときは **per-ticket url** を必ず付ける（飛び先が違う枠を後から潰さないため
＝[[feedback_dedup_badges_keeps_urls]] / [[feedback_tour_per_ticket_url]]）。
既存の他社（e+等）枠は絶対に消さない＝追加のみ。
おまけ：3040 山崎ハコは links.pia が空だったので、今回拾ったぴあURLを補完する。
"""
import io, json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

built = {e['id']: e for e in json.load(io.open('tmp/built_0820.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
BY = {e['id']: e for e in EVENTS}


def tkey(t):
    return (t.get('type'), t.get('date'), t.get('startDate'))


def add_tickets(dst_id, src_id, add_venue=True):
    """src の枠を dst へ足す（既にある枠は足さない）。会場・県・千秋楽も広げる。"""
    d, s = BY[dst_id], built[src_id]
    url = (s.get('links') or {}).get('pia') or ''
    have = {tkey(t) for t in d.get('tickets') or []}
    added = 0
    for t in s.get('tickets') or []:
        if tkey(t) in have:
            continue
        t = dict(t)
        if not t.get('url') and url:
            t['url'] = url
        d.setdefault('tickets', []).append(t)
        added += 1
    if add_venue:
        for v in (s.get('venue') or '').replace('全国ツアー（', '').rstrip('）').split('／'):
            if v and v not in (d.get('venue') or ''):
                base = d.get('venue') or ''
                if base.startswith('全国ツアー（'):
                    d['venue'] = base.rstrip('）') + '／' + v + '）'
                else:
                    d['venue'] = '全国ツアー（' + base + '／' + v + '）'
        for p in (s.get('prefecture') or '').split('・'):
            cur = d.get('prefecture') or ''
            if p and p not in cur and cur != '全国':
                d['prefecture'] = cur + '・' + p
    if (s.get('date') or '') > (d.get('date') or ''):
        d['date'] = s['date']
    print('  id%-5d %-28s 枠 %d → %d / 千秋楽 %s / 県 %s' % (
        dst_id, (d.get('artist') or '')[:26], len(have), len(d['tickets']), d.get('date'), d.get('prefecture')))
    return added


print('=== 統合 ===')
# 850 横山だいすけ＝既存は愛知9/3の1枠だけ。ツアー全体のbundleで丸ごと置き換える
d, s = BY[850], built[4740]
print('  id850  横山だいすけ 枠 %d → %d（ツアー全体に置き換え）' % (
    len(d.get('tickets') or []), len(s['tickets'])))
for k in ('tickets', 'date', 'dateLabel', 'venue', 'prefecture'):
    d[k] = s[k]
d.setdefault('links', {})['pia'] = (s.get('links') or {}).get('pia') or d.get('links', {}).get('pia')

add_tickets(3526, 4749, add_venue=False)   # dustbox＝同じ会場・同じ日程、売り場だけ別
add_tickets(738, 4751)                     # フラワーカンパニーズ＝栃木12/5を追加
add_tickets(950, 4755, add_venue=False)    # 天満天神繁昌亭＝同じ小屋の11/18公演
add_tickets(1028, 4758)                    # 桂宮治＝東京 R9年1/30公演

# おまけ：3040 山崎ハコの links.pia が空だった
ya = BY[3040]
if not (ya.get('links') or {}).get('pia'):
    ya.setdefault('links', {})['pia'] = (built[4752].get('links') or {}).get('pia')
    print('  id3040 山崎ハコ links.pia を補完 → %s' % ya['links']['pia'])

shutil.copyfile('index.html', 'index.html.bak_0820_merge')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 書き込み完了 ===')
