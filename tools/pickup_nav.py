# -*- coding: utf-8 -*-
"""記事のページ（pickup/ の下の .html 全部）に
  ① 上の帯（OSHINAVI・チケット・イベント一覧へ）を、下に読み進めても常に上に出す
  ② 右下に「↑ 上に戻る」矢印のボタン（少し下に読み進めたら出る）
を足す（2026-11-19 すちこ「記事が増えてきたから記事のページにもトップに戻るボタン矢印を」「いつでもoshinaviに戻れるように上にバーを常に出しておいて」）。

帯が下に読み進めると消えていたわけ：html と body の両方に overflow-x: hidden があると、body が自分で巻物になり、
帯の position: sticky が効かない。html の方を visible に戻すと、body の overflow は画面全体に移り、帯が上に残る。

使い方: python tools/pickup_nav.py            # pickup/ の下の全部に足す（足してあるページは飛ばす）
        pickup_article.py・pickup_list.py も書いたあとに add_nav() を通す
"""
import glob, io, os, sys

MARK = 'oshinavi-pickup-nav'
CSS = """    /* ── %s：上の帯を常に上に・右下に「上に戻る」矢印（2026-11-19） ── */
    html { overflow-x: visible !important; }
    body { overflow-x: hidden; }
    header { position: sticky; top: 0; z-index: 100; }
    .pk-totop {
      position: fixed; right: 16px; bottom: calc(18px + env(safe-area-inset-bottom, 0px)); z-index: 200;
      width: 52px; height: 52px; border-radius: 50%%; border: 1px solid var(--accent);
      background: rgba(17,17,17,.92); color: var(--accent); font-size: 24px; font-weight: 900; line-height: 1;
      display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 1px;
      cursor: pointer; box-shadow: 0 3px 14px rgba(224,64,251,.35);
      opacity: 0; visibility: hidden; transform: translateY(10px); transition: opacity .2s, transform .2s, visibility .2s;
    }
    .pk-totop small { font-size: 9px; font-weight: 700; letter-spacing: 0; }
    .pk-totop.show { opacity: 1; visibility: visible; transform: none; }
    .pk-totop:hover, .pk-totop:focus-visible { background: var(--accent); color: #14001a; outline: none; }
""" % MARK
BTN = """<button type="button" class="pk-totop" id="pkToTop" aria-label="ページの上に戻る">↑<small>上へ</small></button>
<script>/* %s */(function(){var b=document.getElementById('pkToTop');if(!b)return;function f(){b.classList.toggle('show',(window.scrollY||document.documentElement.scrollTop)>400);}window.addEventListener('scroll',f,{passive:true});f();b.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});})();</script>
""" % MARK


def add_nav(t):
    """CSS とボタンを別々に見て、無い方だけ足す（記事は型のページの頭を写すので CSS だけ先に入っていることがある）。
    </style> の最後の1つの前に CSS、</body> の前にボタン"""
    nl = '\r\n' if '\r\n' in t else '\n'
    if MARK + '：' not in t:
        i = t.rindex('</style>')
        j = t[:i].rfind('\n') + 1
        t = t[:j] + CSS.replace('\n', nl) + t[j:]
    if 'id="pkToTop"' not in t:
        k = t.rindex('</body>')
        t = t[:k] + BTN.replace('\n', nl) + t[k:]
    return t


def main():
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    n = skip = 0
    for p in sorted(glob.glob('pickup/**/*.html', recursive=True)):
        t = io.open(p, encoding='utf-8', newline='').read()
        if '</style>' not in t or '</body>' not in t:
            print('⚠ 飛ばした（style か body が無い）', p); continue
        u = add_nav(t)
        if u == t:
            skip += 1; continue
        io.open(p, 'w', encoding='utf-8', newline='').write(u)
        n += 1
    print('足した %d / もう入っていた %d' % (n, skip))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    main()
