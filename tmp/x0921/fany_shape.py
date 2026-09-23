# -*- coding: utf-8 -*-
"""FANYの登録済みエントリの枠を、発売前／販売中／終了・売切に分け、販売中は締切までの日数・公演までの日数で数える（読むだけ・9/21夜）。
ユーザー「fanyはすでに売ってて、しかももうすぐ終わるのばっかりなんだね　まだ売ってないのはあんまりないのかな？」への答え。"""
import collections, datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date(2026, 9, 21)
h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
fan = [e for e in ev if (e.get('links') or {}).get('fany')]
state = collections.Counter()
left = collections.Counter()
show_left = collections.Counter()
ent_has_pre = 0
kinds = collections.Counter()


def d(s):
    try:
        return datetime.date.fromisoformat(s)
    except Exception:
        return None


def bucket(n):
    return '0〜3日' if n <= 3 else '4〜7日' if n <= 7 else '8〜14日' if n <= 14 else '15〜30日' if n <= 30 else '31日〜'


for e in fan:
    pre = False
    sd_show = None
    m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', e.get('dateLabel') or '')
    if m:
        sd_show = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        kinds['先行' if '先行' in ty else '一般' if '一般' in ty else 'その他'] += 1
        st, en = d(t.get('startDate')), d(t.get('date'))
        if t.get('soldout') or t.get('saleEnded') or t.get('presaleEnded'):
            state['終了・売切の印'] += 1
        elif st and st > TODAY:
            state['発売前'] += 1
            pre = True
        elif en and en < TODAY:
            state['締切が過ぎた'] += 1
        else:
            state['販売中'] += 1
            if en:
                left[bucket((en - TODAY).days)] += 1
            if sd_show:
                show_left[bucket((sd_show - TODAY).days)] += 1
    ent_has_pre += pre
print('FANYのエントリ %d件 ／ 枠 %d' % (len(fan), sum(state.values())))
for k, v in state.most_common():
    print('  %s %d' % (k, v))
print('発売前の枠を持つエントリ %d件' % ent_has_pre)
print('販売中の枠＝締切まで:', dict(left))
print('販売中の枠＝公演まで:', dict(show_left))
print('券種:', dict(kinds))
