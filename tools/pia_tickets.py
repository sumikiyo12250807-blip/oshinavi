# -*- coding: utf-8 -*-
"""ぴあ個別/バンドルページの券種を【決定論的に全件】抽出する。
WebFetch要約だと受付中の先行・寄席セッション等が黙って落ちる問題への対策
（memory: feedback_capture_all_deadlines_on_add / feedback_multiwindow_webfetch_verify）。

使い方:
  python tools/pia_tickets.py <eventCd|eventBundleCd|フルURL> [--all]
  既定は「買える券種(受付中/発売前)」だけ表示。--all で受付終了も含む全件。

出力: 各券種カードを 公演日・会場・県・券種名・状態・受付/発売日 で1行ずつ。
ぴあHTMLの ticketSalesCard-2024 構造をパースするので、要約と違い1枠も落とさない。
"""
import urllib.request, re, io, sys, html as _html, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

arg = sys.argv[1] if len(sys.argv) > 1 else ''
SHOW_ALL = '--all' in sys.argv
JSON_OUT = '--json' in sys.argv
if arg.startswith('http'):
    url = arg
elif arg.startswith('b') or 'Bundle' in arg:
    cd = arg.replace('eventBundleCd=', '')
    url = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=' + cd
else:
    cd = arg.replace('eventCd=', '')
    url = 'https://t.pia.jp/pia/event/event.do?eventCd=' + cd

def fetch(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')

def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()

h = fetch(url)
items = re.split(r'(?=<li class="ticketSalesList-2024__item)', h)
rows = []
for it in items:
    if 'ticketSalesCard-2024__status' not in it:
        continue
    m_url = re.search(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"', it)
    m_title = re.search(r'__title">(.*?)</p>', it, re.S)
    m_place = re.search(r'__place"[^>]*>(.*?)</span>', it, re.S)
    m_region = re.search(r'__region">(.*?)</span>', it, re.S)
    _dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
    perf_start = _dts[0] if _dts else ''
    perf_end = _dts[-1] if _dts else ''
    m_stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
    m_sdate = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
    stat_text = txt(m_stat.group(2)) if m_stat else ''
    cls = m_stat.group(1) if m_stat else ''
    sdate = txt(m_sdate.group(1)) if m_sdate else ''
    # HTMLクラス＋文言で判定。build_pia_entries.py と同一ロジックに統一(2026-06-24)。
    # 「本日発売初日」(is-before)を受付終了と取り違えると買える枠を黙って落とす(琉球フェス沖縄の反省)。
    # 売切・終了・結果発表は文言で先に除外(クラスがactive/beforeでも保険)。
    if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|終了しました|結果発表)', stat_text):
        state = '受付終了'
    elif cls == 'is-active' or re.search(r'(販売期間中|受付中|発売中|販売中|発売初日|本日発売)', stat_text):
        state = '受付中'
    elif cls == 'is-before' or '発売前' in stat_text or 'まもなく' in stat_text:
        state = '発売前'
    else:
        state = '受付終了'  # 販売終了/予定枚数終了/抽選受付終了/結果発表前 等
    rows.append({
        'perfdate': perf_start,
        'perf_end': perf_end,
        'venue': txt(m_place.group(1)) if m_place else '',
        'pref': txt(m_region.group(1)) if m_region else '',
        'title': txt(m_title.group(1)) if m_title else '',
        'state': state,
        'when': sdate,           # 受付中→「～ 終了日時」/ 発売前→「発売日時 より発売」
        'url': m_url.group(1) if m_url else '',
    })

# 重複除去（ぴあHTMLはレスポンシブで同じカードを2回出力する）
seen = set(); uniq = []
for r in rows:
    k = (r['perfdate'], r['perf_end'], r['venue'], r['title'], r['state'], r['when'])
    if k in seen:
        continue
    seen.add(k); uniq.append(r)
rows = uniq

buyable = [r for r in rows if r['state'] in ('受付中', '発売前')]
show = rows if SHOW_ALL else buyable
if JSON_OUT:
    print(json.dumps(show, ensure_ascii=False, indent=1))
else:
    print(f'URL: {url}')
    print(f'全{len(rows)}券種 / 買える(受付中・発売前){len(buyable)}件' + ('' if SHOW_ALL else '（--allで終了枠も表示）'))
    for r in show:
        pr = r['perfdate'] + ('〜'+r['perf_end'] if r.get('perf_end') and r['perf_end'] != r['perfdate'] else '')
        print(f"  [{r['state']}] {pr} {r['pref']} {r['venue']} | {r['title']} | {r['when']}")
