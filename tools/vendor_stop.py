# -*- coding: utf-8 -*-
"""売り場ごとの「見に行くのを止める」札（2026-11-13 すちこ「収集だけ止めて、載ってる分はそのままでいいよ」）。

ZAIKO・livePocket は利用規約で機械で見に行くことを禁止している＝掲載のお願い（11/13）の返事が来るまで、
売り場のページを読む道具（収集・番人・作り直し）は動かさない。載っているカードはそのまま出す（消さない・直さない）。

止める札＝ .claude/state/vendor_stop.json  {"zaiko": "理由", "livepocket": "理由"}
返事が来て OK なら、その売り場の行を消せば元どおり動く。
"""
import io
import json
import os
import sys

_P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.claude', 'state', 'vendor_stop.json')


def check(vendor):
    try:
        d = json.load(io.open(_P, encoding='utf-8'))
    except Exception:
        return
    if vendor in d:
        try:
            sys.stdout.write('STOP %s: %s（.claude/state/vendor_stop.json）\n' % (vendor, d[vendor]))
        except Exception:
            pass
        raise SystemExit(0)
