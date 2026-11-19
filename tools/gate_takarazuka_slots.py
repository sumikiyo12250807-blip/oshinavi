# -*- coding: utf-8 -*-
"""宝塚歌劇 由来の枠の番人＝**公演のチケットページを読み直して、組み立てとは別の読み方で枠を作り、全件突合**する。

  python tools/gate_takarazuka_slots.py                          … index.html の宝塚の枠を全部照合
  python tools/gate_takarazuka_slots.py --ids 1,2                … id 指定
  python tools/gate_takarazuka_slots.py --built tmp/x1120/newv/takarazuka/built.json   … 投入前の組み上がりを照合
  python tools/gate_takarazuka_slots.py --selftest

終了コード 0＝全一致 / 2＝食い違い・読めない あり（投入・push の前に 0 を確かめる）

## 組み立て（takarazuka_harvest＋build_takarazuka_entries）と**別に**作る
- 読み方が違う＝組み立ては正規表現で `<section>`・`<div class="set">` を切って行にする。
  番人は **html.parser で字句を頭から順に読み**、「いまの h3・いまの h4」を持ちながら文字の行を拾う。
- 年＝組み立ては「年の候補を2つ試す」。番人は**千秋楽から1日ずつ366日さかのぼって**月日と曜日が合う日を数える。
- 共有するのは決まりだけ（先行は方式ごと・電話/リセール/他の売り場は載せない・一般前売は Web の欄＝発売〜、
  Web の欄が無ければ h3 の日付だけ・時刻は書いてある時だけ）。
- バッジの文字を**読み戻して**（受付名・県・会期・発売日時／締切・「〜」）比べる。カードの日付＝千秋楽・会場・県・公演名も見る。
- `--built` の時は**売り場にあって組み上がりに無いページ**（取りこぼし）も数える（組み上がりに出てきたページの「会場を選択」から辿る）。
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


TZ = _load('takarazuka_harvest')      # fetch（ページを読むだけ）
if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
REPORT = 'tmp/gate_takarazuka_report.txt'
JST9 = datetime.timedelta(hours=9)
PREFS = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 '
         '岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 '
         '長崎 熊本 大分 宮崎 鹿児島 沖縄').split()
YOUBI = '月火水木金土日'
BASE = 'https://kageki.hankyu.co.jp'


class Reader(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ''
        self.active = ''
        self.period = ''
        self.links = set()
        self.started = False
        self.h3 = ''
        self.h4 = ''
        self.cap = None          # 'title' / 'active' / 'period' / 'h2' / 'h3' / 'h4'
        self.buf = []
        self.line = []
        self.items = []          # (h3, h4, 行)

    def _txt(self):
        s = ' '.join(''.join(self.buf).replace('　', ' ').split())
        self.buf = []
        return s

    def _endline(self):
        s = ' '.join(''.join(self.line).replace('　', ' ').split())
        self.line = []
        if s and self.started:
            self.items.append((self.h3, self.h4, s))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a' and re.match(r'/revue/\d{4}/[\w\-]+/ticket_[\w\-]+\.html', a.get('href') or ''):
            self.links.add(a['href'])
        if tag == 'title':
            self.cap, self.buf = 'title', []
        elif tag == 'a' and a.get('class') == 'active':
            self.cap, self.buf = 'active', []
        elif tag == 'p' and a.get('class') == 'period':
            self.cap, self.buf = 'period', []
        elif tag == 'h2':
            self.cap, self.buf = 'h2', []
        elif tag in ('h3', 'h4') and self.started:
            self._endline()
            self.cap, self.buf = tag, []
        elif tag == 'div' and a.get('class') == 'set' and self.started:
            self._endline()
            self.h4 = ''
        elif tag == 'section' and self.started:
            self._endline()
        elif tag in ('br', 'p', 'li', 'dd') and self.started:
            self._endline()
        elif tag == 'footer':
            self._endline()
            self.started = False

    def handle_endtag(self, tag):
        if self.cap == 'title' and tag == 'title':
            self.title = self._txt()
            self.cap = None
        elif self.cap == 'active' and tag == 'a':
            self.active = self._txt()
            self.cap = None
        elif self.cap == 'period' and tag == 'p':
            self.period = self._txt()
            self.cap = None
        elif self.cap == 'h2' and tag == 'h2':
            if 'チケットお求め方法' in self._txt():
                self.started = True
            self.cap = None
        elif self.cap in ('h3', 'h4') and tag == self.cap:
            t = self._txt()
            if self.cap == 'h3':
                self.h3 = t if t else self.h3
                self.h4 = ''
            else:
                self.h4 = t
            self.cap = None
        elif tag in ('p', 'li', 'dd') and self.started:
            self._endline()

    def handle_data(self, data):
        if self.cap:
            self.buf.append(data)
        elif self.started:
            self.line.append(data)


def read_page(h):
    r = Reader()
    r.feed(h)
    r.close()
    return r


def back_to(mo, da, wd, last):
    """千秋楽から1日ずつさかのぼって、月日（と曜日）が合う日。1つでなければ None。"""
    hits, d = [], last
    for _ in range(367):
        if d.month == mo and d.day == da and (not wd or YOUBI[d.weekday()] == wd):
            hits.append(d)
        d -= datetime.timedelta(days=1)
    return hits[0] if len(hits) == 1 else None


def period_days(s):
    ds = re.findall(r'(?:(\d{4})年\s*)?(\d{1,2})月\s*(\d{1,2})日', s or '')
    if not ds or not ds[0][0]:
        return None
    a = datetime.date(int(ds[0][0]), int(ds[0][1]), int(ds[0][2]))
    if len(ds) == 1:
        return a, a
    b = datetime.date(int(ds[1][0] or a.year), int(ds[1][1]), int(ds[1][2]))
    if not ds[1][0] and b < a:
        b = b.replace(year=b.year + 1)
    return a, b


def r9(d):
    return ('R%d年 %d/%d' % (d.year - 2018, d.month, d.day)) if d.year >= 2027 else '%d/%d' % (d.month, d.day)


D = r'(\d{1,2})月\s*(\d{1,2})日\s*(?:[（(]\s*(\S)[^）)]*[）)])?'


def clock(s):
    m = re.match(r'\s*(?:朝|午前)?\s*(\d{1,2})(?:[:：](\d{2})|時)', s or '')
    return ('%d:%s' % (int(m.group(1)), m.group(2) or '00')) if m else None


def expected(r, pref, now):
    """ページ → 期待する枠（バッジを読み戻した形と同じキー）の集合と、読めない説明。"""
    days = period_days(r.period)
    if not days:
        return None, ['会期が読めない']
    a, b = days
    span = r9(a) if a == b else '%s〜%s' % (r9(a), ('%d/%d' % (b.month, b.day)) if a.year == b.year else r9(b))
    paren = '%s公演' % span
    out, bad = set(), []
    method = {}
    web_seen = {}
    for h3, h4, ln in r.items:
        if h3.startswith('先行'):
            if not h4 or re.search(r'電話|リセール|お問い合わせ|インフォメーション|団体', h4):
                continue
            org = re.sub(r'（[^）]*）', '', h4).strip()
            m = re.match(r'■\s*「([^」]+)」', ln)
            if m:
                method[org] = m.group(1)
                continue
            m = re.match(r'申込期間[：:]\s*' + D + r'\s*(\S*)\s*[〜～~]\s*' + D + r'\s*(\S*)', ln)
            if not m:
                continue
            s = back_to(int(m.group(1)), int(m.group(2)), m.group(3), b)
            e = back_to(int(m.group(5)), int(m.group(6)), m.group(7), b)
            if not s or not e:
                bad.append('申込期間の年が決まらない: %s' % ln[:40])
                continue
            sh, eh = clock(m.group(4)), clock(m.group(8))
            nm = org + '先行' + (('・' + method[org]) if method.get(org) else '')
            end_at = datetime.datetime(e.year, e.month, e.day, *[int(x) for x in (eh or '23:59').split(':')])
            st_at = datetime.datetime(s.year, s.month, s.day, *[int(x) for x in (sh or '0:00').split(':')])
            if end_at < now:
                continue
            if st_at > now:
                out.add((nm, pref, paren, 'sale', r9(s) + ((' ' + sh) if sh else ''), False, e.isoformat(), s.isoformat()))
            else:
                out.add((nm, pref, paren, 'end', r9(e) + ((' ' + eh) if eh else ''), False, e.isoformat(), None))
        elif h3.startswith('一般前売'):
            web_seen.setdefault(h3, False)
            if 'Webチケットサービス' not in h4:
                continue
            if web_seen[h3]:
                continue                 # Web の欄の1行目だけ
            web_seen[h3] = True
            m = re.match(D + r'\s*(.*)$', ln)
            if not m:
                bad.append('一般前売の日付が読めない: %s' % ln[:40])
                continue
            d = back_to(int(m.group(1)), int(m.group(2)), m.group(3), b)
            if not d:
                bad.append('一般前売の年が決まらない: %s' % ln[:40])
                continue
            c = clock(m.group(4))
            out.add(('一般前売', pref, paren, 'sale〜', r9(d) + ((' ' + c) if c else ''), True, b.isoformat(), d.isoformat()))
    for h3, seen in web_seen.items():
        if seen:
            continue
        m = re.search(r'※\s*' + D + r'\s*前売開始', h3)
        d = back_to(int(m.group(1)), int(m.group(2)), m.group(3), b) if m else None
        if d:
            out.add(('一般前売', pref, paren, 'sale〜', r9(d), True, b.isoformat(), d.isoformat()))
        else:
            bad.append('一般前売の見出しの日付が読めない: %s' % h3[:40])
    return out, bad


BADGE_RE = re.compile(r'^(?P<name>.+?)（(?:(?P<pref>(?!R\d+年)[^\s（）]+) )?'
                      r'(?P<span>(?:R\d+年 )?\d{1,2}/\d{1,2}(?:〜(?:R\d+年 )?\d{1,2}/\d{1,2})?公演)）'
                      r'(?:(?P<sale>(?:R\d+年 )?\d{1,2}/\d{1,2}(?: \d{1,2}:\d{2})?)発売(?P<open>〜)?'
                      r'|〜(?P<end>(?:R\d+年 )?\d{1,2}/\d{1,2}(?: \d{1,2}:\d{2})?))$')


def badge_key(t):
    m = BADGE_RE.match(t.get('type') or '')
    if not m:
        return None
    if m.group('sale'):
        kind = 'sale〜' if m.group('open') else 'sale'
        return (m.group('name'), m.group('pref') or '', m.group('span'), kind, m.group('sale'),
                bool(t.get('saleEndUnknown')), t.get('date'), t.get('startDate'))
    return (m.group('name'), m.group('pref') or '', m.group('span'), 'end', m.group('end'),
            bool(t.get('saleEndUnknown')), t.get('date'), t.get('startDate'))


def check_entry(e, r, now):
    ng = []
    reg = [t for t in e.get('tickets') or [] if 'kageki.hankyu.co.jp' in (t.get('url') or '')]
    rk = []
    for t in reg:
        k = badge_key(t)
        if k is None:
            ng.append('バッジの文字が読めない: %s' % t.get('type'))
            continue
        rk.append(k)
        if k[1] and k[1] not in PREFS:
            ng.append('バッジの県が県名でない: %s' % t.get('type'))
    pref = e.get('prefecture') or ''
    m = re.search(r'\[([^\]]+)\]\s*$', r.active)
    page_pref = re.sub(r'[都府県]$', '', m.group(1)) if m and m.group(1) != '北海道' else (m.group(1) if m else '')
    if page_pref and page_pref != pref:
        ng.append('ページの県「%s」≠ カードの県「%s」' % (page_pref, pref))
    exp, bad = expected(r, pref, now)
    if exp is None:
        return ng + bad
    for k in sorted(set(rk) - exp, key=str):
        ng.append('登録にだけある: %s' % (k,))
    for k in sorted(exp - set(rk), key=str):
        ng.append('売り場にだけある: %s' % (k,))
    if len(rk) != len(set(rk)):
        ng.append('同じ枠が2つ以上ある')
    a, b = period_days(r.period)
    if e.get('date') != b.isoformat():
        ng.append('カードの日付 %s ≠ 千秋楽 %s' % (e.get('date'), b))
    if '%d年%d月%d日' % (a.year, a.month, a.day) not in (e.get('dateLabel') or ''):
        ng.append('dateLabel に初日 %s が無い: %s' % (a, e.get('dateLabel')))
    venue = re.sub(r'\s*\[[^\]]*\]\s*$', '', r.active).strip() or \
        re.sub(r'^チケット[：:]\s*', '', r.title.split('|')[0]).strip()
    if venue != e.get('venue'):
        ng.append('会場「%s」≠ カード「%s」' % (venue, e.get('venue')))
    parts = [x.strip() for x in r.title.split('|')]
    if len(parts) >= 3 and e.get('name') != '宝塚歌劇 ' + parts[1]:
        ng.append('公演名が違う: 登録「%s」／ページ「%s」' % (e.get('name'), parts[1]))
    return ng + ['（読めない欄）' + x for x in bad]


def _selftest():
    now = datetime.datetime(2026, 11, 20, 12, 0)
    h = '''<html><head><title>チケット：宝塚大劇場 | 月組公演 『天穹』 | 宝塚歌劇公式ホームページ</title></head><body>
<ul><li><a href="/revue/2026/x/ticket_takarazuka.html" class="active"> 宝塚大劇場 [兵庫県] </a></li>
<li><a href="/revue/2026/x/ticket_tokyo.html"> 東京宝塚劇場 [東京都] </a></li></ul>
<p class="period">公演期間：2026年12月12日（土） - 2027年1月24日（日）</p>
<section class="article01"><h2>チケットお求め方法</h2></section>
<section class="article02"><h3>先行販売</h3><div class="box08"><div class="doc"><section><div class="set"><h4>宝塚友の会</h4>
<p class="txt">一般前売に先がけて<br/><br/><strong>■「第1抽選方式」</strong><br/> 申込期間：10月3日（土）10:00〜10月4日（日）23:00<br/>
<strong>■「第3抽選方式」</strong><br/> 申込期間：11月18日（水）10:00〜11月26日（木）23:00</p></div>
<div class="set"><dl><dd>※期間中</dd></dl></div></section></div></div></section>
<section class="article02"><div class="set"><h4>宝塚歌劇共通ID＋（プラス）</h4><p class="txt"><strong>■「抽選方式」</strong><br/>
申込期間：11月28日（土）10:00〜11月29日（日）23:00</p></div></section>
<section class="article02"><h3>一般前売　※11月21日（土）前売開始</h3><div class="set"><h4>宝塚歌劇Webチケットサービス（インターネット販売）</h4>
<section class="article01"><div class="list"><p>11月21日（土）朝10時から</p><ul><li>1回の購入は1公演2枚まで。</li></ul></div></section></div></section>
<section class="article02"><div class="set"><h4>宝塚大劇場・電話受付</h4><p class="txt">11月24日（火）朝10時から</p></div></section>
<footer>x</footer></body></html>'''
    r = read_page(h)
    assert r.period.startswith('公演期間：2026年12月12日') and r.active == '宝塚大劇場 [兵庫県]', (r.period, r.active)
    assert r.links == {'/revue/2026/x/ticket_takarazuka.html', '/revue/2026/x/ticket_tokyo.html'}
    U = 'https://kageki.hankyu.co.jp/revue/2026/x/ticket_takarazuka.html'
    good = {'name': '宝塚歌劇 月組公演 『天穹』', 'date': '2027-01-24', 'venue': '宝塚大劇場', 'prefecture': '兵庫',
            'dateLabel': '2026年12月12日(土)〜2027年1月24日(日) 兵庫', 'links': {'takarazuka': U}, 'tickets': [
                {'type': '宝塚友の会先行・第3抽選方式（兵庫 12/12〜R9年 1/24公演）〜11/26 23:00', 'date': '2026-11-26', 'url': U},
                {'type': '宝塚歌劇共通ID＋先行・抽選方式（兵庫 12/12〜R9年 1/24公演）11/28 10:00発売', 'date': '2026-11-29',
                 'startDate': '2026-11-28', 'url': U},
                {'type': '一般前売（兵庫 12/12〜R9年 1/24公演）11/21 10:00発売〜', 'date': '2027-01-24',
                 'startDate': '2026-11-21', 'saleEndUnknown': True, 'url': U}]}
    assert check_entry(good, r, now) == [], check_entry(good, r, now)
    T = good['tickets']
    for bad, why in (
            (dict(good, tickets=T[:2]), '枠が足りない'),
            (dict(good, tickets=[T[0], dict(T[1], date='2026-11-30'), T[2]]), '締切'),
            (dict(good, tickets=T[:2] + [dict(T[2], saleEndUnknown=False)]), '締切なしの印'),
            (dict(good, tickets=T[:2] + [dict(T[2], startDate='2025-11-21')]), '発売日の年'),
            (dict(good, date='2027-01-23'), 'カードの日付'),
            (dict(good, prefecture='東京'), '県'),
            (dict(good, venue='東京宝塚劇場'), '会場'),
            (dict(good, name='宝塚歌劇 別の公演'), '公演名')):
        assert check_entry(bad, r, now), why
    assert back_to(1, 9, '土', datetime.date(2027, 3, 14)) == datetime.date(2027, 1, 9)
    assert back_to(1, 9, '金', datetime.date(2027, 3, 14)) is None
    print('selftest OK: html.parser で字句を順に読む/h3・h4 を持ちながら行を拾う/年はさかのぼって数える/'
          '枠・締切・発売日・締切なしの印・日付・県・会場・公演名のずれで鳴る')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', default='')
    ap.add_argument('--built', default='', help='投入前の組み上がり（build_takarazuka_entries の出力）を照合する')
    ap.add_argument('--sleep', type=float, default=3.0)
    ap.add_argument('--report', default=REPORT)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        _selftest()
        sys.exit(0)
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None) + JST9
    if a.built:
        built = json.load(io.open(a.built, encoding='utf-8'))
        ents = built['entries']
        skipped_urls = {s.get('url') for s in built.get('skipped') or []}
        targets = [(e, i) for i, e in enumerate(ents)]
    else:
        h = io.open('index.html', encoding='utf-8', newline='').read()
        ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
        want = {int(x) for x in re.findall(r'\d+', a.ids)} if a.ids else None
        skipped_urls = set()
        targets = [(e, e['id']) for e in ev
                   if 'kageki.hankyu.co.jp' in json.dumps(e.get('links') or {}) + json.dumps(e.get('tickets') or [])
                   and (not want or e['id'] in want)]
    ok, ng, err = 0, [], []
    seen_pages, linked = set(), set()
    for e, key in targets:
        url = (e.get('links') or {}).get('takarazuka') or ''
        if not url:
            ng.append((e, key, ['宝塚のページの飛び先が無い']))
            continue
        try:
            r = read_page(TZ.fetch(url, sleep=a.sleep))
        except Exception as ex:
            err.append((e, key, url, str(ex)[:80]))
            continue
        seen_pages.add(url)
        linked |= {BASE + x for x in r.links}
        msgs = check_entry(e, r, now)
        bad_url = [t.get('url') for t in e.get('tickets') or []
                   if 'kageki.hankyu.co.jp' in (t.get('url') or '') and t.get('url') != url]
        if bad_url:
            msgs.append('枠の飛び先がカードのページと違う: %s' % bad_url[:2])
        if msgs:
            ng.append((e, key, msgs))
        else:
            ok += 1
    missing = []
    if a.built:
        for u in sorted(linked - seen_pages - skipped_urls):
            try:
                r = read_page(TZ.fetch(u, sleep=a.sleep))
            except Exception as ex:
                err.append(({}, '-', u, str(ex)[:80]))
                continue
            exp, bad = expected(r, '', now)
            days = period_days(r.period)
            if exp and days and days[1] >= now.date():
                missing.append((u, len(exp)))
    rep = io.open(a.report, 'w', encoding='utf-8')
    rep.write('=== gate_takarazuka_slots (now=%s) %s 対象%d件 ===\n' % (now.strftime('%Y-%m-%d %H:%M'), a.built or 'index.html', len(targets)))
    for e, key, msgs in ng:
        rep.write('\n🚨 id=%s %s\n    %s\n' % (key, (e.get('name') or '')[:40], (e.get('links') or {}).get('takarazuka')))
        for m in msgs:
            rep.write('    %s\n' % m)
    for u, n in missing:
        rep.write('\n🚨 取りこぼし（売り場にあって組み上がりに無い） %s 枠%d\n' % (u, n))
    for e, key, u, why in err:
        rep.write('❌ id=%s %s 読めなかった: %s\n' % (key, u, why))
    rep.write('\n=== 集計: 一致 %d / 🚨食い違い %d / 🚨取りこぼし %d / ❌読めなかった %d ===\n'
              % (ok, len(ng), len(missing), len(err)))
    rep.close()
    sys.stderr.write('gate_takarazuka_slots: match=%d ng=%d missing=%d fetcherr=%d -> %s\n'
                     % (ok, len(ng), len(missing), len(err), a.report))
    sys.exit(2 if (ng or err or missing) else 0)


if __name__ == '__main__':
    main()
