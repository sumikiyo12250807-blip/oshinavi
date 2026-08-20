# -*- coding: utf-8 -*-
"""新着50件(2865-2914)のお直し。
 1) 空カッコ会場4件をぴあ実ページ由来の会場名で埋める（WebFetch裏取り済）
 2) 統合3組（リクオ通し券/さやか落語会セット券/アインシュタイン15周年）
 3) NEW_ORDER から統合で消えたidを除去
"""
import re, json, sys, shutil, datetime
sys.stdout.reconfigure(encoding='utf-8')

PATH = 'index.html'
BAK = f'index.html.bak_0719_newpool_fix'
shutil.copy(PATH, BAK)
h = open(PATH, encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))
byid = {e['id']: e for e in E}

# ---- 1) 空カッコ会場（ぴあ実ページで会場名を確認済み） ----
VENUES = {
    2867: '全国ツアー（EX THEATER ROPPONGI／OSAKA MUSE ほか全13会場）',
    2869: '全国ツアー（下北沢SHELTER／LIVE SQUARE 2nd LINE）',
    2872: 'SPIRITUAL LOUNGE／Revolver',
    2885: '全国ツアー（日本青年館ホール／金沢市文化ホール／キャメリアホール／熊本城ホール シビックホール／琉球新報ホール／御園座）',
}
for i, v in VENUES.items():
    old = byid[i]['venue']
    byid[i]['venue'] = v
    # dateLabel 末尾の会場表記も揃える
    dl = byid[i].get('dateLabel') or ''
    if old in dl:
        byid[i]['dateLabel'] = dl.replace(old, v)
    print(f'[会場] id={i} {old!r} → {v!r}')

# ---- 2) 統合 ----
PIA = 'https://t.pia.jp/pia/event/event.do?eventCd='

def merge(keep_id, drop_id, new_name, keep_label, drop_label, keep_cd, drop_cd, new_date=None):
    keep, drop = byid[keep_id], byid[drop_id]
    keep['name'] = new_name
    keep['artist'] = new_name
    if new_date:
        keep['date'] = new_date
    # 両者の枠にラベルとURLを付けて1エントリに束ねる
    ts = []
    for t in keep.get('tickets', []):
        t = dict(t)
        t['type'] = re.sub(r'^(一般発売)', r'\1 ' + keep_label, t['type'])
        t['url'] = PIA + keep_cd
        ts.append(t)
    for t in drop.get('tickets', []):
        t = dict(t)
        t['type'] = re.sub(r'^(一般発売)', r'\1 ' + drop_label, t['type'])
        t['url'] = PIA + drop_cd
        ts.append(t)
    keep['tickets'] = ts
    E.remove(drop)
    print(f'[統合] id={drop_id} → id={keep_id} 「{new_name}」枠{len(ts)}')

# A) リクオ（磔磔3日間・各公演券 + 3日間通し券）
merge(2875, 2874, 'リクオ', '各公演券', '3日間通し券', '2627256', '2627257')
# B) さやかミニ落語会（各公演券 + 6回シリーズ セット券）
merge(2880, 2879, 'さやかミニ落語会 2026年度 第4回〜第6回',
      '各公演券', 'セット券（第4回〜第6回分）', '2623657', '2623659')
# C) アインシュタイン15周年ツアー（全国5会場 + 愛知 御園座）
merge(2885, 2884, 'アインシュタイン結成15周年記念ツアー',
      '（東京・石川・愛媛・熊本・沖縄）', '（愛知 御園座）',
      '2617375', '2627777', new_date='2026-11-29')

# アインシュタインは統合で公演期間が伸びる
byid[2885]['dateLabel'] = '2026年8月29日(土)〜2026年11月29日(日) 全国ツアー'

# ---- 3) 書き戻し ----
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
new_arr = '\n'.join(('  ' + ln if ln.strip() else ln) for ln in new_arr.split('\n')).lstrip()
h = h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():]

# NEW_ORDER から統合で消えた id を除去
mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', h)
order = json.loads(mo.group(2))
alive = {e['id'] for e in E}
order2 = [i for i in order if i in alive]
h = h[:mo.start()] + mo.group(1) + json.dumps(order2) + h[mo.end():]
print(f'[NEW_ORDER] {len(order)} → {len(order2)}')

open(PATH, 'w', encoding='utf-8').write(h)
print(f'=== 書き戻し完了 総{len(E)}件 (backup {BAK}) ===')
