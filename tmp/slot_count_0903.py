# -*- coding: utf-8 -*-
"""疑わしいエントリについて、ぴあ実ページの「売り場コード(rlsCd/lotRlsCd)のユニーク数」を数える。
出典 feedback_pia_parser_flattens_slots＝本当の枠数はリンク先のユニーク数で決まる。
登録の枠数と突き合わせて、畳まれているものを機械で特定する。
"""
import re, sys, html, json, time, http.client
sys.stdout.reconfigure(encoding='utf-8')

IDS = [int(x) for x in sys.argv[1].split(',')]


def strip(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s or ''))).strip()


src = open('index.html', encoding='utf-8').read()
events = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
byid = {e['id']: e for e in events}


def event_url(e):
    L = e.get('links')
    cands = []
    if isinstance(L, dict):
        cands = [v for v in L.values() if isinstance(v, str) and 'pia.jp' in v]
    elif isinstance(L, list):
        for x in L:
            if isinstance(x, dict):
                cands += [v for v in x.values() if isinstance(v, str) and 'pia.jp' in v]
    for t in e.get('tickets', []):
        u = t.get('url')
        if isinstance(u, str) and 'pia.jp' in u:
            cands.append(u)
    for u in cands:
        if 'event.do' in u:
            return u
    return cands[0] if cands else None


def fetch(url):
    path = url.split('t.pia.jp', 1)[1]
    conn = http.client.HTTPSConnection('t.pia.jp', timeout=40)
    conn.request('GET', path, headers={'User-Agent': 'Mozilla/5.0', 'Accept-Encoding': 'identity'})
    r = conn.getresponse()
    body = r.read().decode('utf-8', 'replace')
    conn.close()
    return r.status, body


for i in IDS:
    e = byid.get(i)
    if not e:
        print('id=%d 存在しない' % i)
        continue
    url = event_url(e)
    if not url or 't.pia.jp' not in url:
        print('id=%d ぴあURL無し（%s）' % (i, url))
        continue
    try:
        st, raw = fetch(url)
    except Exception as ex:
        print('id=%d 取得失敗 %s' % (i, ex))
        continue
    busy = ('大変混み合' in raw) or ('sorry' in raw[:2000].lower())
    gone = '見つかりませんでした' in raw
    codes = re.findall(r'ticketInformation\.do\?[^"\']*?(?:lotRlsCd|rlsCd)=(\d+)', raw)
    uniq = list(dict.fromkeys(codes))
    # 各コードの近傍テキスト（券種名らしきもの）
    labels = {}
    for m in re.finditer(r'ticketInformation\.do\?[^"\']*?(?:lotRlsCd|rlsCd)=(\d+)', raw):
        c = m.group(1)
        if c in labels:
            continue
        seg = raw[max(0, m.start() - 1200):m.start() + 400]
        labels[c] = strip(seg)[-150:]
    print('== id=%d %s' % (i, (e.get('name') or '')[:40]))
    print('   URL: %s' % url)
    print('   登録枠数: %d / ぴあ売り場コード ユニーク: %d %s%s'
          % (len(e.get('tickets', [])), len(uniq),
             '  🚨混雑ページ' if busy else '', '  🚨ページ消失' if gone else ''))
    for c in uniq:
        print('     code=%s | %s' % (c, labels.get(c, '')[:120]))
    time.sleep(3)
