# -*- coding: utf-8 -*-
"""検索したら結果の先頭まで自動スクロールする（ユーザー指示 2026-08-04）。

ジャンル/ステータス/地方のボタン列が縦に長く、検索しても結果が画面の外にいて
「下までスクロールしないと確認できない・一瞬ん？となる」ため。

🚨index.html は CRLF。newline='' で読み書きし、挿入するコードも \r\n で組み立てる
（孤立LFが混ざると sort_guard が誤ブロックする＝memory feedback_index_html_crlf_preserve）。
"""
import io
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'index.html')
h = io.open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'


def block(lines):
    return NL.join(lines)


# ① ヘルパー本体（showSuggest の直前に置く＝同じ init スコープ内）
HELPER = block([
    '    // 【検索したら結果まで自動スクロール】(ユーザー指示 2026-08-04)',
    '    // 検索窓の下にジャンル/ステータス/地方のボタンが縦に長く並ぶので、検索しても',
    '    // 結果が画面の外にいて「下にスクロールしないと確認できない」状態だった。',
    '    // 1文字ごとに飛ぶと読めないので、入力が止まってから動かす（デバウンス）。',
    '    let scrollTimer = null;',
    '    function scrollToResults(delay) {',
    '      clearTimeout(scrollTimer);',
    '      scrollTimer = setTimeout(() => {',
    '        const meta = document.querySelector(".result-meta");',
    '        if (!meta) return;',
    '        const top = meta.getBoundingClientRect().top + window.pageYOffset - 8;',
    '        window.scrollTo({ top: top, behavior: "smooth" });',
    '      }, delay);',
    '    }',
    '',
    '    function showSuggest(query) {',
])
old = '    function showSuggest(query) {'
assert h.count(old) == 1, 'showSuggest アンカーが%d件' % h.count(old)
h = h.replace(old, HELPER, 1)

# ② 入力時（空文字に戻したときは動かさない＝勝手に飛ばない）
old = block([
    '    searchInput.addEventListener("input", e => {',
    '      searchQuery = e.target.value.trim();',
    '      applyFilters();',
    '      showSuggest(searchQuery);',
    '    });',
])
new = block([
    '    searchInput.addEventListener("input", e => {',
    '      searchQuery = e.target.value.trim();',
    '      applyFilters();',
    '      showSuggest(searchQuery);',
    '      if (searchQuery) scrollToResults(350); else clearTimeout(scrollTimer);',
    '    });',
    '',
    '    // Enterは待たずにすぐ結果へ（サジェストは閉じる）',
    '    searchInput.addEventListener("keydown", e => {',
    '      if (e.key === "Enter") {',
    '        suggest.classList.remove("open");',
    '        if (searchQuery) scrollToResults(0);',
    '      }',
    '    });',
])
assert h.count(old) == 1, 'input ハンドラのアンカーが%d件' % h.count(old)
h = h.replace(old, new, 1)

# ③ サジェストを選んだときもすぐ結果へ
old = block([
    '          applyFilters();',
    '          suggest.classList.remove("open");',
])
new = block([
    '          applyFilters();',
    '          suggest.classList.remove("open");',
    '          scrollToResults(0);',
])
assert h.count(old) == 1, 'サジェスト選択のアンカーが%d件' % h.count(old)
h = h.replace(old, new, 1)

bak = os.path.join(ROOT, 'index.html.bak_0804_search_scroll')
shutil.copyfile(P, bak)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
raw = open(P, 'rb').read()
stray = raw.count(b'\n') - raw.count(b'\r\n')
print('patched. stray_lf=%d (0でないとsort_guardが誤ブロック) backup=%s' % (stray, os.path.basename(bak)))
