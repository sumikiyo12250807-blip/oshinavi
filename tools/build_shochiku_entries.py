# -*- coding: utf-8 -*-
"""チケットWeb松竹のハーベスト結果から OSHINAVI のエントリを組む（T-SQUARE形・1公演＝1カード）。

  python tools/build_shochiku_entries.py tmp/x1120/newv/shochiku/harvest.json --out tmp/x1120/newv/shochiku/built.json
  python tools/build_shochiku_entries.py --selftest

## 枠（tickets）の作り方＝**発売日の表の1行＝1枠**（窓口だけの行は載せない）
- 売り場に**終わりが書いていない**（「10月14日（水）～」）＝締切を作らない（[[feedback_sale_end_unknown_display]]）
  → type＝「受付名（県 会期公演）M/D 10:00発売〜」・startDate＝発売日・date＝千秋楽・saleEndUnknown:true
- 発売の時刻＝行に時刻があればそれ（「11月10日（火）12:00～」）、無ければページの凡例
  「チケットWeb松竹 … 販売開始は10:00～」の 10:00。**販売方法に Web がある公演だけ**。
  Web が無い公演は載せない（この売り場で買えない）。
- 「窓口販売・お引き取り」の行＝劇場の窓口だけ＝載せない。
- 「松竹歌舞伎会◯◯会員」の行＝会員の先行（誰でも見られるページに日付がある＝[[project_fc_presale_public]]）
  → 名前は「松竹歌舞伎会ゴールド会員先行」のように**会員の先行だと分かる形**にする。
- 年は書いていない＝**曜日が合い・会期の終わりより前・366日以内**の年が1つに決まる時だけ使う。決まらなければ載せない（推測しない）。
- 会期（公演日）＝ページの「2026年11月1日（日）～11月25日（水）」。終わりが「6月（未定）」など日まで無い公演は
  **カードの日付が作れない＝載せない**（報告に出す）。
- 終わった公演（千秋楽が今日より前）は載せない。

## 県・ジャンル
- 県＝劇場の見出しの住所（「東京都中央区…」）。県名が無い住所は**政令指定都市の名前**（「京都市」「福岡市」）だけで決める。
  決まらなければ空。
- ジャンル＝この売り場には分類の札が無い＝`_genre` は空（勝手に決めない）・genre は "new"。
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
    # 🚨読み込む道具は中で sys.stdout を差し替える＝前後のラッパーを握っておく（gate_tiget_slots と同じ手）
    prev = sys.stdout
    _KEEP.append(prev)
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _KEEP.append(sys.stdout)
    sys.stdout = prev
    return mod


BT = _load('build_tiget_entries')     # md / jp（同じ物差し）
TH = _load('tiget_harvest')           # PREF47
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JST = datetime.timezone(datetime.timedelta(hours=9))
WD = '月火水木金土日'
WEB_TIME = '10:00'   # ページの凡例「チケットWeb松竹 … (24時間受付・販売開始は10:00～)」
# 政令指定都市（市の名前で県が1つに決まる・事実の表）
CITY_PREF = {'札幌市': '北海道', '仙台市': '宮城', 'さいたま市': '埼玉', '千葉市': '千葉', '横浜市': '神奈川',
             '川崎市': '神奈川', '相模原市': '神奈川', '新潟市': '新潟', '静岡市': '静岡', '浜松市': '静岡',
             '名古屋市': '愛知', '京都市': '京都', '大阪市': '大阪', '堺市': '大阪', '神戸市': '兵庫',
             '岡山市': '岡山', '広島市': '広島', '北九州市': '福岡', '福岡市': '福岡', '熊本市': '熊本'}


def pref_of(addr):
    """住所 → 県（短い形）。県名が1つだけ出ている時／政令市の名前で始まる時だけ。"""
    a = addr or ''
    hits = {p if p == '北海道' else p[:-1] for p in TH.PREF47 if p in a}
    if len(hits) == 1:
        return hits.pop()
    if hits:
        return ''
    for c, p in CITY_PREF.items():
        if a.startswith(c):
            return p
    return ''


def parse_span(span):
    """会期の文字 → (初日, 千秋楽, 状態)。状態＝'ok' / 'end_unknown'（「～6月（未定）」など）/ 'unreadable'。"""
    m = re.match(r'\s*(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日', span or '')
    if not m:
        return None, None, 'unreadable'
    try:
        s = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None, None, 'unreadable'
    rest = span[m.end():]
    if not re.search(r'[～〜~]', rest):
        return s.isoformat(), s.isoformat(), 'ok'
    m2 = re.search(r'[～〜~]\s*(?:(\d{4})年)?\s*(\d{1,2})月\s*(\d{1,2})日', rest)
    if not m2:
        return s.isoformat(), None, 'end_unknown'
    y = int(m2.group(1)) if m2.group(1) else s.year
    try:
        e = datetime.date(y, int(m2.group(2)), int(m2.group(3)))
    except ValueError:
        return None, None, 'unreadable'
    if not m2.group(1) and e < s:
        e = datetime.date(y + 1, e.month, e.day)
    return s.isoformat(), e.isoformat(), 'ok'


def sale_date(txt, show_end):
    """発売日の文字「10月11日（日）～」「11月10日（火）12:00～」→ (発売日 iso, 終わり iso or None, 時刻 or None)
    か (None, 理由, None)。年は「曜日が合う・千秋楽より前・千秋楽の366日前より後」の年が1つに決まる時だけ。"""
    m = re.match(r'\s*(\d{1,2})月\s*(\d{1,2})日\s*(?:[（(]\s*([月火水木金土日])[^）)]*[）)])?\s*'
                 r'(?:(\d{1,2})[:：](\d{2}))?\s*([～〜~])?\s*(?:(\d{1,2})月\s*(\d{1,2})日)?', txt or '')
    if not m:
        return None, '発売日が読めない「%s」' % (txt or '')[:20], None
    hm = '%d:%s' % (int(m.group(4)), m.group(5)) if m.group(4) else None
    end = datetime.date.fromisoformat(show_end)
    cands = []
    for y in (end.year, end.year - 1):
        try:
            d = datetime.date(y, int(m.group(1)), int(m.group(2)))
        except ValueError:
            continue
        if m.group(3) and WD[d.weekday()] != m.group(3):
            continue
        if d <= end and (end - d).days <= 366:
            cands.append(d)
    if len(cands) != 1:
        return None, '発売日の年が1つに決まらない「%s」' % txt[:20], None
    d = cands[0]
    e = None
    if m.group(7):
        try:
            e = datetime.date(d.year, int(m.group(7)), int(m.group(8)))
            if e < d:
                e = datetime.date(d.year + 1, e.month, e.day)
        except ValueError:
            return None, '終わりの日が読めない「%s」' % txt[:20], None
    elif not m.group(6):
        return None, '「～」が無い＝発売日か締切か分からない「%s」' % txt[:20], None
    return d.isoformat(), (e.isoformat() if e else None), hm


def window_name(label):
    """表の受付の名前 → バッジの名前。窓口だけの行は None。"""
    nm = re.sub(r'\s+', '・', re.sub(r'[「」]', '', label or '').strip())
    if not nm or '窓口' in nm:
        return None
    if '会員' in nm and '一般' not in nm and not nm.endswith('先行'):
        nm += '先行'
    return nm


def mdr(iso):
    """'2027-01-05' → 'R9年 1/5'（2027年以降は R9年 を前に付ける）／2026年は '1/5'。"""
    y = int(iso[:4])
    s = BT.md(iso)
    return ('R%d年 %s' % (y - 2018, s)) if y >= 2027 else s


def span_text(s, e):
    if s == e:
        return mdr(s)
    return '%s〜%s' % (mdr(s), BT.md(e) if s[:4] == e[:4] else mdr(e))


def build(ev, today):
    """1公演 → (エントリ, None) か (None, 理由)。"""
    name = ev.get('title') or ''
    if not name:
        return None, '公演名が無い'
    s, e, st = parse_span(ev.get('span'))
    if st == 'unreadable':
        return None, '会期が読めない「%s」' % (ev.get('span') or '')[:30]
    if st == 'end_unknown':
        return None, '会期の終わりが日まで書いていない「%s」' % (ev.get('span') or '')[:30]
    if e < today:
        return None, '公演が終わっている'
    if 'web' not in (ev.get('methods') or []):
        return None, '販売方法に Web が無い＝この売り場で買えない'
    pref = pref_of(ev.get('address'))
    head = '（%s %s公演）' % (pref, span_text(s, e)) if pref else '（%s公演）' % span_text(s, e)
    tickets, unknown = [], []
    for label, txt in ev.get('rows') or []:
        nm = window_name(label)
        if not nm:
            continue
        sd, end, hm = sale_date(txt, e)
        if not sd:
            unknown.append('%s: %s' % (label[:20], end))
            continue
        t = {'type': '%s%s%s %s発売' % (nm, head, mdr(sd), hm or WEB_TIME), 'date': end or e, 'startDate': sd,
             'url': ev['url']}
        if end:
            if end < today:
                continue
            if sd <= today:
                t = {'type': '%s%s〜%s' % (nm, head, mdr(end)), 'date': end, 'url': ev['url']}
        else:
            t['type'] += '〜'
            t['saleEndUnknown'] = True
        tickets.append(t)
    seen, uniq = set(), []
    for t in tickets:
        k = (t['type'], t['date'], t.get('startDate'))
        if k not in seen:
            seen.add(k)
            uniq.append(t)
    if not uniq:
        return None, '載せる枠が無い（読めない行 %d）' % len(unknown)
    label = ('%s %s' % (BT.jp(s), pref) if s == e else '%s〜%s %s' % (BT.jp(s), BT.jp(e), pref)).strip()
    ent = {
        'artist': name,
        'name': name,
        'date': e,
        'dateLabel': label,
        'venue': ev.get('theater') or '（会場未定）',
        'prefecture': pref,
        'genre': 'new',
        '_genre': '',
        '_extraGenres': [],
        '_srcgenre': 'shochiku:',
        'price': None,
        'links': {'rakuten': None, 'lawson': None, 'pia': None, 'eplus': None, 'shochiku': ev['url']},
        'tickets': uniq,
        'verified': True,
        'verifiedAt': today,
        '_shochikuKey': ev['key'],
    }
    rv = ['ジャンル：売り場に分類の札が無い']
    if not pref:
        rv.append('県：劇場の住所から決まらない（推測しない）')
    if ev.get('no_web_note'):
        rv.append('注意書きに「チケットWeb松竹での販売はございません」の一文がある（一部の席・企画だけの話か人が見る）')
    ent['_review'] = ' / '.join(rv)
    if unknown:
        ent['_unknownState'] = unknown
    return ent, None


def _selftest():
    today = '2026-11-20'
    assert parse_span('2026年11月1日（日）～11月25日（水）') == ('2026-11-01', '2026-11-25', 'ok')
    assert parse_span('2026年12月20日（日）～1月5日（火）') == ('2026-12-20', '2027-01-05', 'ok')
    assert parse_span('2026年11月3日(火)～11月8日(日)')[1] == '2026-11-08'
    assert parse_span('2026年11月29日（日）15:30開演') == ('2026-11-29', '2026-11-29', 'ok')
    assert parse_span('2027年2月1日（月）～6月（未定）')[2] == 'end_unknown'
    assert parse_span('近日発表')[2] == 'unreadable'
    # 年は曜日で1つに決める（2026-11-22 は日曜）
    assert sale_date('11月22日（日）～', '2027-01-27') == ('2026-11-22', None, None)
    assert sale_date('11月22日（月）～', '2027-01-27')[0] is None            # 曜日が合わない＝載せない
    assert sale_date('10月19日（月 ）～', '2027-02-28') == ('2026-10-19', None, None)
    assert sale_date('11月10日（火）12:00～', '2026-11-29') == ('2026-11-10', None, '12:00')   # 行に時刻＝それを使う
    assert sale_date('12月5日（土）', '2027-02-26')[0] is None                  # 「～」が無い
    assert window_name('「松竹歌舞伎会」ゴールド会員') == '松竹歌舞伎会ゴールド会員先行'
    assert window_name('松竹歌舞伎会会員 一般') == '松竹歌舞伎会会員・一般'
    assert window_name('窓口販売・お引き取り') is None and window_name('一般発売') == '一般発売'
    assert pref_of('東京都中央区銀座4-12-15') == '東京' and pref_of('京都市東山区四条大橋東詰') == '京都'
    assert pref_of('福岡市博多区下川端町2-1') == '福岡' and pref_of('どこか') == ''
    ev = {'title': '十二月大歌舞伎', 'span': '2026年12月2日（水）～12月25日（金）', 'methods': ['web', 'tel'],
          'theater': '歌舞伎座', 'address': '東京都中央区銀座4-12-15', 'url': 'https://x/east.html#box1',
          'key': 'east#box1|十二月大歌舞伎',
          'rows': [('「松竹歌舞伎会」ゴールド会員', '11月11日（水）～'), ('一般販売', '11月14日（土）～'),
                   ('窓口販売・お引き取り', '11月16日（月）～')]}
    e, why = build(dict(ev), today)
    assert e, why
    assert e['tickets'] == [
        {'type': '松竹歌舞伎会ゴールド会員先行（東京 12/2〜12/25公演）11/11 10:00発売〜', 'date': '2026-12-25',
         'startDate': '2026-11-11', 'url': 'https://x/east.html#box1', 'saleEndUnknown': True},
        {'type': '一般販売（東京 12/2〜12/25公演）11/14 10:00発売〜', 'date': '2026-12-25',
         'startDate': '2026-11-14', 'url': 'https://x/east.html#box1', 'saleEndUnknown': True}], e['tickets']
    assert e['date'] == '2026-12-25' and e['dateLabel'] == '2026年12月2日(水)〜2026年12月25日(金) 東京'
    assert e['_genre'] == '' and e['genre'] == 'new' and e['links']['shochiku'] == 'https://x/east.html#box1'
    e5 = build(dict(ev, span='2026年11月29日（日）15:30開演', rows=[('松竹歌舞伎会会員 一般', '11月10日（火）12:00～')]), today)[0]
    assert e5['tickets'][0]['type'] == '松竹歌舞伎会会員・一般（東京 11/29公演）11/10 12:00発売〜', e5['tickets']
    # 2027年の会期＝R9年
    e2 = build(dict(ev, span='2027年1月3日（日）～1月27日（水）', rows=[('一般販売', '12月1日（火）～')]), today)[0]
    assert e2['tickets'][0]['type'] == '一般販売（東京 R9年 1/3〜1/27公演）12/1 10:00発売〜', e2['tickets']
    # 年をまたぐ会期
    e3 = build(dict(ev, span='2026年12月20日（日）～1月5日（火）'), today)[0]
    assert '（東京 12/20〜R9年 1/5公演）' in e3['tickets'][0]['type'], e3['tickets']
    # 載せない：終わった公演・Web が無い・会期の終わりが未定・曜日が合わない行だけ
    assert build(dict(ev, span='2026年11月1日（日）～11月19日（木）'), today)[0] is None
    assert build(dict(ev, methods=['tel', 'madoguchi']), today)[0] is None
    assert '日まで' in build(dict(ev, span='2027年2月1日（月）～6月（未定）'), today)[1]
    assert build(dict(ev, rows=[('一般販売', '11月14日（金）～')]), today)[0] is None
    # 県が決まらない＝バッジから県を落とす
    e4 = build(dict(ev, address='どこか'), today)[0]
    assert e4['prefecture'] == '' and e4['tickets'][0]['type'].startswith('松竹歌舞伎会ゴールド会員先行（12/2〜12/25公演）')
    print('selftest OK: 会期/年を曜日で決める/会員先行の名前/窓口は載せない/発売〜（締切なし）/R9年/年またぎ/'
          '終わった・Webなし・未定は載せない/県は住所と政令市だけ')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('--out', default='tmp/built_shochiku.json')
    ap.add_argument('--today', default=datetime.datetime.now(JST).date().isoformat())
    a = ap.parse_args()
    d = json.load(io.open(a.src, encoding='utf-8'))
    out, skipped = [], []
    for ev in d['events']:
        e, why = build(ev, a.today)
        if e:
            out.append(e)
        else:
            skipped.append({'url': ev.get('url'), 'name': ev.get('title'), 'why': why})
    out.sort(key=lambda e: (e['date'], e['name']))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump({'entries': out, 'skipped': skipped}, io.open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('=== 組み上がり %d件 / 載せない %d件 → %s ===' % (len(out), len(skipped), a.out))
    why = {}
    for s in skipped:
        k = re.sub(r'「.*', '', s['why'])
        why[k] = why.get(k, 0) + 1
    for k, v in sorted(why.items(), key=lambda x: -x[1]):
        print('  載せない: %s: %d件' % (k, v))
    print('  県が空のカード %d' % sum(1 for e in out if not e['prefecture']))
    nt = sum(len(e['tickets']) for e in out)
    print('  枠 %d（締切が書いていない＝発売〜 %d）/ 読めない行があるカード %d'
          % (nt, sum(1 for e in out for t in e['tickets'] if t.get('saleEndUnknown')),
             sum(1 for e in out if e.get('_unknownState'))))


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    main()
