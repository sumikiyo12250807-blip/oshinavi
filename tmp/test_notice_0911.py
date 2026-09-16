# -*- coding: utf-8 -*-
"""build_pia_entries.find_notice_presales を、朝に保存したぴあのページで試す（ぴあは叩かない）。"""
import io, sys
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import build_pia_entries as B
for f in ['tmp/probe_b2670908.html', 'tmp/probe_b2670967.html', 'tmp/probe_tokubetsu_2634819.html']:
    h = io.open(f, encoding='utf-8').read()
    print(f, B.find_notice_presales(h))
