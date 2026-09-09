# -*- coding: utf-8 -*-
"""ぴあの**枠ごと**に「予定枚数終了／販売終了」を付ける（mark_soldout の穴を埋める）。

  python tools/pia_mark_soldout_slots.py --ids 1147,4998        … 調べるだけ
  python tools/pia_mark_soldout_slots.py --ids 1147 --apply
  python tools/pia_mark_soldout_slots.py --selftest

## なぜ要るか

`tools/mark_soldout.py` は**エントリ単位**で、**買える枠が1つでもあれば即 alive を返して打ち切る**
（[[feedback_soldout_keep_visible]] の 2026-08-27 項に「未修正」と書いてある穴）。
＝同じエントリに「売り切れた枠」と「まだ買える枠」が混ざると、
**売り切れた枠が買えるフリのまま残る**。

実例（2026-09-10）＝id1147 安部恭弘。12/17 と R9年1/8 は発売前で生きているが、
大阪9/22 と 東京9/25 は**ぴあの実ページで [予定枚数終了]**だった。
同じ日に楽天側でも同型の穴（[[reference_rakuten_harvest]]）が見つかっている。

## 判定の作法

- 枠の `url`（無ければエントリの links.pia）を開き、**その枠の公演日のカードだけ**を見る
- そのカードが**全部「予定枚数終了/完売/売切」** → `soldout`
- 全部「販売終了/受付終了」など期間切れの言い方 → `soldout` ＋ `saleEnded`（弱いほうに倒す）
- 買える言い方が1つでもある／カードが見つからない → **触らない**
- 売り切れは**消さない**（[[feedback_soldout_keep_visible]]）
- 逆向きも見る＝買えるようになっていたら印を外す
"""
import argparse
import datetime
import json
import re
import sys
import time

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from build_pia_entries import fetch            # noqa: E402
from pia_statustext import statuses            # noqa: E402

TODAY = datetime.date.today().isoformat()
SOLD = re.compile(r'予定枚数終了|完売|売切')
ENDED = re.compile(r'販売終了|受付終了|終了しました')
ALIVE = re.compile(r'受付中|販売期間中|発売前|販売前|受付前|発売中')
BADGE = re.compile(r'（[^（）]*?((?:R\d+年\s*)?\d{1,2}/\d{1,2}(?:〜(?:R\d+年\s*)?\d{1,2}/\d{1,2})?)'
                   r'(?:\s+\d{1,2}:\d{2})?公演）')


def badge_days(ty):
    m = BADGE.search(ty or '')
    if not m:
        return []
    return [re.sub(r'^R\d+年\s*', '', x.strip()) for x in m.group(1).split('〜')]


def card_day(around):
    """カードの地の文から公演日（M/D）を拾う。ぴあは「2026/9/22(火・祝)」の形。"""
    ds = re.findall(r'20\d{2}/(\d{1,2})/(\d{1,2})\(', around)
    return {'%d/%d' % (int(a), int(b)) for a, b in ds}


def judge(ty, cards):
    """('soldout'|'saleended'|None, 見たカード数)。"""
    days = set(badge_days(ty))
    if not days:
        return None, 0
    mine = [(txt, cls) for txt, cls, around in cards if card_day(around) & days]
    if not mine:
        return None, 0
    if any(ALIVE.search(t) for t, _ in mine):
        return None, len(mine)          # 1つでも生きている＝触らない
    if all(SOLD.search(t) for t, _ in mine):
        return 'soldout', len(mine)
    if all(SOLD.search(t) or ENDED.search(t) for t, _ in mine):
        return 'saleended', len(mine)   # 売り切れと言い切れない＝弱いほうに倒す
    return None, len(mine)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ids', required=True)
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    ids = {int(x) for x in a.ids.split(',') if x.strip()}

    src = open('index.html', encoding='utf-8').read()
    m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
    events = json.loads(m.group(2))

    cache = {}
    marked = unmarked = 0
    for e in events:
        if e['id'] not in ids:
            continue
        myurl = (e.get('links') or {}).get('pia') or ''
        for t in e.get('tickets') or []:
            u = t.get('url') or myurl
            if 'pia.jp' not in u:
                continue                 # ぴあの枠だけ（他社は各社の道具で）
            # 🚨締切がもう過ぎている枠には印を付けない。
            #   その枠は今も画面から消えている（正しい）のに、soldout を付けると
            #   「販売終了」として**出し直してしまう**＝ノイズを増やすだけ。
            #   打ち分けが要るのは「締切が未来なのに買えない枠」＝買えるように見える枠だけ。
            if (t.get('date') or '') < TODAY and not t.get('soldout'):
                continue
            if u not in cache:
                try:
                    cache[u] = statuses(fetch(u))
                except Exception as ex:
                    cache[u] = []
                    print('   取得できなかった %s (%r)' % (u, ex))
                time.sleep(1.2)
            v, n = judge(t.get('type'), cache[u])
            if v == 'soldout' and not t.get('soldout'):
                t['soldout'] = True
                t['soldoutSince'] = TODAY
                t.pop('saleEnded', None)
                t.pop('saleEndedSince', None)
                marked += 1
                print('🔴 id=%-5s %-50s → 予定枚数終了（カード%d枚）' % (e['id'], t['type'][:50], n))
            elif v == 'saleended' and not t.get('soldout'):
                t['soldout'] = True
                t['saleEnded'] = True
                t['soldoutSince'] = TODAY
                t['saleEndedSince'] = TODAY
                marked += 1
                print('⚪ id=%-5s %-50s → 販売終了（カード%d枚）' % (e['id'], t['type'][:50], n))
            elif v is None and t.get('soldout') and n:
                t.pop('soldout', None)
                t.pop('soldoutSince', None)
                t.pop('saleEnded', None)
                t.pop('saleEndedSince', None)
                unmarked += 1
                print('🟢 id=%-5s %-50s → 買えるので印を外す' % (e['id'], t['type'][:50]))

    print('\n=== 印を付けた %d枠 / 外した %d枠 ===' % (marked, unmarked))
    if not a.apply:
        print('(--apply で書き込み)')
        return 0
    arr = json.dumps(events, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(
        src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
    print('書き込み完了')
    return 0


def _selftest():
    assert badge_days('一般発売（大阪 9/22公演）〜9/21 23:59') == ['9/22']
    assert badge_days('一般発売（東京 R9年 1/8公演）10/10 10:00発売') == ['1/8']
    assert card_day(' … 2026/9/22(火・祝) 心斎橋ＪＡＮＵＳ ( 大阪府 ) ') == {'9/22'}
    cards = [('予定枚数終了', 'is-active', ' 2026/9/22(火・祝) 心斎橋 '),
             ('抽選受付終了', 'is-before', ' 2026/9/22(火・祝) 心斎橋 ')]
    # 「抽選受付終了」は生きている言い方ではないので、全部が売切/終了なら弱いほうに倒す
    assert judge('一般発売（大阪 9/22公演）〜9/21', cards)[0] == 'saleended'
    cards2 = [('予定枚数終了', 'is-active', ' 2026/9/25(金) 渋谷 '),
              ('予定枚数終了', 'is-active', ' 2026/9/25(金) 渋谷 ')]
    assert judge('一般発売（東京 9/25公演）〜9/24', cards2)[0] == 'soldout'
    cards3 = [('予定枚数終了', 'is-active', ' 2026/9/25(金) 渋谷 '),
              ('受付中', 'is-active', ' 2026/9/25(金) 渋谷 ')]
    assert judge('一般発売（東京 9/25公演）〜9/24', cards3)[0] is None   # 1つでも生きていたら触らない
    assert judge('一般発売（東京 12/1公演）〜11/30', cards2)[0] is None  # 別の公演日は見ない
    print('selftest OK: バッジの公演日 / カードの公演日 / 全部売切だけ印 / 1つでも生きていたら触らない')


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        _selftest()
        sys.exit(0)
    sys.exit(main())
