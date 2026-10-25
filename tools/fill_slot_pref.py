# -*- coding: utf-8 -*-
"""枠の括弧（…M/D公演）に県が無い枠へ、エントリの県を入れる。2026-10-26 新設。

  python tools/fill_slot_pref.py           … 数えるだけ（exit 0＝入れる枠なし／1＝ある）
  python tools/fill_slot_pref.py --apply   … 書く

## なぜ要るか（2026-10-26 抜き打ち 16678 crotchet「全椅子席（11/21公演）」・すちこ「同じ間違いがないように、ゲートをなんとかして」）
TIGET・livePocket・ZAIKO の組み立ては会場名から県を当てるので、知らない会場だと括弧に県が入らない。
あとからエントリの県を埋めても、毎朝のヒール（売り場から作り直し）で枠の名前が作り直され、県がまた消える。
＝fold_parts と同じく「ヒールのあとに --apply・push 前に gate_fields L で確かめる」形にした（648枠あった）。

## 決まり
- エントリの県が1つ（「東京」など47都道府県のどれか）の時だけ入れる。複数・全国・海外・空は触らない
- 県の欄が空の分は埋めない（配信「Zaiko Live」・会場非公開など、本当に県が無いものが多い＝同じ会場名から推測しない）
"""
import io, json, re, sys

ROOT = 'C:/Users/user/oshinavi/'
PREF47 = ['北海道', '青森', '岩手', '宮城', '秋田', '山形', '福島', '茨城', '栃木', '群馬', '埼玉', '千葉', '東京', '神奈川',
          '新潟', '富山', '石川', '福井', '山梨', '長野', '岐阜', '静岡', '愛知', '三重', '滋賀', '京都', '大阪', '兵庫', '奈良',
          '和歌山', '鳥取', '島根', '岡山', '広島', '山口', '徳島', '香川', '愛媛', '高知', '福岡', '佐賀', '長崎', '熊本', '大分',
          '宮崎', '鹿児島', '沖縄']
ANY_PLACE = PREF47 + ['全国', '海外', '韓国', '台湾', '配信']
SLOT = re.compile(r'（((?:R9年\s*)?\d{1,2}/\d{1,2}[^（）]*?(?:公演|開演|開場))）')


def missing(e):
    """(枠, 括弧のマッチ) のうち、県が入っていなくてエントリの県が1つのもの"""
    p = (e.get('prefecture') or '').strip()
    if p not in PREF47:
        return []
    out = []
    for t in e.get('tickets') or []:
        ty = t.get('type') or ''
        m = SLOT.search(ty)
        if m and not any(x in ty[m.start():m.end()] for x in ANY_PLACE):
            out.append((t, m))
    return out


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    apply = '--apply' in sys.argv
    s = io.open(ROOT + 'index.html', encoding='utf-8', newline='').read()
    mm = re.search(r'const\s+EVENTS\s*=\s*(\[)', s)
    st = mm.start(1)
    E, end = json.JSONDecoder().raw_decode(s, st)
    n, ids = 0, set()
    for e in E:
        for t, m in missing(e):
            n += 1
            ids.add(e['id'])
            if apply:
                ty = t['type']
                t['type'] = ty[:m.start()] + '（%s %s）' % (e['prefecture'].strip(), m.group(1)) + ty[m.end():]
    print(f'fill_slot_pref: 県を入れる枠 {n}（{len(ids)}件）' + (' → 書いた' if apply and n else ''))
    if apply and n:
        body = '[\n' + ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in E) + '\n]'
        s = s[:st] + body.replace('\n', '\r\n') + s[end:]
        io.open(ROOT + 'index.html', 'wb').write(s.encode('utf-8'))
    sys.exit(1 if (n and not apply) else 0)


if __name__ == '__main__':
    main()
