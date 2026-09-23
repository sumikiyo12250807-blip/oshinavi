# -*- coding: utf-8 -*-
"""「先行終了」の印を付ける（2026-09-20 夜・ユーザー指示「先行終了のバッジ出してみて」）。

いきさつ＝`check_zero_badge` が出した「カードは出るのに買える枠0」を mark_soldout にかけたら、
22件が **ぴあの実ページで「抽選受付終了」としか書いていない**ものだった。
  ・「販売終了」と書くのは嘘＝先行抽選が終わっただけで、**一般発売はこれから来ることがある**
    （Vaundy・椎名林檎・T.M.Revolution・Suchmos・ウルフルズ など）
  ・かといって何も出さないと、カードに1枚もバッジが無く「もう終わったのか」も分からない
→ 3つ目のバッジ **「先行終了」** を作った（点線＋薄い青）。

印の付け方＝`soldout: true` ＋ `presaleEnded: true` ＋ `presaleEndedSince`。
🚨`soldout` を土台にするのは **並び順ロジックに1文字も触らないため**
   （[[feedback_saleended_vs_soldout]]＝`EVENTS.sort`/`ticketSortKey` を直すと sort_guard が止める）。

付ける条件（全部満たす枠だけ）:
  ① 券種名が先行型（先行／抽選／プレリザーブ／プリセール／最速／オフィシャル／会員／プレオーダー）
  ② その枠の締切が**過去**
  ③ エントリの公演日が**未来**（終わった公演には付けない）
  ④ まだ soldout も saleEnded も付いていない
🚨②の判定に使う「公演日」は券種名の中の公演日ではなくエントリの date（カードが出ている間だけ意味がある）。
🚨券種名の中の公演日が過去のものは付けない（id1554 の「福岡 9/12公演」など）。

使い方: python tmp/x0920/mark_presale_ended.py [--apply]
"""
import datetime, io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
APPLY = '--apply' in sys.argv
NL = '\r\n'

# ぴあの実ページで「抽選受付終了」とだけ書いてあった22件（tmp/x0920/ms2_u.txt）
IDS = [1554, 3510, 4059, 4077, 4079, 4089, 4094, 4106, 4117, 4373, 4386,
       4401, 4412, 4418, 4420, 4809, 4823, 4951, 5719, 7037, 7113, 7485]
PRE = re.compile(r'先行|抽選|プレリザーブ|プリセール|最速|オフィシャル|会員|プレオーダー')
SHOWDATE = re.compile(r'[（(][^（()）]*?(\d{1,2})/(\d{1,2})[^（()）]*?公演[）)]')

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

marked, skipped = [], []
for i in IDS:
    e = by.get(i)
    if not e:
        skipped.append((i, '', 'エントリが無い'))
        continue
    if (e.get('date') or '') < TODAY:
        skipped.append((i, e.get('artist'), '公演が終わっている'))
        continue
    for t in (e.get('tickets') or []):
        ty = t.get('type') or ''
        if t.get('soldout') or t.get('saleEnded'):
            skipped.append((i, e.get('artist'), '既に印あり: ' + ty[:34]))
            continue
        if not PRE.search(ty):
            skipped.append((i, e.get('artist'), '先行型でない: ' + ty[:34]))
            continue
        if (t.get('date') or '9999') >= TODAY:
            skipped.append((i, e.get('artist'), 'まだ受付中: ' + ty[:34]))
            continue
        # 券種名の中の公演日が全部過去なら、その枠は終わった公演のもの＝触らない
        ds = [d for d in SHOWDATE.findall(ty)]
        if ds:
            y = int(TODAY[:4])
            iso = ['%04d-%02d-%02d' % (y, int(a), int(b)) for a, b in ds]
            if all(x < TODAY for x in iso) and 'R9' not in ty and 'R10' not in ty:
                skipped.append((i, e.get('artist'), '公演が過去の枠: ' + ty[:34]))
                continue
        marked.append((i, e.get('artist'), ty))
        if APPLY:
            t['soldout'] = True
            t['presaleEnded'] = True
            t['presaleEndedSince'] = TODAY

print('=== 「先行終了」の印（today=%s）===' % TODAY)
print('付ける %d枠 / 付けない %d枠' % (len(marked), len(skipped)))
for i, n, ty in marked:
    print('  ＋ id%s %s ｜ %s' % (i, (n or '')[:22], ty))
for i, n, why in skipped:
    print('  − id%s %s' % (i, why))

if not APPLY:
    print('\n(--apply で書き込み)')
    sys.exit(0)

io.open('index.html.bak_0920_presaleended', 'w', encoding='utf-8', newline='').write(h)
io.open('index.html', 'w', encoding='utf-8', newline='').write(
    h[:m.start()] + m.group(1)
    + json.dumps(EVENTS, ensure_ascii=False, indent=2).replace('\n', NL)
    + m.group(3) + h[m.end():])
raw = io.open('index.html', 'rb').read()
assert raw.count(b'\r\r\n') == 0 and not re.findall(rb'(?<!\r)\n', raw), '改行が壊れた'
print('\n書き込み完了（バックアップ index.html.bak_0920_presaleended）')
