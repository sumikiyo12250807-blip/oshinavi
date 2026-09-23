# -*- coding: utf-8 -*-
"""index.html の EVENTS 配列を「1件1行」に詰めて書く（中身は1文字も変えない）。

  python tools/compact_events.py             # 下見（今の大きさ→詰めた後の大きさ）
  python tools/compact_events.py --apply     # 書き込む
  python tools/compact_events.py --selftest

## なぜ（2026-09-23 ユーザー実測「1秒か2秒くらい画面が暗くなる」→ ユーザー「Bだけやっといて」）

index.html 23.62MB のうち EVENTS が 17.94MB。その約4.4MBは indent=2 の空白と改行だった。
詰めても画面に出るもの・並び・中身は変わらない（JSONとして同じ値に読み戻せることを毎回確かめる）。

## 書き方＝**1件1行**
```
  const EVENTS = [
{"id":1,...},
{"id":2,...}
];
```
1行にまとめてもサイズはほぼ同じ。1件1行なら git の差分が1件ずつ見えるので事故に気づける。

## 🚨 いつ回すか＝**push の直前**
他の道具（ヒール・投入・振り分け）は indent=2 で書き戻すので、走ると元の形に戻る。
push の直前に回せば、公開される index.html は必ず詰めた形になる。
⚠️EVENTSを「行」で読む道具は tools/delete_entries.py だけだった（2026-09-24 に JSON で読むよう直した）。
   新しい道具を作る時は EVENTS を**行で数えない**＝ `EVENTS_RE` か `load()` で読む。

## 安全弁（1つでも外れたら書かない）
1. 詰めた後の EVENTS を json で読み戻し、元と**完全に同じ値**か
2. 他の道具が使っている正規表現 `(  const EVENTS = )(\\[.*?\\])(;)`（最短一致）で
   詰めた後のファイルから取り出しても、同じ値が出るか（文字列の中に "];" があると途中で切れる）
3. EVENTS の外側（CSS・JS・SSR）が1バイトも変わっていないか
4. CRLF指紋＝LFだけの改行が0・CRCRLFが0
"""
import argparse
import io
import json
import re
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

HEAD = '  const EVENTS = '
# 他の道具（31本）が使っている取り出し方と同じ＝詰めた後もこれで読めることを確かめる
EVENTS_RE = re.compile(r'(  const EVENTS = )(\[.*?\])(;)', re.S)


def locate(text):
    """(配列の開始位置, 終了位置の次, 値) を返す。最短一致に頼らず JSON として最後まで読む。"""
    i = text.find(HEAD)
    if i < 0:
        raise RuntimeError('const EVENTS が見つからない')
    s = i + len(HEAD)
    val, end = json.JSONDecoder().raw_decode(text, s)
    if text[end:end + 1] != ';':
        raise RuntimeError('EVENTS の直後が ; でない')
    return s, end, val


def load(text):
    return locate(text)[2]


def is_compact(text):
    s, _, _ = locate(text)
    return text[s:s + 3] == '[\r\n' and text[s + 3:s + 4] == '{' or text[s:s + 2] == '[\n' and text[s + 2:s + 3] == '{'


def dump(events, compact, nl='\r\n'):
    """compact=True＝1件1行／False＝従来の indent=2。改行は nl（index.html は CRLF）。"""
    if compact:
        body = (',' + nl).join(json.dumps(e, ensure_ascii=False, separators=(',', ':')) for e in events)
        return '[' + nl + body + nl + ']' if events else '[]'
    return json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)


def compact_text(text):
    s, end, val = locate(text)
    nl = '\r\n' if '\r\n' in text[:s] else '\n'
    new = text[:s] + dump(val, True, nl) + text[end:]
    check(text, new, val)
    return new


def check(old, new, val):
    s0, e0, _ = locate(old)
    s1, e1, v1 = locate(new)
    if v1 != val:
        raise RuntimeError('安全弁1: 詰めた後の EVENTS が元と違う')
    m = EVENTS_RE.search(new)
    try:
        same = bool(m) and json.loads(m.group(2)) == val
    except ValueError:
        same = False
    if not same:
        raise RuntimeError('安全弁2: 最短一致の取り出しで同じ値にならない（文字列の中に "];" がある）')
    if old[:s0] != new[:s1] or old[e0:] != new[e1:]:
        raise RuntimeError('安全弁3: EVENTS の外側が変わった')
    if '\r\n' in old:
        bare = len(re.findall(r'(?<!\r)\n', new))
        crcr = new.count('\r\r\n')
        if bare or crcr:
            raise RuntimeError('安全弁4: CRLF指紋 bareLF=%d CRCRLF=%d' % (bare, crcr))


def _selftest():
    ev = [{'id': 1, 'name': 'A「x」', 'tickets': [{'type': '一般（大阪 10/1公演）〜9/30', 'date': '2026-09-30'}]},
          {'id': 2, 'name': 'B', 'tickets': []}]
    head = '<script>\r\n  const X = 1;\r\n'
    tail = ';\r\n\r\n  // tail ];\r\n</script>\r\n'
    old = head + HEAD + dump(ev, False) + tail
    new = compact_text(old)
    assert load(new) == ev
    assert is_compact(new) and not is_compact(old)
    assert new.startswith(head) and new.endswith(tail)
    assert '\n{"id":1,' in new and '},\r\n{"id":2,' in new, new
    assert compact_text(new) == new                       # 2回目は何も変わらない
    print('OK ① 詰めても同じ値・外側は1バイトも変わらない・2回目は同じ')
    # 文字列に "];" があると最短一致で切れる → 書かずに止まる
    bad = [{'id': 1, 'name': 'x];y'}]
    try:
        compact_text(head + HEAD + dump(bad, False) + tail)
        raise AssertionError('止まるべき')
    except RuntimeError as ex:
        assert '安全弁2' in str(ex), ex
    print('OK ② 文字列に "];" がある時は止まる')
    # LF のファイルは LF のまま
    lf = old.replace('\r\n', '\n')
    assert '\r' not in compact_text(lf)
    print('OK ③ LF のファイルは LF で書く')
    # 実物で読み戻しだけ確かめる（書かない）
    try:
        h = io.open('index.html', encoding='utf-8', newline='').read()
    except FileNotFoundError:
        h = None
    if h:
        n = compact_text(h)
        print('OK ④ 実物 index.html：%d件・%.2fMB → %.2fMB（書いていない）'
              % (len(load(h)), len(h.encode('utf-8')) / 1e6, len(n.encode('utf-8')) / 1e6))
    print('selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--file', default='index.html')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    h = io.open(a.file, encoding='utf-8', newline='').read()
    n = compact_text(h)
    b0, b1 = len(h.encode('utf-8')), len(n.encode('utf-8'))
    print('%s：%d件  %.2fMB → %.2fMB（-%.2fMB）%s'
          % (a.file, len(load(h)), b0 / 1e6, b1 / 1e6, (b0 - b1) / 1e6,
             '' if a.apply else '＝下見（--apply で書く）'))
    if a.apply and n != h:
        io.open(a.file, 'w', encoding='utf-8', newline='').write(n)
        print('書いた')


if __name__ == '__main__':
    main()
