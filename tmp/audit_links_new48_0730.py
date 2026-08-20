# -*- coding: utf-8 -*-
"""新着48件のリンク品質チェック（ネットワーク不要）。
 ①個別公演URLになっているか（[[feedback_require_specific_url]]／[[feedback_url_first_on_new_add]]）
 ②複数eventCd由来なら各ticketにurlが付いているか（[[feedback_tour_per_ticket_url]]）
 ③購入ボタンの優先（楽天>ぴあ＝[[feedback_vendor_priority]]）と重複ベンダー
 ④AmazonリンクのクエリにイベントUUだけ入っていないか（公演名が丸ごと入るとCD 0件＝今日の宿題）
"""
import json
import re
import urllib.parse

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = sorted([e for e in EVENTS if e.get('genre') == 'new'], key=lambda x: x['id'])

# 公演名っぽい語＝これがAmazonクエリに入っているとCDが当たらない
NOISE = re.compile(r'コンサート|リサイタル|公演|ツアー|フェス|第\d|回|定期|記念|LIVE|ライブ|'
                   r'ホール|劇場|独演会|ネタ|会$|音楽会|祭|場所|展')

lines = []
n_url = n_amz = n_multi = 0
for e in news:
    L = e.get('links') or {}
    ids = []
    for c in re.findall(r'event(?:Bundle)?Cd=(\w+)', json.dumps(e, ensure_ascii=False)):
        if c not in ids:
            ids.append(c)
    # ① 個別URL
    pia = L.get('pia') or ''
    rak = L.get('rakuten') or ''
    if not (pia or rak):
        lines.append(f"🚨 id={e['id']} 購入URLが無い | {(e.get('artist') or '')[:40]}")
        n_url += 1
    elif pia and not re.search(r'event(?:Bundle)?Cd=\w+', pia):
        lines.append(f"🚨 id={e['id']} ぴあURLが個別ページでない: {pia[:70]}")
        n_url += 1
    # ② 複数eventCd由来は各ticketにurl必須
    if len(ids) > 1:
        miss = [t for t in (e.get('tickets') or []) if not (t.get('url') or '')]
        if miss:
            lines.append(f"🚨 id={e['id']} {len(ids)}ページ由来なのにurl無しの枠が{len(miss)}件 | {(e.get('artist') or '')[:36]}")
            n_multi += 1
    # ③ ベンダー重複（楽天とぴあ両方＝ボタンの優先ルール確認用）
    if pia and rak:
        lines.append(f"ℹ️ id={e['id']} ぴあ＋楽天の両方あり（ボタンは楽天優先が正） | {(e.get('artist') or '')[:36]}")
    # ④ Amazonクエリの中身
    az = L.get('amazon') or ''
    if az:
        q = urllib.parse.parse_qs(urllib.parse.urlparse(az).query).get('k', [''])[0]
        hits = NOISE.findall(q)
        if hits:
            lines.append(f"⚠️ id={e['id']} Amazonクエリに公演名の語が入っている {hits[:4]}: 「{q}」")
            n_amz += 1

lines.append('')
lines.append(f'=== URL不備 {n_url} / per-ticket url欠落 {n_multi} / Amazonクエリ要注意 {n_amz}（新着{len(news)}件） ===')
open('tmp/audit_links_new48_0730.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('wrote tmp/audit_links_new48_0730.txt')
