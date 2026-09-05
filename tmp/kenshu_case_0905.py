# -*- coding: utf-8 -*-
"""2026-09-05に見つかった券種名の化け2件が直ったかを確かめる。"""
import io, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import build_pia_entries as B

CASES = [
    # (入力タイトル, 期待する券種名)
    ("一般発売(１／１０公演) ／ 怒髪天", "一般発売"),
    ("一般発売(１／１１公演) ／ 怒髪天", "一般発売"),
    ("一般発売（帯広） ／ ＬｉＳＡ", "一般発売（帯広）"),
    ("一般発売（帯広／車椅子席） ／ ＬｉＳＡ", "一般発売（帯広/車椅子席）"),
    ("一般発売（札幌） ／ ＬｉＳＡ", "一般発売（札幌）"),
    ("一般発売（札幌／車椅子席） ／ ＬｉＳＡ", "一般発売（札幌/車椅子席）"),
    # 既存の挙動が変わっていないこと
    ("一般発売（９／２２公演） ／ ＪＵＪＵ", "一般発売"),
    ("一般発売／勝欲の秋シート ／ 巨人×中日", "一般発売【勝欲の秋シート】"),
    ("一般発売＜昼公演＞ ／ サンパレス", "一般発売【昼公演】"),
]

buf = []
ng = 0
for title, want in CASES:
    got = B.kenshu(title)
    ok = (got == want)
    if not ok:
        ng += 1
    buf.append("%s  in=%s\n     got =%s\n     want=%s" % ("OK  " if ok else "NG !!", title, got, want))
buf.append("")
buf.append("NG=%d / %d" % (ng, len(CASES)))
io.open("tmp/kenshu_case_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("NG=%d / %d" % (ng, len(CASES)))
sys.exit(1 if ng else 0)
