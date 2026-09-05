# -*- coding: utf-8 -*-
"""build の重複判定を「アーティスト名の部分一致」から「eid（e+公演ID）」へ直す恒久対策。"""
import io

P = 'tools/eplus_harvest.py'
s = io.open(P, encoding='utf-8').read()

OLD = """        # アーティストでグループ化（同一ツアーの別base-eidを束ねる）
        groups = {}
        for c in cands:
            ak = artist_key(c['title'])
            if nz(ak) and nz(ak) in dbblob:
                continue  # DB重複（ローマ字/カナ含む）
            groups.setdefault(ak, []).append(c)
        print(f'候補 {len(cands)}件 → 新規アーティスト {len(groups)}組')
"""

NEW = """        # 🚨重複判定は eid（e+の公演ID）で行う。アーティスト名の部分一致で落とすと
        # 「同じ人の別公演」も「名前が他エントリに含まれるだけの別物」も丸ごと消える
        # （2026-09-05に36候補→2件まで落ちた＝サーカス/wacci/シンギュラリティ等）。
        # ぴあ側は2026-08-17に同じ理由でeventCd判定へ直してある。旧挙動は --name-dedup。
        dbids = set(re.findall(r'/sf/detail/(\d+)', hh))
        name_dedup = '--name-dedup' in sys.argv
        groups, skipped_id, warn_name = {}, [], []
        for c in cands:
            if c['eid'] in dbids:
                skipped_id.append(c)
                continue  # DB重複（同じe+公演IDが既に載っている）
            ak = artist_key(c['title'])
            if nz(ak) and nz(ak) in dbblob:
                if name_dedup:
                    continue
                warn_name.append(c)
            groups.setdefault(ak, []).append(c)
        nnew = sum(len(v) for v in groups.values())
        print(f'候補 {len(cands)}件 → 登録済みeid {len(skipped_id)}件を除外 → 新規 {nnew}件 / {len(groups)}組')
        if warn_name:
            print(f'  ℹ️ 名前がDBにある{len(warn_name)}件も残した（同名別公演の可能性・投入前に突合）')
"""

assert OLD in s, 'PATCH TARGET NOT FOUND'
s = s.replace(OLD, NEW, 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(s)
print('PATCHED')
