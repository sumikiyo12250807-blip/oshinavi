# -*- coding: utf-8 -*-
"""エントリの県（prefecture）に、まだ買える枠の括弧にある県が入っていない型を直す（足すだけ・消さない）

🆕2026-10-26 すちこ「それで全部県名問題は解決？」＝県が空の洗い出しのついでに見つけた型。
  41475 SALSATION は県=「福岡・大阪」なのに枠は東京・広島・埼玉にもあった。ヒールで後から足された会場の県が
  エントリの県に入らない（10/26 に 142件を直した）。画面の地域の絞り込みは枠の県で見るが、
  枠に県が無い時の受け皿・ホテルの検索・ai.html はエントリの県を使う。

  python tools/fill_entry_pref.py           # 下見（tmp/fill_entry_pref.txt）
  python tools/fill_entry_pref.py --apply   # 書く（ヒールのあと・push 前）＝番人 gate_fields N
"""
import datetime, io, json, re, sys

ROOT = 'C:/Users/user/oshinavi/'
PREFS = ('北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 新潟 富山 石川 福井 山梨 長野 岐阜 静岡 '
         '愛知 三重 滋賀 京都 大阪 兵庫 奈良 和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 宮崎 鹿児島 沖縄').split()
RX = re.compile(r'（(' + '|'.join(PREFS) + r')[ ・]')
PSET = set(PREFS)
# 🆕2026-11-04 抜き打ち 5162 山本彩（tmp/x1104/spot/rootcause.md）＝RX は括弧の**1つ目の県だけ**を見ていた。
#   「一般発売（埼玉・東京 R9年 1/14〜2/10公演）」の東京が拾えず、県が「…埼玉・広島」で東京なしのまま（全体 8件）。
#   括弧の頭の「県・県・県 」を全部読む。
RX_ALL = re.compile(r'（((?:' + '|'.join(PREFS) + r')(?:・(?:' + '|'.join(PREFS) + r'))*)[ ]')


def paren_prefs(ty, first_only=False):
    if first_only:
        return RX.findall(ty or '')
    return [x for m in RX_ALL.findall(ty or '') for x in m.split('・') if x in PSET]


def need(e, today, first_only=False):
    """足すべき県のリスト（無ければ空）。県が空・全国・海外のエントリは見ない
    first_only=True は 11/4 より前の数え方（番人 N が既存の件で push を止めないための比較用）"""
    p = (e.get('prefecture') or '').strip()
    if not p or p in ('全国', '海外'):
        return []
    have = [x for x in p.split('・') if x]
    add = []
    for t in e.get('tickets') or []:
        if not t.get('saleUntilSoldOut') and (t.get('date') or '') < today:
            continue  # 締切が過ぎた枠は見ない（画面にも出ない）
        for x in paren_prefs(t.get('type'), first_only):
            if x not in have and x not in add:
                add.append(x)
    return add


def _selftest():
    e = {'prefecture': '福岡・宮城・大阪・埼玉・広島',
         'tickets': [{'type': '一般発売（埼玉・東京 R9年 1/14〜2/10公演）〜12/22 23:59', 'date': '2026-12-22'}]}
    assert need(e, '2026-11-04') == ['東京'], need(e, '2026-11-04')
    assert need(e, '2026-11-04', first_only=True) == []
    e2 = {'prefecture': '東京', 'tickets': [{'type': '一般発売（大阪 11/6公演）〜11/5 23:59', 'date': '2026-11-05'}]}
    assert need(e2, '2026-11-04') == ['大阪']
    assert paren_prefs('一般発売【東京・大阪】（全国 12/1公演）') == []
    print('selftest OK: 括弧の県を全部読む（5162 埼玉・東京）')


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if '--selftest' in sys.argv:
        return _selftest()
    today = datetime.date.today().isoformat()
    P = ROOT + 'index.html'
    s = io.open(P, encoding='utf-8', newline='').read()
    i = s.index('const EVENTS = [') + len('const EVENTS = ')
    E, _ = json.JSONDecoder().raw_decode(s[i:])
    fix = {}
    for e in E:
        add = need(e, today)
        if add:
            p = e['prefecture'].strip()
            fix[e['id']] = (p, '・'.join([x for x in p.split('・') if x] + add))
    io.open(ROOT + 'tmp/fill_entry_pref.txt', 'w', encoding='utf-8').write(
        f'{len(fix)}件\n' + '\n'.join(f'{k} {a} → {b}' for k, (a, b) in fix.items()))
    if '--apply' not in sys.argv:
        print(f'下見 {len(fix)}件 → tmp/fill_entry_pref.txt')
        return
    idrx = re.compile(r'"id": ?(\d+),')
    ms = list(idrx.finditer(s, i))
    out, pos, n = [], 0, 0
    for j, m in enumerate(ms):
        k = int(m.group(1))
        if k not in fix:
            continue
        a = m.start()
        b = ms[j + 1].start() if j + 1 < len(ms) else len(s)
        seg = s[a:b]
        old, new = fix[k]
        pat = re.compile(r'("prefecture": ?)"' + re.escape(old) + '"')
        if len(pat.findall(seg)) != 1:
            continue
        out.append(s[pos:a])
        out.append(pat.sub(lambda mm: mm.group(1) + json.dumps(new, ensure_ascii=False), seg))
        pos = b
        n += 1
    out.append(s[pos:])
    io.open(P, 'w', encoding='utf-8', newline='').write(''.join(out))
    print(f'当てた {n} / {len(fix)}件')


if __name__ == '__main__':
    main()
