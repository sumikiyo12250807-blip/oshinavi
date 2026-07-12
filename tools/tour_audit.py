# -*- coding: utf-8 -*-
"""【取りこぼし見える化・朝ルーチン常設】多会場ツアーの「公式全日程との照合対象」を炙り出す。

真因(2026-07-12 高嶋ちさ子で発覚): harvest は t.pia.jp 専業。ツアーの公演が
ぴあ以外の販売チャネル(ローチケ/キョードー/公式先行)に分かれていると、そのぴあバンドルに
無い日程は構造的に取れない。しかも公式全日程と照合していないので、抜けに気づけない
(サイレント取りこぼし)。ぴあの外を自動取得はできないが、「照合すべきツアー」を機械で
リストアップすれば、人が公式を1回見て差分を潰せる。

出力: ツアー系エントリ(全国ツアー表記 or 多会場 or 多公演日)を、公演日数の多い順に。
     各行に「捕捉した公演日数 / 会場数 / 公式linkの有無 / 全枠ぴあか」を出す。
     公式linkが無い & 公演日が多い ものほど照合優先度が高い。

  python tools/tour_audit.py            # 上位を表示
  python tools/tour_audit.py --all      # 全件
  python tools/tour_audit.py --id 2496  # 指定idの捕捉公演日を列挙
"""
import re, sys, json, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()

PREFS = ('北海道|青森|岩手|宮城|秋田|山形|福島|茨城|栃木|群馬|埼玉|千葉|東京|神奈川|新潟|富山|石川|'
         '福井|山梨|長野|岐阜|静岡|愛知|三重|滋賀|京都|大阪|兵庫|奈良|和歌山|鳥取|島根|岡山|広島|山口|'
         '徳島|香川|愛媛|高知|福岡|佐賀|長崎|熊本|大分|宮崎|鹿児島|沖縄')


def load():
    h = open('index.html', encoding='utf-8').read()
    return json.loads(re.search(r'const EVENTS = (\[.*?\]);', h, re.S).group(1))


def perf_dates(ev):
    """tickets の type から公演日(県 M/D公演)を抜いてユニーク化。締切でなく公演の識別。"""
    s = set()
    for t in ev.get('tickets', []):
        for m in re.finditer(r'（([^（）]*?)(\d{1,2}/\d{1,2})(?:[〜~]\d{1,2}/\d{1,2})?公演）', t.get('type', '')):
            s.add((m.group(1).strip('・ 　'), m.group(2)))
    return s


def is_tour(ev):
    v = ev.get('venue', '') or ''
    if 'ツアー' in v:
        return True
    if v.count('／') >= 1:               # 複数会場を／で列挙
        return True
    if len(perf_dates(ev)) >= 4:         # 4公演日以上
        return True
    return False


def pia_only(ev):
    urls = [(ev.get('links') or {}).get(k, '') for k in ('pia', 'rakuten', 'lawson', 'eplus')]
    urls += [t.get('url', '') for t in ev.get('tickets', [])]
    urls = [u for u in urls if u]
    return all('pia' in u for u in urls) if urls else True


def main():
    E = load()
    if '--id' in sys.argv:
        i = int(sys.argv[sys.argv.index('--id') + 1])
        ev = [x for x in E if x['id'] == i][0]
        pd = sorted(perf_dates(ev), key=lambda x: x[1])
        print(f"id={i} {ev.get('artist','')}")
        print(f"  会場: {ev.get('venue','')}")
        print(f"  捕捉した公演日 {len(pd)}件:")
        for pref, md in pd:
            print(f"    {pref} {md}")
        print("  → 公式サイトの全日程と件数を照合。多い側があれば各プレイガイドで裏取りして買えるものだけ補完。")
        return
    tours = [e for e in E if is_tour(e)]
    rows = []
    for e in tours:
        rows.append((len(perf_dates(e)), e['id'], (e.get('artist') or '')[:32],
                     bool((e.get('links') or {}).get('official')), pia_only(e)))
    rows.sort(reverse=True)
    limit = len(rows) if '--all' in sys.argv else 30
    print(f'=== ツアー監査 (today={TODAY}) 対象{len(tours)}件 / 公演日多い順 ===')
    print('  公演日 id     公式link 全ぴあ  アーティスト')
    for n, i, a, off, po in rows[:limit]:
        flag = '' if off else ' ⚠️公式link無=照合先不明'
        print(f"  {n:>3}日  {i:<5} {'有' if off else '無 '}    {'ぴあ専' if po else '複数所'}  {a}{flag}")
    if limit < len(rows):
        print(f'  … 他 {len(rows)-limit}件（--all で全件）')
    print('\n【使い方】公演日が多く公式link無しのツアーほど、ぴあ以外チャネル(ローチケ/キョードー)の'
          '取りこぼしリスク大。公式を1回開いて全日程と件数照合→差分を各プレイガイドで裏取り→買えるものだけ補完。')


if __name__ == '__main__':
    main()
