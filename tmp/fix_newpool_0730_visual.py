# 目視で見つかった新着プールの修正（バイト単位・CRLF維持・該当エントリ以外は1バイトも触らない）
#   ①id3516 諏訪湖祭湖上花火大会：会場名の半角カナ「Cｹﾞｰﾄ」→全角「Cゲート」
#     （楽天由来。norm_fw は全角ラテン→半角しかしないので半角カナは素通りしていた）
#   ②id3478 Jamys Album release LIVE：_genre fes→jpop
#     （BOLO静岡＝屋内ライブハウス。fesは「複数組＋屋外」＝feedback_fes_definition）
# 使い方: python tmp/fix_newpool_0730_visual.py        （差分表示のみ）
#         python tmp/fix_newpool_0730_visual.py --apply
import io, os, re, sys

SRC = os.path.join(os.path.dirname(__file__), '..', 'index.html')
APPLY = '--apply' in sys.argv

# (id, 旧バイト列, 新バイト列, 期待置換回数)
TARGETS = [
    (3516, 'Cｹﾞｰﾄ観覧席', 'Cゲート観覧席', 2),   # venue と dateLabel の2箇所
    (3478, '"_genre": "fes"', '"_genre": "jpop"', 1),
]

raw = open(SRC, 'rb').read()
before_crlf = raw.count(b'\r\n')
before_len = len(raw)


def entry_span(buf, eid):
    """id=eid のエントリ本文の範囲を返す（次エントリの "id": が始まる直前まで）"""
    m = re.search(('"id": %d,' % eid).encode('utf-8'), buf)
    assert m, 'id%d が見つからない' % eid
    nxt = re.search(rb'\n\s*"id": \d+,', buf[m.end():])
    end = m.end() + (nxt.start() if nxt else 0)
    return m.start(), end


out = raw
for eid, old, new, expect in TARGETS:
    s, e = entry_span(out, eid)
    block = out[s:e]
    ob, nb = old.encode('utf-8'), new.encode('utf-8')
    n = block.count(ob)
    print('id%d: 「%s」→「%s」 該当 %d 箇所（期待%d）' % (eid, old, new, n, expect))
    assert n == expect, 'id%d の該当数が期待と違う（%d != %d）＝中止' % (eid, n, expect)
    out = out[:s] + block.replace(ob, nb) + out[e:]

# 差分の安全確認：CRLF数は不変・長さ変化は置換分だけ
after_crlf = out.count(b'\r\n')
print('CRLF: %d → %d （不変であるべき）' % (before_crlf, after_crlf))
print('バイト長: %d → %d （差 %+d）' % (before_len, len(out), len(out) - before_len))
assert before_crlf == after_crlf, 'CRLFが変わった＝中止'
assert out.count(b'\n') == raw.count(b'\n'), '行数が変わった＝中止'

if APPLY:
    open(SRC, 'wb').write(out)
    print('=== 適用した ===')
else:
    print('=== 未適用（--apply で適用）===')
