# -*- coding: utf-8 -*-
"""build_ai_page.py の status_text にも「締切が書かれていない枠」の分岐を足す。
renderCard と同じルールに揃える（3面＝renderCard / SSR / ai*.html を合わせる決まり）。"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')

P = 'tools/build_ai_page.py'
h = io.open(P, encoding='utf-8', newline='').read()
orig = h

OLD = ('    if t.get("saleUntilSoldOut"):\n'
       '        return f"{emoji} 販売中（予定枚数に達し次第終了）", d\n')
NEW = ('    if t.get("saleUntilSoldOut"):\n'
       '        return f"{emoji} 販売中（予定枚数に達し次第終了）", d\n'
       '    if t.get("saleEndUnknown") and t.get("startDate") and parse(t["startDate"]) <= today:\n'
       '        # 売り場に「いつまで」が書かれていない枠。嘘の締切を作らず発売日だけ告げる。\n'
       '        # index.html renderCard と同じルール（ユーザー決定 2026-09-09）。\n'
       '        return f\'{emoji} 販売中（{t["startDate"]}発売〜・終了日は売り場に記載なし）\', t["startDate"]\n')

if OLD not in h:
    # 改行がCRLFの可能性
    OLD = OLD.replace('\n', '\r\n')
    NEW = NEW.replace('\n', '\r\n')
assert h.count(OLD) == 1, '差し込み場所が見つからない（%d件）' % h.count(OLD)
h = h.replace(OLD, NEW)

print('差分: %+d バイト' % (len(h) - len(orig)))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open(P, 'w', encoding='utf-8', newline='').write(h)
print('書き込み完了')
