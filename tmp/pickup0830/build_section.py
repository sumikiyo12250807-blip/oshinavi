# -*- coding: utf-8 -*-
"""8/31〜9/6号のピックアップ記事セクションを組み立てる。

🚨2026-08-30 全面手直し（ユーザーがプレビューを見て指摘した4点）
  1. pk-most は「今週最多」の“小さな赤バッジ”専用クラス（赤地・黒字・11px）。
     本文の箱として <div class="pk-most"> で使っていたのが「赤いバックに黒字／小さい字」の正体。
     → 本文はすべて pk-act + pk-detail に統一（黒地 var(--bg2) に白字 var(--text)・14.5px）。
  2. <blockquote> は pk- のCSSが無い＝素の見た目になる。使わない。引用は普通の <p> で出す。
  3. 字の大きさは既存CSSのまま。新しいサイズを作らない。
  4. 「折りたたむ」は本文のいちばん下＋ id="pickupClose"（JSがこのidを見ている。
     id が無いと押しても閉じない＝開いている間は上のボタンも隠れるので閉じる手段が消える）。
     ラベルは「折りたたむ」だけ。▲ は CSS の ::after が足すので文字に書くと二重になる。
"""
import io, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')

MD = 'tmp/article_draft_0830.md'
OUT = 'tmp/pickup0830/section.html'
os.makedirs('tmp/pickup0830', exist_ok=True)

md = io.open(MD, encoding='utf-8').read()

PARA_LINES = 5          # 何文ごとに段落を割るか（8/23号と同じ見た目にする）


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


# 🚨「。」のあとは必ず改行（feedback_x_kuten_kaigyo・記事にも効く）。
#   例外は名前の中の「。」だけ＝退避してから割る。
#   引用の中に「。」が来る行があって apply_pickup の検査に引っかかっていたので、
#   目視でなくビルダー側で機械的に守らせる。
KEEP_KUTEN = ('モーニング娘。',)


def kuten_break(t):
    hold = {}
    for i, k in enumerate(KEEP_KUTEN):
        ph = '\x00%d\x00' % i
        hold[ph] = k
        t = t.replace(k, ph)
    t = re.sub(r'。(?!<br>)(?!$)', '。<br>', t)
    for ph, k in hold.items():
        t = t.replace(ph, k)
    return t


def paras(lines, indent='        '):
    """文の配列 → <br> でつないだ <p> を PARA_LINES 文ごとに分けて返す"""
    out = []
    for i in range(0, len(lines), PARA_LINES):
        chunk = lines[i:i + PARA_LINES]
        out.append(indent + '<p>' + kuten_break('<br>'.join(esc(l) for l in chunk)) + '</p>')
    return out


def is_noise(s):
    """本文に入れない行＝表・罫線・**強調だけの行・箇条書き"""
    return (not s or s.startswith('|') or s.startswith('---')
            or s.startswith('**') or s.startswith('- '))


def clean(s):
    return re.sub(r'^>\s*', '', s).replace('　', ' ').strip()


def body_lines(block):
    """本文の文だけ取り出す。引用の `> ` は剥がす（生の > が本文に出ていた）"""
    out = []
    for l in block.splitlines():
        s = l.strip()
        if is_noise(s):
            continue
        s = clean(s)
        if s:
            out.append(s)
    return out


def act_block(A, name, sale, lines, shows, search, top=False, figure=None):
    """主役1組ぶんの折りたたみカード（8/23号と同じ形）"""
    A('      <div class="pk-act%s">' % (' pk-top' if top else ''))
    A('        <button class="pk-open" type="button" aria-expanded="false">')
    A('          <span class="pk-name">%s</span>' % esc(name))
    if sale:
        A('          <span class="pk-sale">%s</span>' % esc(sale))
    A('        </button>')
    A('        <div class="pk-detail" hidden>')
    if figure:
        for f in figure:
            A(f)
    for p in paras(lines):
        A(p)
    if shows:
        A('        <a class="pk-shows" href="#" data-pk-search="%s">' % esc(search or name))
        A('          <b>発売になる公演<span class="pk-go">タップで探す →</span></b>')
        A('          ' + esc(shows))
        A('        </a>')
    # 🚨読み終わったところに ▲ を置く（2026-08-30 ユーザー指示）。
    #   見出しまでスクロールで戻らないと閉じられないのが手間だった。
    #   ▲ は CSS の .pk-close::after が足すので文字には書かない。
    A('        <button class="pk-more pk-close" type="button" data-pk-shut>%s</button>'
      % esc((name + 'を閉じる') if len(name) <= 14 else '閉じる'))
    A('        </div>')
    A('      </div>')


# ── マークダウンを節ごとに割る
parts = re.split(r'\n(?=## )', md)
head = parts[0]
title = re.search(r'^# (.+)$', head, re.M).group(1).strip()
head_lines = [l.strip() for l in head.splitlines()
              if l.strip() and not l.startswith('#') and not l.startswith('---')]
sub = head_lines[0]
lede = head_lines[1:]

sections = {}
for p in parts[1:]:
    sections[re.match(r'## (.+)', p).group(1).strip()] = p


def acts_from(block):
    """### 見出し ごとの主役を取り出す（表や締めの一文を飲み込まないようにする）"""
    out = []
    for m in re.finditer(r'### (.+?)\n(.*?)(?=\n### |\Z)', block, re.S):
        name = m.group(1).strip()
        body = m.group(2)
        sale = re.search(r'^\*\*(?!発売になる公演)(.+?)\*\*$', body, re.M)
        sale = sale.group(1).strip() if sale else ''
        text = body_lines(body)
        shows = [l.strip('- ').strip() for l in body.splitlines() if l.strip().startswith('- ')]
        out.append((name, sale, text, '／'.join(shows)))
    return out


html = []
A = html.append
A('<section class="pickup" id="pickup">')
A('  <span class="pk-label">📖 今週のピックアップ</span>')
A('  <h2 class="pk-title">%s</h2>' % esc(title.split('——')[-1].strip() if '——' in title else title))
A('  <p class="pk-sub">%s</p>' % esc(sub))
A('  <div class="pk-lede">')
for i, l in enumerate(lede):
    cls = ' class="pk-tease"' if i == len(lede) - 1 else ''
    A('    <p%s>%s</p>' % (cls, esc(l)))
A('  </div>')
A('  <button class="pk-more" id="pickupMore" type="button" aria-expanded="false" aria-controls="pickupBody">今週の主役を読む</button>')
A('  <div class="pk-body" id="pickupBody" hidden>')

# ── 今週の主役
A('      <h3 class="pk-h2">今週の主役</h3>')
for i, (name, sale, text, shows) in enumerate(acts_from(sections['今週の主役'])):
    act_block(A, name, sale, text, shows, name, top=(i == 0))

# ── 今週はほかにも（森高千里・夜の本気ダンス）＋名前タイル
oth = sections['今週はほかにも']

# 🚨表の直前の一文は「タイルの導入」であって、直前の主役の本文ではない。
#   ここで切っておかないと最後の主役（夜の本気ダンス）が表と導入文まで飲み込む。
tbl = oth.find('\n|')
note = ''
oth_acts = oth
if tbl >= 0:
    before = oth[:tbl].rstrip().splitlines()
    if before:
        note = before[-1].strip()
        oth_acts = '\n'.join(before[:-1])

A('      <h3 class="pk-h2">今週はほかにも</h3>')
for name, sale, text, shows in acts_from(oth_acts):
    act_block(A, name, sale, text, shows, name)

# 名前タイル（表）＝表の直前の一文をタイルの導入に使う（本文に混ぜない）
rows = re.findall(r'^\|\s*(\d{1,2}/\d{1,2}[^|]*)\|\s*([^|]+?)\s*\|$', oth, re.M)
rows = [(d.strip(), n.strip()) for d, n in rows if not d.startswith('---')]
if rows:
    A('      <p class="pk-others-note">%s</p>'
      % esc(note or '名前を押すと、そのアーティストのチケットを探せるわ。'))
    A('      <div class="pk-others">')
    for d, n in rows:
        key = re.split(r'[／\s（(]', n)[0][:18]
        A('        <a href="#" data-pk-search="%s"><span class="pk-o-name">%s</span><span class="pk-o-when">%s</span></a>'
          % (esc(key), esc(n), esc(d)))
    A('      </div>')

# ── もうひとつの目玉（本文の箱ではなく、主役と同じ折りたたみカードにする）
for key in list(sections):
    if not key.startswith('もうひとつの目玉'):
        continue
    blk = '\n'.join(sections[key].splitlines()[1:])
    A('      <h3 class="pk-h2">もうひとつの目玉</h3>')
    act_block(A, key.split('｜', 1)[1].strip(), '9/6(日)10:00 一般発売',
              body_lines(blk),
              'MTG名古屋四季劇場［熱田］　2027年1月・2月・3月公演', 'オペラ座の怪人')

# ── 今週の深掘り（第九）＝引用も普通の段落で出す
TAIL = md.strip().splitlines()[-1].strip()
for key in list(sections):
    if not key.startswith('今週の深掘り'):
        continue
    blk = '\n'.join(sections[key].splitlines()[1:]).replace(TAIL, '')
    fig = ['        <figure class="pk-fig pk-portrait">',
           '          <img src="img/daiku_orchestra.jpg" alt="コンサートホールのオーケストラと合唱のイメージ" loading="lazy">',
           '          <figcaption>※イメージ画像（AI生成）</figcaption>',
           '        </figure>']
    A('      <h3 class="pk-h2">今週の深掘り</h3>')
    act_block(A, key.split('｜', 1)[1].strip(), '', body_lines(blk), '', '', figure=fig)

# ── 締め＝押せるボタン付きのリンク（<p> だと「今週発売を見る →」が出ない）
A('      <a class="pk-tail" href="#" data-pk-status="urgent">%s<span class="pk-go">今週発売を見る →</span></a>' % esc(TAIL))
# 🚨id="pickupClose" が必須。▲ は CSS が足すので文字に書かない
A('      <button class="pk-more pk-close" id="pickupClose" type="button">折りたたむ</button>')
A('  </div>')
A('</section>')

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(html) + '\n')
print('書き出した:', OUT, '%.1fKB' % (os.path.getsize(OUT) / 1024))
