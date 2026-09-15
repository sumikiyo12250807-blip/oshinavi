# -*- coding: utf-8 -*-
"""7618 鈴木雅之を「長野1公演だけ」から「これからの14公演のツアー1件」に広げる（2026-09-16 朝）。
根拠＝別エージェントが公式（sonymusic のライブデータ）と ぴあ b2665442 を突き合わせた結果＝38公演で一致・
これからの公演は 9/22〜11/22 の14公演（scratchpad/pia_rows.txt がぴあの生HTMLからの抜き出し）。
  ・買える枠＝福岡 10/3・10/4（販売期間中 〜9/17 23:59・2544962）
  ・予定枚数終了＝東京9/22（「一般発売.」）・栃木・茨城・京都・群馬・高知・香川・愛知・府中・よこすか（一般／立ち見）・石垣 → soldout の印付きで足す（消さない決まり）
  ・販売終了だけ＝東京9/22（「一般発売」）・長野9/27 ×2 → 足さない（9/11 ユーザー決定＝販売終了の印を付けて回らない）。
    長野のもとの枠はそのまま残し、飛び先 2545048 だけ焼き込む
使い方: python tmp/grow_7618_0916.py [--apply]
"""
import io
import json
import re
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
ID = 7618
TODAY = '2026-09-16'
U = 'https://t.pia.jp/pia/event/event.do?eventCd=%s'


def events(text):
    return json.loads(re.search(r'  const EVENTS = (\[.*?\]);', text, re.S).group(1))


SOLD = [  # (券種名, 県, 公演日, eventCd)
    ('一般発売', '東京', '2026-09-22', '2548803'),
    ('一般発売', '栃木', '2026-10-10', '2600822'),
    ('一般発売', '茨城', '2026-10-11', '2600823'),
    ('一般発売', '京都', '2026-10-16', '2547006'),
    ('一般発売', '群馬', '2026-10-18', '2600824'),
    ('一般発売', '高知', '2026-10-22', '2548238'),
    ('一般発売', '香川', '2026-10-24', '2548238'),
    ('一般発売', '愛知', '2026-10-28', '2548647'),
    ('一般発売', '東京', '2026-10-31', '2547433'),
    ('一般発売', '神奈川', '2026-11-07', '2548506'),
    ('立ち見販売', '神奈川', '2026-11-07', '2548506'),
    ('一般発売', '沖縄', '2026-11-22', '2619650'),
]


def md(d):
    return '%d/%d' % (int(d[5:7]), int(d[8:10]))


with open(P, encoding='utf-8', newline='') as f:
    text = f.read()
ev = events(text)
old = next(e for e in ev if e['id'] == ID)
assert [t['type'] for t in old['tickets']] == ['一般発売（長野 9/27公演）〜9/15 23:59'], old['tickets']

tickets = []
for t in old['tickets']:
    t2 = dict(t)
    t2.setdefault('url', U % '2545048')
    tickets.append(t2)
for d in ('2026-10-03', '2026-10-04'):
    tickets.append({'type': '一般発売（福岡 %s公演）〜9/17 23:59' % md(d), 'date': '2026-09-17', 'url': U % '2544962'})
for name, pf, d, cd in SOLD:
    tickets.append({'type': '%s（%s %s公演）' % (name, pf, md(d)), 'date': d, 'url': U % cd,
                    'soldout': True, 'soldoutSince': TODAY})
tickets.sort(key=lambda t: t['date'])

venues = ['東京国際フォーラム ホールA', 'ホクト文化ホール 大ホール', '福岡サンパレス', '宇都宮市文化会館 大ホール',
          '水戸市民会館 グロービスホール', 'ロームシアター京都 メインホール', '高崎芸術劇場 大劇場',
          '新来島高知重工ホール オレンジホール', 'レクザムホール 大ホール', '愛知県芸術劇場 大ホール',
          '府中の森芸術劇場 どりーむホール', 'よこすか芸術劇場', '石垣市民会館']
new_e = dict(old)
new_e.update({
    'date': '2026-11-22',
    'dateLabel': '2026年9月22日(火)〜2026年11月22日(日) 全国ツアー',
    'venue': '全国ツアー（%s）' % '／'.join(venues),
    'prefecture': '全国',
    'tickets': tickets,
    'verifiedAt': TODAY,
})
keys = list(old.keys())  # 項目の並びはもとのまま
new_e = {k: new_e[k] for k in keys}
block = ['  ' + ln for ln in json.dumps(new_e, ensure_ascii=False, indent=2).split('\n')]
block[-1] += ','

lines = text.split('\r\n')
out, i, hit = [], 0, 0
while i < len(lines):
    if lines[i] == '  {' and i + 1 < len(lines) and lines[i + 1] == '    "id": %d,' % ID:
        j = i
        while not lines[j].startswith('  }'):
            j += 1
        assert lines[j] == '  },'
        out += block
        hit += 1
        i = j + 1
        continue
    out.append(lines[i])
    i += 1
assert hit == 1
new = '\r\n'.join(out)

ev2 = events(new)
assert len(ev2) == len(ev)
b = {e['id']: json.dumps(e, ensure_ascii=False, sort_keys=True) for e in ev if e['id'] != ID}
a = {e['id']: json.dumps(e, ensure_ascii=False, sort_keys=True) for e in ev2 if e['id'] != ID}
assert a == b, 'ほかのエントリが変わった'
assert '\n' not in new.replace('\r\n', ''), '素のLFが混ざった'
got = next(e for e in ev2 if e['id'] == ID)
print('7618 枠 %d → %d（買える2・売り切れの印%d・長野のもとの枠1）' % (len(old['tickets']), len(got['tickets']), len(SOLD)))
for t in got['tickets']:
    print('  ', t['date'], t['type'], '売切' if t.get('soldout') else '', t['url'][-7:])
print('会期', got['dateLabel'], '／県', got['prefecture'])
if '--apply' in sys.argv:
    shutil.copyfile(P, 'index.html.bak_0916_grow7618')
    with open(P, 'w', encoding='utf-8', newline='') as f:
        f.write(new)
    print('書き込んだ（予備 index.html.bak_0916_grow7618）')
else:
    print('（調べるだけ。--apply で書き込み）')
