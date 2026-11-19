# -*- coding: utf-8 -*-
"""チケットWeb松竹 由来の枠の番人＝**発売日スケジュールのページを読み直して、組み立てとは別の読み方で枠を作り、全件突合**する。

  python tools/gate_shochiku_slots.py                          … index.html の松竹の枠を全部照合
  python tools/gate_shochiku_slots.py --ids 1,2                … id 指定
  python tools/gate_shochiku_slots.py --built tmp/x1120/newv/shochiku/built.json   … 投入前の組み上がりを照合
  python tools/gate_shochiku_slots.py --selftest

終了コード 0＝全一致 / 2＝食い違い・読めない あり（投入・push の前に 0 を確かめる）

## 組み立て（shochiku_harvest＋build_shochiku_entries）と**別に**作る
- 読み方が違う＝組み立ては正規表現で `<h4>`・`<table>` を切り出す。番人は **html.parser で字句を頭から順に読む**
  （コメントは字句として飛ばす・崩れた `<th>…</td>` も「次の td が来たら値」として読む）。
- 発売日の年＝組み立ては「年の候補を2つ試す」。番人は**千秋楽から1日ずつ366日さかのぼって**月日と曜日が合う日を数える。
- 共有するのは決まりだけ（窓口の行は載せない・会員の行は「…先行」・Web が無ければ載せない・発売は 10:00・締切なし＝発売〜）。
- バッジの文字を**読み戻して**（受付名・県・会期・発売日・時刻・「〜」）比べる。カードの日付＝千秋楽・会場・県も見る。
- `--built` の時は、**売り場にあって組み上がりに無い公演**（取りこぼし）も数える。
報告の形は他の売り場の番人とそろえる＝「🚨 id=<番号> 名前」。
"""
import argparse
import datetime
import html.parser
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


SH = _load('shochiku_harvest')        # fetch / PAGES（ページを読むだけ）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/gate_shochiku_report.txt'
JST9 = datetime.timedelta(hours=9)
PREFS = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 '
         '岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 '
         '長崎 熊本 大分 宮崎 鹿児島 沖縄').split()
CITIES = {'札幌': '北海道', '仙台': '宮城', 'さいたま': '埼玉', '千葉': '千葉', '横浜': '神奈川', '川崎': '神奈川',
          '相模原': '神奈川', '新潟': '新潟', '静岡': '静岡', '浜松': '静岡', '名古屋': '愛知', '京都': '京都',
          '大阪': '大阪', '堺': '大阪', '神戸': '兵庫', '岡山': '岡山', '広島': '広島', '北九州': '福岡',
          '福岡': '福岡', '熊本': '熊本'}
YOUBI = '月火水木金土日'


class Reader(html.parser.HTMLParser):
    """字句を頭から読む。劇場（box）→ 公演 → 表の行 を組む。"""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.prods = []
        self.box = None          # {'id','name','addr'}
        self.mode = None         # 'boxh4' / 'boxspan' / 'title' / 'agenda' / 'th' / 'td'
        self.buf = []
        self.cur = None
        self.label = None
        self.in_methods = False

    def _flush(self):
        s = ''.join(self.buf).replace('　', ' ')
        self.buf = []
        return ' '.join(s.split())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get('class') or ''
        if tag == 'h4' and 'page-block__title' in cls:
            self.box = {'id': a.get('id') or '', 'name': '', 'addr': ''}
            self.mode, self.buf = 'boxh4', []
        elif tag == 'span' and self.mode == 'boxh4':
            self.box['name'] = self._flush()
            self.mode = 'boxspan'
        elif tag == 'h4' and 'performance-title' in cls:
            self.cur = {'box': dict(self.box or {}), 'title': '', 'span': '', 'methods': set(), 'rows': []}
            self.prods.append(self.cur)
            self.mode, self.buf = 'title', []
        elif tag == 'p' and 'agenda_size' in cls and self.cur is not None:
            self.mode, self.buf = 'agenda', []
        elif tag == 'br' and self.mode in ('title', 'agenda', 'th', 'td', 'boxh4'):
            self.buf.append(' ')
        elif tag == 'span' and cls.endswith(' icon_size') and self.cur is not None:
            k = cls.split()[0]
            if k in ('web', 'tel', 'madoguchi'):
                self.cur['methods'].add(k)
        elif tag == 'th' and self.cur is not None:
            self.mode, self.buf = 'th', []
        elif tag == 'td' and self.cur is not None:
            if self.mode == 'th':
                self.label = self._flush()
            self.mode, self.buf = 'td', []

    def handle_endtag(self, tag):
        if self.mode == 'boxh4' and tag == 'h4':
            self.box['name'] = self._flush()
            self.mode = None
        elif self.mode == 'boxspan' and tag in ('span', 'h4'):
            self.box['addr'] = self._flush()
            self.mode = None
        elif self.mode == 'title' and tag == 'h4':
            self.cur['title'] = self._flush()
            self.mode = None
        elif self.mode == 'agenda' and tag == 'p':
            self.cur['span'] = self._flush()
            self.mode = None
        elif self.mode == 'th' and tag in ('th', 'td'):
            self.label = self._flush()
            self.mode = 'after_th'
        elif self.mode == 'td' and tag == 'td':
            self.cur['rows'].append((self.label or '', self._flush()))
            self.label, self.mode = None, None

    def handle_data(self, data):
        if self.mode in ('boxh4', 'boxspan', 'title', 'agenda', 'th', 'td'):
            self.buf.append(data)


def read_page(h):
    r = Reader()
    r.feed(h)
    r.close()
    return r.prods


def pref_from(addr):
    found = []
    for p in PREFS:
        full = p if p == '北海道' else p + ('都' if p == '東京' else '府' if p in ('大阪', '京都') else '県')
        if full in addr:
            found.append(p)
    if len(found) == 1:
        return found[0]
    if found:
        return ''
    for c, p in CITIES.items():
        if addr.startswith(c + '市'):
            return p
    return ''


def show_days(span):
    """会期 → (初日, 千秋楽) の date か None（終わりが日まで無い・読めない）。"""
    nums = re.findall(r'(?:(\d{4})年)?\s*(\d{1,2})月\s*(\d{1,2})日', span)
    if not nums or not nums[0][0]:
        return None
    y = int(nums[0][0])
    a = datetime.date(y, int(nums[0][1]), int(nums[0][2]))
    tail = span.split('日', 1)[1] if '日' in span else ''
    if not any(c in tail for c in '～〜~'):
        return a, a
    if len(nums) < 2:
        return None
    b = datetime.date(int(nums[1][0]) if nums[1][0] else y, int(nums[1][1]), int(nums[1][2]))
    if b < a:
        b = b.replace(year=b.year + 1)
    return a, b


def find_sale_day(txt, last):
    """「10月11日（日）～」→ 千秋楽から1日ずつさかのぼって、月日（と曜日）が合う日。1つでなければ None。"""
    m = re.match(r'\s*(\d{1,2})月\s*(\d{1,2})日\s*(?:[（(]\s*(\S)[^）)]*[）)])?\s*(?:\d{1,2}[:：]\d{2})?\s*([～〜~])?', txt)
    if not m or not m.group(4):
        return None
    hits = []
    d = last
    for _ in range(367):
        if d.month == int(m.group(1)) and d.day == int(m.group(2)) and \
                (not m.group(3) or YOUBI[d.weekday()] == m.group(3)):
            hits.append(d)
        d -= datetime.timedelta(days=1)
    return hits[0] if len(hits) == 1 else None


def r9(d):
    return ('R%d年 %d/%d' % (d.year - 2018, d.month, d.day)) if d.year >= 2027 else '%d/%d' % (d.month, d.day)


def expected(prod, today):
    """1公演 → 期待する枠のキーの集合（載せない公演は None・理由）。"""
    days = show_days(prod['span'])
    if not days:
        return None, '会期の終わりが読めない'
    a, b = days
    if b.isoformat() < today:
        return None, '終わった公演'
    if 'web' not in prod['methods']:
        return None, 'Web なし'
    out, bad = set(), []
    for label, txt in prod['rows']:
        nm = '・'.join(label.replace('「', '').replace('」', '').split())
        if '窓口' in nm or not nm:
            continue
        if '会員' in nm and '一般' not in nm and not nm.endswith('先行'):
            nm = nm + '先行'
        if re.search(r'[～〜~]\s*\d{1,2}月', txt):
            bad.append('終わりのある行（この番人は読まない形）: %s %s' % (label, txt))
            continue
        d = find_sale_day(txt, b)
        if not d:
            bad.append('発売日が1つに決まらない: %s %s' % (label, txt))
            continue
        span = r9(a) if a == b else '%s〜%s' % (r9(a), ('%d/%d' % (b.month, b.day)) if a.year == b.year else r9(b))
        tm = re.search(r'日\s*(?:[（(][^）)]*[）)])?\s*(\d{1,2})[:：](\d{2})', txt)
        out.add((nm, pref_from(prod['box'].get('addr') or ''), span, r9(d),
                 ('%d:%s' % (int(tm.group(1)), tm.group(2))) if tm else '10:00', True,
                 b.isoformat(), d.isoformat()))
    return out, bad


BADGE_RE = re.compile(r'^(?P<name>.+?)（(?:(?P<pref>(?!R\d+年)[^\s（）]+) )?'
                      r'(?P<span>(?:R\d+年 )?\d{1,2}/\d{1,2}(?:〜(?:R\d+年 )?\d{1,2}/\d{1,2})?)公演）'
                      r'(?P<sale>(?:R\d+年 )?\d{1,2}/\d{1,2}) (?P<time>\d{1,2}:\d{2})発売(?P<open>〜)?$')


def badge_key(t):
    m = BADGE_RE.match(t.get('type') or '')
    if not m:
        return None
    return (m.group('name'), m.group('pref') or '', m.group('span'), m.group('sale'), m.group('time'),
            bool(m.group('open')) and bool(t.get('saleEndUnknown')), t.get('date'), t.get('startDate'))


def check_entry(e, prod, today):
    ng = []
    reg = [t for t in e.get('tickets') or [] if 'ticket-web-shochiku.com' in (t.get('url') or '')]
    rk = []
    for t in reg:
        k = badge_key(t)
        if k is None:
            ng.append('バッジの文字が読めない: %s' % t.get('type'))
        else:
            rk.append(k)
            if k[1] and k[1] not in PREFS:
                ng.append('バッジの県が県名でない: %s' % t.get('type'))
        if t.get('url') != (e.get('links') or {}).get('shochiku'):
            ng.append('枠の飛び先がカードの売り場と違う: %s' % t.get('url'))
    exp, bad = expected(prod, today)
    if exp is None:
        ng.append('売り場では載せない公演（%s）' % bad)
        return ng
    for k in sorted(set(rk) - exp, key=str):
        ng.append('登録にだけある: %s' % (k,))
    for k in sorted(exp - set(rk), key=str):
        ng.append('売り場にだけある: %s' % (k,))
    if len(rk) != len(set(rk)):
        ng.append('同じ枠が2つ以上ある')
    a, b = show_days(prod['span'])
    if e.get('date') != b.isoformat():
        ng.append('カードの日付 %s ≠ 千秋楽 %s' % (e.get('date'), b.isoformat()))
    if '%d年%d月%d日' % (a.year, a.month, a.day) not in (e.get('dateLabel') or ''):
        ng.append('dateLabel に初日 %s が無い: %s' % (a, e.get('dateLabel')))
    if prod['box'].get('name') and prod['box']['name'] != e.get('venue'):
        ng.append('会場「%s」≠ カード「%s」' % (prod['box']['name'], e.get('venue')))
    p = pref_from(prod['box'].get('addr') or '')
    if p != (e.get('prefecture') or ''):
        ng.append('住所の県「%s」≠ カードの県「%s」' % (p, e.get('prefecture')))
    if bad:
        ng += ['（読めない行）' + x for x in bad]
    return ng


def load_all(sleep):
    """2枚のページを読む → {(ページURL, box, 公演名): prod}"""
    out = {}
    for region, url in SH.PAGES:
        h = SH.fetch(url, sleep=sleep)
        for p in read_page(h):
            p['page'] = url
            out[(url, p['box'].get('id') or '', p['title'])] = p
    return out


def _selftest():
    today = '2026-11-20'
    h = '''<h4 class="page-block__title title3" id="box1">歌舞伎座<br><span>東京都中央区銀座4-12-15</span></h4>
<div><h4 class="performance-title"><span><br></span> 十二月大歌舞伎 </h4>
<p class="mt1 md agenda_size"><strong>2026年12月2日（水）～12月25日（金）</strong></p>
<p class="md icon_list"><span class="li_line">松竹歌舞伎会</span><span class="shochikukabukikai icon_size">x</span></p>
<p class="md icon_list"><span class="li_line">販売方法</span><span class="web icon_size">Web</span></p>
<table><tr><th class="width-auto">「松竹歌舞伎会」ゴールド会員</th><td>11月11日（水）～</span></td></tr
<tr><th>一般販売<br></th><td>11月14日（土）～</td></tr><tr><th>窓口販売・お引き取り</td><td>11月16日（月）～</td></tr>></table>
<!-- <h4 class="performance-title">古い</h4> --></div>
<h4 class="page-block__title" id="box56">博多座<br><span>福岡市博多区下川端町2-1</span></h4>
<h4 class="performance-title">流白浪燦星<br>碧翠の麗城<br></h4><p class="agenda_size"><strong>2027年2月6日（土）～2月26日（金）</strong></p>'''
    ps = read_page(h)
    assert [p['title'] for p in ps] == ['十二月大歌舞伎', '流白浪燦星 碧翠の麗城'], ps
    p = ps[0]
    assert p['box'] == {'id': 'box1', 'name': '歌舞伎座', 'addr': '東京都中央区銀座4-12-15'}, p['box']
    assert p['methods'] == {'web'} and len(p['rows']) == 3 and p['rows'][2][0] == '窓口販売・お引き取り', p
    assert ps[1]['box']['name'] == '博多座' and pref_from(ps[1]['box']['addr']) == '福岡'
    good = {'name': '十二月大歌舞伎', 'date': '2026-12-25', 'venue': '歌舞伎座', 'prefecture': '東京',
            'dateLabel': '2026年12月2日(水)〜2026年12月25日(金) 東京', 'links': {'shochiku': 'https://x#box1'},
            'tickets': [
                {'type': '松竹歌舞伎会ゴールド会員先行（東京 12/2〜12/25公演）11/11 10:00発売〜', 'date': '2026-12-25',
                 'startDate': '2026-11-11', 'saleEndUnknown': True, 'url': 'https://www1.ticket-web-shochiku.com/x#box1'},
                {'type': '一般販売（東京 12/2〜12/25公演）11/14 10:00発売〜', 'date': '2026-12-25',
                 'startDate': '2026-11-14', 'saleEndUnknown': True, 'url': 'https://www1.ticket-web-shochiku.com/x#box1'}]}
    good['links']['shochiku'] = 'https://www1.ticket-web-shochiku.com/x#box1'
    assert check_entry(good, p, today) == [], check_entry(good, p, today)
    bads = (
        (dict(good, tickets=good['tickets'][:1]), '枠が足りない'),
        (dict(good, tickets=[dict(good['tickets'][0], startDate='2025-11-11')] + good['tickets'][1:]), '発売日の年'),
        (dict(good, tickets=[dict(good['tickets'][0], saleEndUnknown=False)] + good['tickets'][1:]), '締切なしの印'),
        (dict(good, tickets=[dict(good['tickets'][0], type=good['tickets'][0]['type'].replace('10:00', '11:00'))]
              + good['tickets'][1:]), '時刻'),
        (dict(good, date='2026-12-24'), 'カードの日付'),
        (dict(good, prefecture='大阪'), '県'),
        (dict(good, venue='新橋演舞場'), '会場'))
    for bad, why in bads:
        assert check_entry(bad, p, today), why
    assert find_sale_day('11月22日（日）～', datetime.date(2027, 1, 27)) == datetime.date(2026, 11, 22)
    assert find_sale_day('11月22日（月）～', datetime.date(2027, 1, 27)) is None
    assert show_days('2027年2月1日（月）～6月（未定）') is None
    assert show_days('2026年12月20日（日）～1月5日（火）')[1] == datetime.date(2027, 1, 5)
    print('selftest OK: html.parser で字句を順に読む/コメント・崩れた表/年はさかのぼって数える/'
          '枠・発売日・締切なしの印・時刻・日付・県・会場のずれで鳴る')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='', help='投入前の組み上がり（build_shochiku_entries の出力）を照合する')
    ap.add_argument('--today', default=(datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + JST9).date().isoformat())
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--report', default=REPORT)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        sys.exit(0)
    if a.built:
        ents = json.load(io.open(a.built, encoding='utf-8'))['entries']
        targets = [(e, i) for i, e in enumerate(ents)]
    else:
        h = io.open('index.html', encoding='utf-8', newline='').read()
        ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
        want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None
        targets = [(e, e['id']) for e in ev
                   if 'ticket-web-shochiku.com' in json.dumps(e.get('links') or {}) + json.dumps(e.get('tickets') or [])
                   and (not want or e['id'] in want)]
    err = []
    try:
        pages = load_all(a.sleep)
    except Exception as ex:
        pages = None
        err.append(('-', '-', 'ページが読めない: %s' % str(ex)[:80]))
    ok, ng, used = 0, [], set()
    for e, key in (targets if pages is not None else []):
        url = (e.get('links') or {}).get('shochiku') or ''
        page, _, box = url.partition('#')
        k = (page, box, e.get('name'))
        prod = pages.get(k)
        if not prod:
            ng.append((e, key, ['売り場のページにこの公演が無い（%s #%s「%s」）' % (page[-30:], box, e.get('name'))]))
            continue
        used.add(k)
        msgs = check_entry(e, prod, a.today)
        if msgs:
            ng.append((e, key, msgs))
        else:
            ok += 1
    missing = []
    if a.built and pages is not None:
        for k, p in pages.items():
            if k in used:
                continue
            exp, why = expected(p, a.today)
            if exp:
                missing.append((k, len(exp)))
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_shochiku_slots (today=%s) %s 対象%d件 ===\n' % (a.today, a.built or 'index.html', len(targets)))
    for e, key, msgs in ng:
        rep.write('\n🚨 id=%s %s\n    %s\n' % (key, (e.get('name') or '')[:40], (e.get('links') or {}).get('shochiku')))
        for m in msgs:
            rep.write('    %s\n' % m)
    for k, n in missing:
        rep.write('\n🚨 取りこぼし（売り場にあって組み上がりに無い） %s #%s「%s」 枠%d\n' % (k[0][-30:], k[1], k[2], n))
    for i, u, why in err:
        rep.write('❌ id=%s %s 読めなかった: %s\n' % (i, u, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / 🚨取りこぼし %d / ❌読めなかった %d ===\n'
              % (ok, len(ng), len(missing), len(err)))
    rep.close()
    sys.stderr.write('gate_shochiku_slots: match=%d ng=%d missing=%d fetcherr=%d -> %s\n'
                     % (ok, len(ng), len(missing), len(err), a.report))
    sys.exit(2 if (ng or err or missing) else 0)


if __name__ == '__main__':
    main()
