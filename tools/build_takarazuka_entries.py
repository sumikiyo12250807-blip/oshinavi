# -*- coding: utf-8 -*-
"""宝塚歌劇のハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形・1公演×1劇場＝1カード）。

  python tools/build_takarazuka_entries.py tmp/x1120/newv/takarazuka/harvest.json --out tmp/x1120/newv/takarazuka/built.json
  python tools/build_takarazuka_entries.py <harvest> --out <built> --index-venue   … 県が出ない劇場に index.html の県を使う
  python tools/build_takarazuka_entries.py --selftest

## 枠（tickets）＝チケットページの「チケットお求め方法」から
- 先行販売（`<h3>先行販売</h3>` の下の `<h4>宝塚友の会</h4>`・`<h4>宝塚歌劇共通ID＋（プラス）</h4>` 等）：
  「■「第1抽選方式」」＋「申込期間：10月3日（土）10:00〜10月4日（日）23:00」＝**方式ごとに1枠**。
  名前＝「宝塚友の会先行・第1抽選方式」（会員の先行だと分かる形・[[project_fc_presale_public]]）。
  受付前＝「…M/D HH:MM発売」（date＝締切・startDate＝始まり）／受付中＝「…〜M/D HH:MM」（date＝締切）／締切が過ぎた枠は載せない。
  「詳細が決まり次第掲載」の欄は枠を作らない（日付が無い）。
- 一般前売（`<h3>一般前売 ※11月21日（土）前売開始</h3>`）：
  `<h4>宝塚歌劇Webチケットサービス（インターネット販売）</h4>` の「11月21日（土）朝10時から」＝**終わりが書いていない**
  → 「一般前売（県 会期公演）11/21 10:00発売〜」・startDate＝発売日・date＝千秋楽・saleEndUnknown:true
  （[[feedback_sale_end_unknown_display]]）。Web の欄が無い（梅田芸術劇場の公演＝劇場・プレイガイドで売る）時は
  h3 の日付だけ＝「一般前売（…）10/31発売〜」（時刻は書いていない＝付けない）。
- 載せない：電話受付・電話予約・リセール・お問い合わせ・他の売り場（チケットかながわ等）の欄。
- 年は書いていない＝**曜日が合い・千秋楽より前・366日以内**の年が1つに決まる時だけ。決まらなければ載せない。
## カード
- name＝「宝塚歌劇 ＋ ページの題（月組公演 『…』『…』）」・artist＝「宝塚歌劇＋組」（題に組が無ければ name）。
- 会期＝`公演期間：2026年12月12日（土） - 2027年1月24日（日）`（**事実の会期**＝初日〜千秋楽）。終わった公演は載せない。
- 劇場＝「会場を選択」の active（無ければ `<title>` の「チケット：劇場名」）。県＝その `[兵庫県]`、他のページの同じ劇場の `[県]`、
  調べて確かめた表（VENUE_PREF・出所をコメント）、`--index-venue` の時だけ index.html で他の売り場が同じ劇場に付けた県。決まらなければ空。
- ジャンル＝売り場に分類の札が無い＝`_genre` は空（勝手に決めない）・genre は "new"。
"""
import argparse
import datetime
import importlib.util
import io
import json
import os
import re
import sys

_KEEP = []
HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


BT = _load('build_tiget_entries')     # md / jp（同じ物差し）
BD = _load('build_ticketdive_entries')  # load_index_venues / INDEX_VENUE / vkey（--index-venue の時だけ）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JST = datetime.timezone(datetime.timedelta(hours=9))
WD = '月火水木金土日'
# 調べて確かめた劇場の県（出所を残す）
VENUE_PREF = {
    '宝塚大劇場': '兵庫',        # kageki.hankyu.co.jp/theater/takarazuka/index.html「兵庫県宝塚市栄町1-1-57」（2026-11-20）
    '宝塚バウホール': '兵庫',    # 同じページ「宝塚大劇場・宝塚バウホール」「隣接する宝塚バウホール」（2026-11-20）
    '東京宝塚劇場': '東京',      # /ticket/index.html の見出し「東京宝塚劇場[東京都]」（2026-11-20）
}
SKIP_H4 = re.compile(r'電話|リセール|お問い合わせ|インフォメーション|団体')


def short_pref(p):
    p = (p or '').strip()
    if p == '北海道':
        return p
    return re.sub(r'[都府県]$', '', p) if re.fullmatch(r'[一-龥]{2,3}[都府県]', p) else ''


def parse_period(s):
    """「公演期間：2026年12月12日（土） - 2027年1月24日（日）」→ (初日, 千秋楽) iso か (None, None)。"""
    m = re.search(r'(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日', s or '')
    if not m:
        return None, None
    a = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    rest = s[m.end():]
    m2 = re.search(r'[-－〜～~]\s*(?:(\d{4})年)?\s*(\d{1,2})月\s*(\d{1,2})日', rest)
    if not m2:
        if re.search(r'[-－〜～~]', rest):
            return None, None
        return a.isoformat(), a.isoformat()
    b = datetime.date(int(m2.group(1)) if m2.group(1) else a.year, int(m2.group(2)), int(m2.group(3)))
    if not m2.group(1) and b < a:
        b = b.replace(year=b.year + 1)
    return a.isoformat(), b.isoformat()


def year_of(mo, da, wd, show_end):
    """月日（と曜日）→ 曜日が合い・千秋楽より前・366日以内の年が1つの時だけ date。"""
    end = datetime.date.fromisoformat(show_end)
    c = []
    for y in (end.year, end.year - 1):
        try:
            d = datetime.date(y, mo, da)
        except ValueError:
            continue
        if wd and WD[d.weekday()] != wd:
            continue
        if d <= end and (end - d).days <= 366:
            c.append(d)
    return c[0] if len(c) == 1 else None


DAY = r'(\d{1,2})月\s*(\d{1,2})日\s*(?:[（(]\s*([月火水木金土日])[^）)]*[）)])?'


def hm_of(s):
    m = re.match(r'\s*(?:朝|午前)?\s*(\d{1,2})(?:[:：](\d{2})|時)', s or '')
    if not m:
        return None
    return '%d:%s' % (int(m.group(1)), m.group(2) or '00')


def windows_of(ev, show_end):
    """受付の欄 → [{'name','start','start_hm','end','end_hm','kind'}] と、読めなかった説明のリスト。"""
    out, bad = [], []
    ctx = ''
    for sec in ev.get('sections') or []:
        h3 = (sec.get('h3') or '').strip()
        if h3:
            ctx = h3
        if ctx.startswith('先行'):
            for st in sec.get('sets') or []:
                org = (st.get('h4') or '').strip()
                if not org or SKIP_H4.search(org):
                    continue
                org_s = re.sub(r'（[^）]*）', '', org).strip()
                method = ''
                for ln in st.get('lines') or []:
                    mm = re.match(r'■\s*「([^」]+)」', ln)
                    if mm:
                        method = mm.group(1)
                        continue
                    mp = re.match(r'申込期間[：:]\s*' + DAY + r'\s*(.*?)\s*[〜～~]\s*' + DAY + r'\s*(.*)$', ln)
                    if mp:
                        s = year_of(int(mp.group(1)), int(mp.group(2)), mp.group(3), show_end)
                        e = year_of(int(mp.group(5)), int(mp.group(6)), mp.group(7), show_end)
                        if not s or not e:
                            bad.append('申込期間の年が1つに決まらない: %s %s' % (org_s, ln[:40]))
                            continue
                        out.append({'name': '%s先行%s' % (org_s, ('・' + method) if method else ''),
                                    'start': s.isoformat(), 'start_hm': hm_of(mp.group(4)),
                                    'end': e.isoformat(), 'end_hm': hm_of(mp.group(8)), 'kind': 'presale'})
                    elif ln.startswith('申込期間'):
                        bad.append('申込期間が読めない: %s %s' % (org_s, ln[:40]))
        elif ctx.startswith('一般前売'):
            web = False
            for st in sec.get('sets') or []:
                org = (st.get('h4') or '').strip()
                if 'Webチケットサービス' not in org:
                    continue
                web = True
                ln = (st.get('lines') or [''])[0]
                m = re.match(r'\s*' + DAY + r'\s*(.*)$', ln)
                if not m:
                    bad.append('一般前売の日付が読めない: %s' % ln[:40])
                    continue
                d = year_of(int(m.group(1)), int(m.group(2)), m.group(3), show_end)
                if not d:
                    bad.append('一般前売の年が1つに決まらない: %s' % ln[:40])
                    continue
                out.append({'name': '一般前売', 'start': d.isoformat(), 'start_hm': hm_of(m.group(4)),
                            'end': None, 'end_hm': None, 'kind': 'general'})
            if not web and h3.startswith('一般前売'):
                m = re.search(r'※\s*' + DAY + r'\s*前売開始', h3)
                d = year_of(int(m.group(1)), int(m.group(2)), m.group(3), show_end) if m else None
                if d:
                    out.append({'name': '一般前売', 'start': d.isoformat(), 'start_hm': None,
                                'end': None, 'end_hm': None, 'kind': 'general'})
                else:
                    bad.append('一般前売の日付が読めない: %s' % h3[:40])
        # お問い合わせ・その他の見出しは読まない
    return out, bad


def mdr(iso):
    y = int(iso[:4])
    s = BT.md(iso)
    return ('R%d年 %s' % (y - 2018, s)) if y >= 2027 else s


def span_text(s, e):
    if s == e:
        return mdr(s)
    return '%s〜%s' % (mdr(s), BT.md(e) if s[:4] == e[:4] else mdr(e))


def at(iso, hm):
    h, m = hm.split(':')
    return datetime.datetime.fromisoformat(iso) + datetime.timedelta(hours=int(h), minutes=int(m))


def venue_of(ev):
    if ev.get('venue'):
        return ev['venue']
    m = re.match(r'\s*チケット[：:]\s*(.+?)\s*$', (ev.get('title_raw') or '').split('|')[0])
    return m.group(1) if m else ''


def pref_of(ev, venue, seen):
    """県＝[兵庫県] → 他のページの同じ劇場の[県] → 調べた表 → --index-venue。→ (県, 出所)"""
    p = short_pref(ev.get('venue_pref'))
    if p:
        return p, 'page'
    if seen.get(venue):
        return seen[venue], 'other_page'
    if venue in VENUE_PREF:
        return VENUE_PREF[venue], 'venue_table'
    p = BD.INDEX_VENUE.get(BD.vkey(venue))
    if p:
        return p, 'index_venue'
    return '', 'unknown'


def build(ev, today, now, seen=None):
    """1チケットページ → (エントリ, None) か (None, 理由)。now は JST の naive datetime。"""
    seen = seen or {}
    show = (ev.get('show') or '').strip()
    if not show:
        return None, '題が読めない'
    s, e = parse_period(ev.get('period'))
    if not s:
        return None, '会期が読めない「%s」' % (ev.get('period') or '')[:30]
    if e < today:
        return None, '公演が終わっている'
    venue = venue_of(ev)
    pref, how = pref_of(ev, venue, seen)
    wins, bad = windows_of(ev, e)
    head = '（%s %s公演）' % (pref, span_text(s, e)) if pref else '（%s公演）' % span_text(s, e)
    tickets = []
    for w in wins:
        url = ev['page']
        if w['end']:
            if at(w['end'], w['end_hm'] or '23:59') < now:
                continue                                   # 締切が過ぎた
            if at(w['start'], w['start_hm'] or '0:00') > now:
                tm = (' ' + w['start_hm']) if w['start_hm'] else ''
                tickets.append({'type': '%s%s%s%s発売' % (w['name'], head, mdr(w['start']), tm),
                                'date': w['end'], 'startDate': w['start'], 'url': url})
            else:
                tm = (' ' + w['end_hm']) if w['end_hm'] else ''
                tickets.append({'type': '%s%s〜%s%s' % (w['name'], head, mdr(w['end']), tm),
                                'date': w['end'], 'url': url})
        else:
            tm = (' ' + w['start_hm']) if w['start_hm'] else ''
            tickets.append({'type': '%s%s%s%s発売〜' % (w['name'], head, mdr(w['start']), tm),
                            'date': e, 'startDate': w['start'], 'saleEndUnknown': True, 'url': url})
    seen_k, uniq = set(), []
    for t in tickets:
        k = (t['type'], t['date'], t.get('startDate'))
        if k not in seen_k:
            seen_k.add(k)
            uniq.append(t)
    if not uniq:
        return None, '載せる枠が無い（受付の案内がまだ無い・締切が過ぎた・読めない %d）' % len(bad)
    name = '宝塚歌劇 ' + show
    troupe = ev.get('troupe')
    label = ('%s %s' % (BT.jp(s), pref) if s == e else '%s〜%s %s' % (BT.jp(s), BT.jp(e), pref)).strip()
    ent = {
        'artist': ('宝塚歌劇' + troupe) if troupe else name,
        'name': name,
        'date': e,
        'dateLabel': label,
        'venue': venue or '（会場未定）',
        'prefecture': pref,
        'genre': 'new',
        '_genre': '',
        '_extraGenres': [],
        '_srcgenre': 'takarazuka:',
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'takarazuka': ev['page']},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
    }
    rv = ['ジャンル：売り場に分類の札が無い']
    if not pref:
        rv.append('県：ページ・調べた表から決まらない（推測しない）')
    ent['_review'] = ' / '.join(rv)
    ent['_prefFrom'] = [how]
    if bad:
        ent['_unknownState'] = bad
    return ent, None


def venue_prefs(events):
    """全ページの「劇場 [県]」から 劇場→県 の表（1つに揃っている時だけ）。"""
    m = {}
    for ev in events:
        p = short_pref(ev.get('venue_pref'))
        if ev.get('venue') and p:
            m.setdefault(ev['venue'], set()).add(p)
    return {k: list(v)[0] for k, v in m.items() if len(v) == 1}


def _selftest():
    today = '2026-11-20'
    now = datetime.datetime(2026, 11, 20, 12, 0)
    assert parse_period('公演期間：2026年12月12日（土） - 2027年1月24日（日）') == ('2026-12-12', '2027-01-24')
    assert parse_period('公演期間：2026年10月17日（土） - 11月22日（日）') == ('2026-10-17', '2026-11-22')
    assert year_of(1, 9, '土', '2027-03-14') == datetime.date(2027, 1, 9)
    assert year_of(1, 9, '金', '2027-03-14') is None
    assert hm_of('朝10時から') == '10:00' and hm_of('10:00') == '10:00' and hm_of('から') is None
    ev = {'page': 'https://kageki.hankyu.co.jp/revue/2026/x/ticket_takarazuka.html', 'url': 'u',
          'show': '月組公演 『天穹のアルテミス』', 'troupe': '月組', 'venue': '宝塚大劇場', 'venue_pref': '兵庫県',
          'period': '公演期間：2026年12月12日（土） - 2027年1月24日（日）', 'title_raw': 'チケット：宝塚大劇場 | x | y',
          'sections': [
              {'h3': '先行販売', 'sets': [{'h4': '宝塚友の会', 'lines': [
                  '■「第1抽選方式」', '申込期間：10月3日（土）10:00〜10月4日（日）23:00', '結果照会：10月7日（水）10:00〜',
                  '■「第3抽選方式」', '申込期間：11月18日（水）10:00〜11月26日（木）23:00']},
                  {'h4': '', 'lines': ['※期間中…']}]},
              {'h3': '', 'sets': [{'h4': '宝塚歌劇共通ID＋（プラス）', 'lines': [
                  '■「抽選方式」', '申込期間：11月28日（土）10:00〜11月29日（日）23:00']}]},
              {'h3': '一般前売 ※11月21日（土）前売開始', 'sets': [
                  {'h4': '宝塚歌劇Webチケットサービス（インターネット販売）', 'lines': ['11月21日（土）朝10時から']}]},
              {'h3': '', 'sets': [{'h4': '宝塚大劇場・電話受付', 'lines': ['11月24日（火）朝10時からご観劇日の前日まで']}]},
              {'h3': '', 'sets': [{'h4': '宝塚歌劇公式リセールサービス', 'lines': ['一般前売開始日の3日後から']}]}]}
    e, why = build(json.loads(json.dumps(ev)), today, now)
    assert e, why
    assert e['tickets'] == [
        {'type': '宝塚友の会先行・第3抽選方式（兵庫 12/12〜R9年 1/24公演）〜11/26 23:00', 'date': '2026-11-26', 'url': ev['page']},
        {'type': '宝塚歌劇共通ID＋先行・抽選方式（兵庫 12/12〜R9年 1/24公演）11/28 10:00発売', 'date': '2026-11-29',
         'startDate': '2026-11-28', 'url': ev['page']},
        {'type': '一般前売（兵庫 12/12〜R9年 1/24公演）11/21 10:00発売〜', 'date': '2027-01-24', 'startDate': '2026-11-21',
         'saleEndUnknown': True, 'url': ev['page']}], e['tickets']
    assert e['name'] == '宝塚歌劇 月組公演 『天穹のアルテミス』' and e['artist'] == '宝塚歌劇月組' and e['date'] == '2027-01-24'
    assert e['dateLabel'] == '2026年12月12日(土)〜2027年1月24日(日) 兵庫' and e['_genre'] == '' and e['genre'] == 'new'
    # Web の欄が無い一般前売＝h3 の日付だけ・時刻なし
    ev2 = dict(json.loads(json.dumps(ev)), venue='梅田芸術劇場メインホール', venue_pref='大阪府',
               period='公演期間：2026年12月24日（木） - 12月30日（水）',
               sections=[{'h3': '一般前売 ※10月31日（土）前売開始', 'sets': [{'h4': '', 'lines': ['インターネット、各プレイガイド']},
                                                                      {'h4': '梅田芸術劇場', 'lines': []}]}])
    t = build(ev2, today, now)[0]['tickets']
    assert t == [{'type': '一般前売（大阪 12/24〜12/30公演）10/31発売〜', 'date': '2026-12-30', 'startDate': '2026-10-31',
                  'saleEndUnknown': True, 'url': ev['page']}], t
    # 県：ページに無い → 他のページの同じ劇場 → 調べた表 → 空
    ev3 = dict(json.loads(json.dumps(ev)), venue='', venue_pref='', title_raw='チケット：宝塚バウホール | x | y')
    e3 = build(ev3, today, now)[0]
    assert e3['venue'] == '宝塚バウホール' and e3['prefecture'] == '兵庫' and e3['_prefFrom'] == ['venue_table']
    ev4 = dict(json.loads(json.dumps(ev)), venue='', venue_pref='', title_raw='チケット：KAAT神奈川芸術劇場 | x | y')
    assert build(ev4, today, now)[0]['prefecture'] == ''
    assert build(ev4, today, now, {'KAAT神奈川芸術劇場': '神奈川'})[0]['prefecture'] == '神奈川'
    # 受付の案内がまだ無い・終わった公演は載せない
    assert build(dict(json.loads(json.dumps(ev)), sections=[]), today, now)[0] is None
    assert build(dict(json.loads(json.dumps(ev)), period='公演期間：2026年10月1日（木） - 11月19日（木）'), today, now)[0] is None
    print('selftest OK: 会期/年を曜日で決める/方式ごとの先行（受付前・受付中・締切過ぎ）/一般前売＝発売〜/'
          'Web の欄が無い一般前売/電話・リセールは載せない/県の出所/R9年')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_takarazuka.json')
    ap.add_argument('--today', default=datetime.datetime.now(JST).date().isoformat())
    ap.add_argument('--index-venue', action='store_true',
                    help='他の売り場が index.html で同じ劇場名に付けた県も使う（既定は使わない）')
    a = ap.parse_args()
    if a.index_venue:
        print('  index.html の会場→県の表 %d 会場' % BD.load_index_venues())
    now = datetime.datetime.now(JST).replace(tzinfo=None)
    d = json.load(io.open(a.src, encoding='utf-8'))
    seen = venue_prefs(d['events'])
    out, skipped = [], []
    for ev in d['events']:
        e, why = build(ev, a.today, now, seen)
        if e:
            out.append(e)
        else:
            skipped.append({'url': ev.get('page'), 'name': ev.get('show'), 'why': why})
    out.sort(key=lambda e: (e['date'], e['name']))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump({'entries': out, 'skipped': skipped}, io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== 組み上がり %d件 / 載せない %d件 → %s ===' % (len(out), len(skipped), a.out))
    for s in skipped:
        print('  載せない: %s … %s' % ((s['name'] or '')[:30], s['why']))
    pf = {}
    for e in out:
        for k in e['_prefFrom']:
            pf[k] = pf.get(k, 0) + 1
    print('  県の出所:', pf, '/ 県が空のカード', sum(1 for e in out if not e['prefecture']))
    nt = sum(len(e['tickets']) for e in out)
    print('  枠 %d（発売前 %d・締切なし＝発売〜 %d）/ 読めない欄があるカード %d'
          % (nt, sum(1 for e in out for t in e['tickets'] if t.get('startDate') and not t.get('saleEndUnknown')),
             sum(1 for e in out for t in e['tickets'] if t.get('saleEndUnknown')),
             sum(1 for e in out if e.get('_unknownState'))))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
