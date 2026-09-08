# -*- coding: utf-8 -*-
"""直近バッチの記録をファイルに書き出す（コンソールはcp932で落ちるので使わない）"""
import json, io
d = json.load(open('.claude/state/last_batch.json', encoding='utf-8'))
b = d['batches'][-4:]
out = io.open('tmp/lastbatch_tail_0908.txt', 'w', encoding='utf-8')
out.write(json.dumps(b, ensure_ascii=False, indent=1))
out.close()
print("wrote tmp/lastbatch_tail_0908.txt  total_batches=%d" % len(d['batches']))
