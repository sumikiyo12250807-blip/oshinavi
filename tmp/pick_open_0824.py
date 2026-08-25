# -*- coding: utf-8 -*-
"""受付中（もう買える枠）から新着の穴埋め候補を選ぶ（2026-08-24）。

発売前(rlsIn=03)の未掲載は77件しかなく23件しか投入できなかった。1バッチ100件が上限なので
受付中から埋める。

🚨受付中の一覧には**締切が載っていない**（rlsdate は空）。なので
  ①ここでは「公演日が十分先のもの」で粗く絞り、
  ②build_pia_entries で枠を取ってから「締切が4日以内」を落とす（第3便の手順）。
🚨ぴあの一覧は100ページ＝1000件が上限。音楽0101は在庫4476件に対し600件しか見えていない
  ＝**頭文字の若い側に偏る**。投入した内訳は必ず報告に書く。

ジャンル優先順＝①音楽 ②演劇・クラシック ③その他（feedback_harvest_genre_priority）
"""
import collections
import datetime
import io
import json

TODAY = datetime.date(2026, 8, 24)
NEED = 77                      # 100件バッチの残り（発売前で23件投入済み）
FILES = [('01', '音楽', 'tmp/open_01_0101_0824.json', 30),
         ('01', '音楽(抽選)', 'tmp/open_01_0201_0824.json', 10),
         ('07', 'クラシック', 'tmp/open_07_0101_0824.json', 15),
         ('02', '演劇', 'tmp/open_02_0101_0824.json', 12),
         ('02', '演劇(抽選)', 'tmp/open_02_0201_0824.json', 3),
         ('06', 'イベント', 'tmp/open_06_0101_0824.json', 4),
         ('03', 'スポーツ', 'tmp/open_03_0101_0824.json', 3)]


def perf_date(s):
    """'2026/10/11(日)' や '2026/10/11(日) ～ 2026/12/…' の**初日**を返す。"""
    try:
        head = s.split('～')[0].split('・')[0].strip()
        y, m, d = head.split('(')[0].strip().split('/')
        return datetime.date(int(y), int(m), int(d))
    except Exception:
        return None


pick, merge, skip = [], [], []
for lg, name, path, quota in FILES:
    try:
        d = json.load(io.open(path, encoding='utf-8'))
    except IOError:
        print('!! %s が無い' % path)
        continue
    rows = []
    for it in d['new']:
        it['lg'] = lg
        it['_src'] = name
        pd = perf_date(it.get('perfdate') or '')
        it['_pdays'] = (pd - TODAY).days if pd else None
        if it.get('name_in_db'):
            merge.append(it)
        elif it['_pdays'] is None or it['_pdays'] < 30:
            # 公演が1か月以内＝前売りが終わりかけ。カウントダウンにならないので今日は拾わない
            skip.append(it)
        else:
            rows.append(it)
    # 公演が遠い順＝前売り期間が長く残っているもの優先
    rows.sort(key=lambda x: -x['_pdays'])
    pick += rows[:quota]
    print('%-12s 未掲載%4d → 候補%4d（同名既存%d・近すぎ/不明%d）→ 採用%d' % (
        name, len(d['new']), len(rows),
        sum(1 for x in d['new'] if x.get('name_in_db')),
        sum(1 for x in d['new'] if not x.get('name_in_db') and (perf_date(x.get('perfdate') or '') is None or (perf_date(x.get('perfdate') or '') - TODAY).days < 30)),
        min(quota, len(rows))))

pick = pick[:NEED]
print('\n選定 %d件  内訳 %s' % (len(pick), dict(collections.Counter(x['_src'] for x in pick))))
json.dump(pick, io.open('tmp/pick_open_0824.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
o = io.open('tmp/pick_open_0824.txt', 'w', encoding='utf-8')
for x in pick:
    o.write('%-12s 公演%s(あと%d日) | %s | %s\n' % (x['_src'], x['perfdate'][:10], x['_pdays'], x['artist'], x['url']))
o.close()
print('→ tmp/pick_open_0824.json')
