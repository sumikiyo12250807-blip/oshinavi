# -*- coding: utf-8 -*-
# gate_fields S1・S3 のうち実害がある型＝受付の飛び先がその売り場で1つだけなのに、カードの売り場ボタン（links.pia / links.eplus）が別の公演のページ
#   → ボタンの行き先を受付と同じページに直す。受付の飛び先が2つ以上のカードは画面に売り場ボタンを出さない（index.html multiTicketUrl）ので触らない
#   python tools/fix_links.py [--apply]   … 2026-11-05 新設・gate_fields S1/S3 を直す
import io, os, re, sys, json, time, atexit, datetime
R = 'C:/Users/user/oshinavi/'
today = datetime.date.today().isoformat()
apply = '--apply' in sys.argv
# 鍵は取らない＝呼ぶ側（prepush など）が index.lock を持って呼ぶ（入れ子にしない＝feedback_index_lock_no_nesting）
path = R + 'index.html'
text = io.open(path, encoding='utf-8', newline='').read()
mm = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
E, end = json.JSONDecoder().raw_decode(text, mm.start(1))
KEY = {'pia': (r'pia\.jp/.*eventCd=(\w+)', r'eventCd=(\w+)'), 'eplus': (r'eplus\.jp/sf/detail/(\d+)', r'eplus\.jp/sf/detail/(\d+)')}
log = []
for e in E:
    if (e.get('date') or '') < today:
        continue
    links = e.get('links') or {}
    allurls = {t.get('url') for t in e.get('tickets') or [] if t.get('url')}
    for k, (tre, lre) in KEY.items():
        lv = links.get(k)
        if not lv:
            continue
        live = [t for t in e.get('tickets') or [] if re.search(tre, t.get('url') or '')
                and (t.get('soldout') or t.get('saleUntilSoldOut') or (t.get('date') or '') >= today)]
        codes = {re.search(tre, t['url']).group(1) for t in live}
        lc = re.search(lre, lv)
        if not lc or not codes or lc.group(1) in codes:
            continue
        if len(allurls) == 1 and len(codes) == 1:
            nu = live[0]['url']
            log.append(f"id{e['id']} {(e.get('name') or '')[:40]} ｜ links.{k} {lv} → {nu}")
            if apply:
                links[k] = nu
io.open(R + 'tmp/fix_links.txt', 'w', encoding='utf-8').write(f'{len(log)}件\n' + '\n'.join(log))
if apply and log:
    body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
    if '\r\n' in text[mm.start(1):mm.start(1) + 3000]:
        body = body.replace('\n', '\r\n')
    io.open(path, 'wb').write((text[:mm.start(1)] + body + text[end:]).encode('utf-8'))
print(len(log))
