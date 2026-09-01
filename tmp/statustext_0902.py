# -*- coding: utf-8 -*-
"""指定エントリのぴあ実ページから、券種ごとの「生の状態文言（statustext）」を出す。

🚨 `pia_tickets.py` の state は「予定枚数終了」と「受付終了」を同じ"受付終了"に潰す。
   売り切れ（＝消さずに『予定枚数終了』で出し続ける）か、本当に販売が終わったのかは
   生HTMLの `__status (is-xxx)">文言` を読まないと分からない
   （feedback_heal_flattens_ticket_types / feedback_saleended_vs_soldout）。

  python tmp/statustext_0902.py 3841,3849,...
"""
import re, json, sys, time, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

IDS = [int(x) for x in sys.argv[1].split(',')]
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}


def fetch(u):
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


def cards(html):
    """券種カード単位に切って (券種名, statusクラス, 状態文言) を返す。"""
    out = []
    for it in re.split(r'(?=<li class="ticketSalesCard-2024)', html):
        t = re.search(r'__title">(.*?)</p>', it, re.S)
        s = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        if not t or not s:
            continue
        name = re.sub(r'<[^>]+>', '', t.group(1)).strip()
        txt = re.sub(r'<[^>]+>', '', s.group(2)).strip()
        out.append((name, s.group(1), txt))
    return out


h = open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
by = {e['id']: e for e in EV}
seen = {}
for i in IDS:
    e = by.get(i)
    if not e:
        print(f'id{i} 見つからない')
        continue
    urls = []
    u = (e.get('links') or {}).get('pia')
    if u:
        urls.append(u)
    for t in (e.get('tickets') or []):
        tu = t.get('url') or ''
        if tu and 'pia.jp' in tu and tu not in urls:
            urls.append(tu)
    print(f'\n=== id{i} {e.get("artist","")[:44]} / 公演{e.get("date")} / 登録{len(e.get("tickets") or [])}枠')
    if not urls:
        print('   !! ぴあURLが無い（links.pia も ticket.url も空）')
        continue
    for u in urls:
        if u not in seen:
            try:
                seen[u] = cards(fetch(u))
            except Exception as ex:
                seen[u] = [('!! 取得失敗', '', str(ex)[:60])]
            time.sleep(2)
        print(f'   {u}  券種{len(seen[u])}件')
        for nm, cls, txt in seen[u]:
            print(f'      [{txt}] cls={cls} | {nm[:64]}')
