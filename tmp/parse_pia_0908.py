# -*- coding: utf-8 -*-
"""保存したぴあHTMLから券種カードをゼロから数え直し、登録データと突き合わせる材料を作る。
生の状態テキスト・受付終了日時・公演日・会場・県をそのまま出す（要約しない）。"""
import json, re, io, sys, os, html as _html

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def txt(s):
    return _html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or ''))).strip()


sel = json.load(open('tmp/audit_new_0908.json', encoding='utf-8'))
out = open('tmp/pia_parsed_0908.txt', 'w', encoding='utf-8')

for e in sel:
    eid = e['id']
    path = 'tmp/pia0908/%s.html' % eid
    out.write('=' * 78 + '\n')
    out.write('id=%s  %s\n' % (eid, e.get('name', '')))
    out.write('登録: 会場=%s / 県=%s / 公演日=%s / 枠数=%d\n'
              % (e.get('venue', ''), e.get('prefecture', ''), e.get('date', ''), len(e.get('tickets', []))))
    for t in e.get('tickets', []):
        out.write('   登録枠: %s | 終了=%s | url=%s\n' % (t.get('type', ''), t.get('date', ''), t.get('url', '')))
    if not os.path.exists(path):
        out.write('★実ページ取得できず\n')
        continue
    h = open(path, encoding='utf-8').read()
    mt = re.search(r'<title>(.*?)</title>', h, re.S)
    out.write('実ページtitle: %s\n' % txt(mt.group(1) if mt else ''))

    items = re.split(r'(?=<li class="ticketSalesList-2024__item)', h)
    rows = []
    for it in items:
        if 'ticketSalesCard-2024__status' not in it:
            continue
        m_url = re.search(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"', it)
        m_title = re.search(r'__title">(.*?)</p>', it, re.S)
        m_place = re.search(r'__place"[^>]*>(.*?)</span>', it, re.S)
        m_region = re.search(r'__region"[^>]*>(.*?)</span>', it, re.S)
        dts = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', it)
        m_stat = re.search(r'__status (is-[\w-]+)">(.*?)(?:<br|</p>)', it, re.S)
        m_sdate = re.search(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>', it, re.S)
        rows.append({
            'perf': (dts[0] if dts else '') + (('〜' + dts[-1]) if dts and dts[-1] != dts[0] else ''),
            'venue': txt(m_place.group(1)) if m_place else '',
            'pref': txt(m_region.group(1)) if m_region else '',
            'title': txt(m_title.group(1)) if m_title else '',
            'cls': m_stat.group(1) if m_stat else '',
            'stat': txt(m_stat.group(2)) if m_stat else '',
            'when': txt(m_sdate.group(1)) if m_sdate else '',
            'url': m_url.group(1) if m_url else '',
        })
    seen = set(); uniq = []
    for r in rows:
        k = (r['perf'], r['venue'], r['title'], r['stat'], r['when'], r['url'])
        if k in seen:
            continue
        seen.add(k); uniq.append(r)

    def state(r):
        if re.search(r'(予定枚数|完売|売り?切|受付は?終了|販売終了|販売期間終了|終了しました|結果発表)', r['stat']):
            return '受付終了'
        if r['cls'] == 'is-active' or re.search(r'(販売期間中|受付中|発売中|販売中|発売初日|本日発売)', r['stat']):
            return '受付中'
        if r['cls'] == 'is-before' or '発売前' in r['stat'] or 'まもなく' in r['stat']:
            return '発売前'
        return '受付終了'

    buy = [r for r in uniq if state(r) in ('受付中', '発売前')]
    out.write('実ページ: 全%d券種 / 買える枠 %d件\n' % (len(uniq), len(buy)))
    for r in uniq:
        out.write('  [%s|%s] 公演=%s %s %s | %s | when=%s\n'
                  % (state(r), r['stat'], r['perf'], r['pref'], r['venue'], r['title'], r['when']))
        out.write('      url=%s\n' % r['url'])
    # ページ内に出る公演日をすべて拾う
    alldts = sorted(set(re.findall(r'datetime="(\d{4}-\d{2}-\d{2})', h)))
    out.write('実ページ内の公演日(datetime全体): %s\n' % ', '.join(alldts))
out.close()
print('書き出し完了')
