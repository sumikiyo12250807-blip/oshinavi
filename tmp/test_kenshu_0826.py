# -*- coding: utf-8 -*-
"""券種名の整形が「＜昼公演＞＜夜公演＞」を残すようになったか確かめる。
落としてはいけないもの（同日の別回を区別する語）と、落とすべきもの（公演日そのもの）の両方を見る。"""
import sys

sys.path.insert(0, "tools")
sys.stdout.reconfigure(encoding="utf-8")

import build_pia_entries as bpe

CASES = [
    ("一般発売＜昼公演＞", "サンパレス六甲ウィンターディナーショー２０２６北島兄弟", "残す"),
    ("一般発売＜夜公演＞", "サンパレス六甲ウィンターディナーショー２０２６北島兄弟", "残す"),
    ("一般発売＜６／２４公演＞", "だれか", "落とす"),
    ("一般発売＜１０／３０（金）公演＞", "だれか", "落とす"),
    ("一般発売【８／１３（木）第２部】", "だれか", "残す"),
    ("一般発売【学生限定LIVE】", "KAWAII LAB. MATES／KAWAII LAB. SOUTH", "残す"),
    ("一般発売〔テーブルシート販売〕", "だれか", "残す"),
    ("一般発売＜京都公演＞", "びわ湖ホール声楽アンサンブル", "残す?"),
    ("一般発売", "だれか", "そのまま"),
]

for title, name, expect in CASES:
    got = bpe.drop_labels_in_name(bpe.kenshu(title), name)
    print("%-28s → %-28s （期待: %s）" % (title, got, expect))
