# -*- coding: utf-8 -*-
"""index.html に「1組ずつのカードを、読み終わったところで閉じる」ハンドラを足す。

🚨2026-08-30 ユーザー指示:
  「ゴスペラーズとかTHE MODS 一つ一つの戻るボタンの▲を読み終わったところにおいて欲しい」
  ＝ pk-open（見出し）まで戻らないと閉じられないのが手間。本文の末尾にも閉じる口を置く。

🚨CRLFを壊さないこと（feedback_index_html_crlf_preserve / feedback_index_html_crcrlf_trap）:
  newline='' で読み書きし、足す行は自分で \r\n を付ける。
"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PATH = 'index.html'
ANCHOR = """    document.querySelectorAll(".pk-open").forEach(btn => {"""
MARK = 'data-pk-shut'

h = io.open(PATH, encoding='utf-8', newline='').read()

if MARK in h:
    print('もう入っているわ（何もしない）')
    sys.exit(0)

i = h.index(ANCHOR)
# .pk-open の forEach ブロックの終わりを探す
j = h.index('});', h.index('btn.setAttribute("aria-expanded", String(!open));', i)) + len('});')

ADD = [
    '',
    '    // 🚨1組ずつのカードも「読み終わったところ」で閉じられるようにする（2026-08-30 ユーザー指示',
    '    //   「ゴスペラーズとかTHE MODS 一つ一つの戻るボタンの▲を読み終わったところにおいて欲しい」）。',
    '    //   本文が長いので、閉じるのに見出しまでスクロールで戻らせない。',
    '    //   閉じたあとはその組の見出しを画面に出す（どこにいるか分からなくならないように）。',
    '    document.querySelectorAll("[data-pk-shut]").forEach(btn => {',
    '      btn.addEventListener("click", () => {',
    '        const act = btn.closest(".pk-act");',
    '        const head = act && act.querySelector(".pk-open");',
    '        const detail = act && act.querySelector(".pk-detail");',
    '        if (!head || !detail) return;',
    '        detail.hidden = true;',
    '        head.setAttribute("aria-expanded", "false");',
    '        const hd = document.querySelector("header");',
    '        const gap = (hd ? hd.getBoundingClientRect().height : 0) + 12;',
    '        const top = head.getBoundingClientRect().top + window.pageYOffset - gap;',
    '        window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });',
    '      });',
    '    });',
]
h2 = h[:j] + '\r\n'.join([''] + ADD) + h[j:]

io.open(PATH, 'w', encoding='utf-8', newline='').write(h2)

d = io.open(PATH, 'rb').read()
bare = d.count(b'\n') - d.count(b'\r\n')
crcr = d.count(b'\r\r\n')
print('JSを足したわ')
print('CRLF指紋: bareLF=%d CRCRLF=%d %s' % (bare, crcr, 'OK' if bare == 0 and crcr == 0 else '[NG]'))
sys.exit(0 if bare == 0 and crcr == 0 else 2)
