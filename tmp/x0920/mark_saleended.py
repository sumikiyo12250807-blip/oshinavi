# -*- coding: utf-8 -*-
"""「カードは出るのに買える枠0」のうち、ぴあの実ページが**はっきり「販売終了」と書いている**
ものに `saleEnded` の印を付ける（2026-09-20 昼）。

🚨消さない。公演はこれからなので「販売終了」のバッジ（点線）で出し続ける
   （[[feedback_saleended_vs_soldout]]／[[feedback_soldout_keep_visible]]／[[feedback_oshinavi_concept]]）。

🚨**「抽選受付終了」だけのものは付けない**＝先行抽選が終わっただけで、
   このあと一般発売が来ることがある。そこに「販売終了」と出したら**嘘になる**
   （Vaundy・椎名林檎・T.M.Revolution など22件。[[feedback_deadline_extended_after_register]]）。
   → 毎朝の mark_soldout で見続ける。

対象＝mark_soldout が実ページから「販売終了／販売を終了致しました」と読んだ4件だけ。
使い方: python tmp/x0920/mark_saleended.py [--apply]
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv
NL = '\r\n'

# id: ぴあの実ページで読めた文言（tmp/x0920/ms2_u.txt）
TARGET = {
    3418: '販売終了',
    4121: '販売終了',
    5053: '抽選受付終了／販売終了',
    5669: '販売を終了致しました',
}

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

n = 0
for eid, note in TARGET.items():
    e = by.get(eid)
    if not e:
        print('id%s 無し' % eid)
        continue
    print('== id%d %s（公演 %s）… ぴあの文言「%s」' % (eid, (e.get('artist') or '')[:36], e.get('date'), note))
    for t in (e.get('tickets') or []):
        if t.get('soldout') or t.get('saleEnded'):
            continue
        # 🚨「M/D HH:MM発売」形＝発売日と締切日が同じ**隠れ枠**は触らない。
        #   本当の締切がまだ入っていないだけかもしれず、「販売終了」と書いたら嘘になる。
        #   （id5053 の一般発売は昨日9/19 10:00発売／id5669 は9/2発売で、どちらもこの形）
        if re.search(r'\d{1,2}/\d{1,2}\s*\d{1,2}:\d{2}発売\s*$', (t.get('type') or '')):
            print('   ⏭ 隠れ枠（発売日=締切日）＝触らない: %s' % t.get('type'))
            continue
        if 'pia.jp' not in (t.get('url') or '') and (e.get('links') or {}).get('pia') is None:
            print('   ⏭ ぴあの枠でない＝触らない: %s' % t.get('type'))
            continue
        n += 1
        print('   ＋販売終了の印: %s' % t.get('type'))
        if APPLY:
            t['soldout'] = True
            t['saleEnded'] = True
            t['saleEndedSince'] = TODAY

print('\n印を付ける %d枠' % n)
if not APPLY:
    print('(--apply で書き込み)')
    sys.exit(0)

io.open('index.html.bak_0920_saleended', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('書き込み完了（バックアップ index.html.bak_0920_saleended）')
