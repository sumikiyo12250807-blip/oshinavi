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


def need(e, today):
    """足すべき県のリスト（無ければ空）。県が空・全国・海外のエントリは見ない"""
    p = (e.get('prefecture') or '').strip()
    if not p or p in ('全国', '海外'):
        return []
    have = [x for x in p.split('・') if x]
    add = []
    for t in e.get('tickets') or []:
        if not t.get('saleUntilSoldOut') and (t.get('date') or '') < today:
            continue  # 締切が過ぎた枠は見ない（画面にも出ない）
        for x in RX.findall(t.get('type') or ''):
            if x not in have and x not in add:
                add.append(x)
    return add


def main():
    sys.stdout.reconfigure(encoding='utf-8')
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
