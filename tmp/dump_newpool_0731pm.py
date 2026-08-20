# -*- coding: utf-8 -*-
"""新着プール全件を目視チェック用にダンプ＋機械で拾える怪しさに印を付ける。"""
import json, re, sys, unicodedata
sys.stdout.reconfigure(encoding='utf-8')

PREF = ('北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|福井|'
        '山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|徳島|香川|'
        '愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄')
PREF_RE = re.compile(PREF)

h = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
news = [e for e in EVENTS if e.get('genre') == 'new']

for e in news:
    flags = []
    tks = e.get('tickets') or []
    # 千秋楽 date が dateLabel の終端と食い違わないか（表記から年月日を拾って比較）
    ymd = re.findall(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or '')
    if ymd:
        last = '%04d-%02d-%02d' % tuple(int(x) for x in ymd[-1])
        if last != e['date']:
            flags.append('date≠dateLabel終端(%s)' % last)
    # バッジの県名と prefecture の整合
    bpref = set()
    for t in tks:
        mm = re.search(r'（([^）]*?)\s*[\d]', t['type'])
        if mm:
            bpref |= set(PREF_RE.findall(mm.group(1)))
    if e['prefecture'] != '全国' and bpref and bpref != {e['prefecture']}:
        flags.append('県ズレ pref=%s badge=%s' % (e['prefecture'], '・'.join(sorted(bpref))))
    if e['prefecture'] == '全国' and len(bpref) <= 1:
        flags.append('全国なのにバッジ県が%d個' % len(bpref))
    # 券種名の省略記号・囲み残り
    for t in tks:
        if '…' in t['type'] or '...' in t['type']:
            flags.append('券種に…省略あり')
        if re.search(r'[／【〔［＜]', t['type']) and not re.search(r'【[^】]*】', t['type']):
            flags.append('券種に区切り記号残り')
    # 2027公演のR9年表記
    for t in tks:
        if re.search(r'R9年', t['type']):
            pass
    if e['date'] >= '2027-01-01' and not any('R9年' in t['type'] or 'R10年' in t['type'] for t in tks):
        flags.append('2027公演なのにR9年表記なし(要確認)')
    # links
    lk = e.get('links') or {}
    if not lk.get('pia') and not lk.get('rakuten'):
        flags.append('主要ベンダーlinkなし')
    uniq = {t.get('url') for t in tks if t.get('url')}
    if len(uniq) > 1 and len(uniq) < len([t for t in tks if t.get('url')]):
        pass
    if len(tks) > 1 and any(t.get('url') for t in tks) and not all(t.get('url') for t in tks):
        flags.append('ticket.urlが一部だけ＝誤誘導の恐れ')

    print('%d  %s' % (e['id'], e['name']))
    print('    %s / %s / 千秋楽=%s / _genre=%s%s' % (
        e['prefecture'], e['dateLabel'], e['date'], e.get('_genre'),
        ' / amazon=有' if (lk.get('amazon')) else ''))
    print('    venue=%s' % e['venue'])
    for t in tks:
        print('      - %s | date=%s start=%s%s' % (
            t['type'], t['date'], t.get('startDate', '-'), ' url有' if t.get('url') else ''))
    if flags:
        print('    ⚠️ ' + ' / '.join(sorted(set(flags))))
    print()
