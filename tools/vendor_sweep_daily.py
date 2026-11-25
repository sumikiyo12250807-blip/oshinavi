# -*- coding: utf-8 -*-
"""登録済みの TIGET・FANY を毎日見直す1本（2026-11-23 新設）。

  python tools/vendor_sweep_daily.py          … TIGET 全件の番人 → heal_tiget --apply（鍵の中）→ 番人 → FANY 売り切れ --apply
  python tools/vendor_sweep_daily.py --skip-fany

## なぜ要るか（tmp/x1123/spot/rootcause.md A）
11/23 の抜き打ち30件で 🔴6件のうち4件が TIGET・FANY の登録済みカード：
  20204 2Cheat7・22817 ルミネ（FANY「予定数終了」に印なし）／49411 DEMICK（TIGET 受付中なのに売り切れの印）／
  37549 DJダイノジ（TIGET の開催日が 11/13 に前へずれて終わったのに、カードは 12/5 で買える形）。
手順書（.claude/skills/day/SKILL.md）には「毎朝 gate_tiget_slots 全件 → heal_tiget」「fany_mark_soldout」と書いてあるのに、
毎朝の鎖（tmp/x11NN/morning_local.py・morning_pia.py）は前の日の写しで、どちらも入っていなかった。
FANY の売り切れ点検は 11/5 から1度も回っていなかった（tmp/fany_soldout_report.txt の日付）。
→ 1本にまとめ、終わったら .claude/state/vendor_sweep_YYYYMMDD.txt に印＝shift_guard.ps1 の C が16時を過ぎて印が無ければ止める。

TIGET・FANY だけを叩く（ぴあ・e+ は叩かない）＝ぴあ・e+ の道具と同時に回してよい。重い道具は同時2本まで。
heal_tiget は鍵を取らないので、ここで tmp/x1112/index.lock を取って呼ぶ。fany_mark_soldout は自分で同じ鍵を取る（入れ子にしない）。
"""
import argparse, datetime, io, os, re, subprocess, sys, time
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(R)
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')
LOG = os.path.join(R, 'tmp', 'vendor_sweep_daily.txt')
LOCK = os.path.join(R, 'tmp', 'x1112', 'index.lock')


def run(out, args):
    p = subprocess.run([sys.executable] + args, env=ENV, capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('$ %s\nexit %d\n%s%s\n' % (' '.join(args), p.returncode, p.stdout[-2000:], p.stderr[-1500:]))
    out.flush()
    return p.returncode


def ids_in(path):
    t = io.open(path, encoding='utf-8').read()
    return sorted({int(x) for x in re.findall(r'id=(\d+)', t)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--skip-fany', action='store_true')
    a = ap.parse_args()
    today = datetime.date.today().isoformat()
    out = io.open(LOG, 'w', encoding='utf-8')
    out.write('=== vendor_sweep_daily %s ===\n' % today)
    run(out, ['tools/gate_tiget_slots.py', '--sleep', '0.6'])
    io.open(os.path.join(R, 'tmp', 'gate_tiget_report_full.txt'), 'w', encoding='utf-8').write(
        io.open(os.path.join(R, 'tmp', 'gate_tiget_report.txt'), encoding='utf-8').read())
    bad = ids_in(os.path.join(R, 'tmp', 'gate_tiget_report.txt'))
    out.write('TIGET 番人で鳴った %d件\n' % len(bad))
    if bad:
        fd = None
        for _ in range(1200):
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'vendor_sweep_daily'); os.close(fd); break
            except FileExistsError:
                time.sleep(3)
        if fd is None:
            out.write('鍵が取れなかった＝heal_tiget は回していない\n')
        else:
            try:
                run(out, ['tools/heal_tiget.py', '--ids', ','.join(map(str, bad)), '--apply'])
            finally:
                os.remove(LOCK)
            out.write(io.open(os.path.join(R, 'tmp', 'heal_tiget_report.txt'), encoding='utf-8').read()[-4000:] + '\n')
            run(out, ['tools/gate_tiget_slots.py', '--ids', ','.join(map(str, bad))])
            out.write(io.open(os.path.join(R, 'tmp', 'gate_tiget_report.txt'), encoding='utf-8').read()[-4000:] + '\n')
    if not a.skip_fany:
        # 🆕2026-11-25 抜き打ち 41041 六本木コントライブNEXT！＝登録（10/25）のあとで売り場が出演者を8組足したのに、
        #   カードはロングコートダディ1組のまま。heal_fany --artist（増えた時だけ差し替え）が毎日の流れに入っていなかった
        #   ＝その日か前の日に引いた FANY の一覧があれば、鍵の中で heal_fany --apply --artist（枠の作り直し＋増えた出演者）
        import glob
        src = [p for p in sorted(glob.glob(os.path.join(R, 'tmp', 'fany_1[0-9][0-9][0-9].json')), key=os.path.getmtime)
               if time.time() - os.path.getmtime(p) < 36 * 3600]
        if src:
            fd = None
            for _ in range(1200):
                try:
                    fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, b'vendor_sweep_daily_fany'); os.close(fd); break
                except FileExistsError:
                    time.sleep(3)
            if fd is None:
                out.write('鍵が取れなかった＝heal_fany は回していない\n')
            else:
                try:
                    run(out, ['tools/heal_fany.py', '--src', os.path.relpath(src[-1], R), '--apply', '--artist'])
                finally:
                    os.remove(LOCK)
                out.write(io.open(os.path.join(R, 'tmp', 'heal_fany_report.txt'), encoding='utf-8').read()[-3000:] + '\n')
        else:
            out.write('36時間以内の FANY の一覧が無い＝heal_fany は回していない（朝の fany の収集が止まった日）\n')
        run(out, ['tools/fany_mark_soldout.py', '--apply'])
        out.write(io.open(os.path.join(R, 'tmp', 'fany_soldout_report.txt'), encoding='utf-8').read()[-1500:] + '\n')
    out.close()
    io.open(os.path.join(R, '.claude', 'state', 'vendor_sweep_%s.txt' % today.replace('-', '')), 'w', encoding='utf-8').write(
        datetime.datetime.now().strftime('%H:%M') + '\n')


if __name__ == '__main__':
    main()
