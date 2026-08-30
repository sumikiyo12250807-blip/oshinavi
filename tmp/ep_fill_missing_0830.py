# -*- coding: utf-8 -*-
"""e+ の取りこぼし公演を、既存エントリに**追加だけ**して埋める（置換しない）。

対象＝エージェント2本が実ページ＋APIで洗い出した12件。
やり方＝各エントリの e+ URL から wordID を取り、API で**全公演**を引き、
        「登録と同じ公演名」の公演で**まだ登録に無いもの**を ticket として足す。

🚨 置換しない（memory: feedback_build_pia_multiurl_loses_ticket_url の「置換は枠を殺す」）。
🚨 各公演の -P URL を ticket.url に必ず刻む（memory: feedback_tour_per_ticket_url）。
"""
import datetime
import importlib.util
import io
import json
import re
import shutil
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TODAY = datetime.date.today()

# 取りこぼしが確認されたエントリ（現在のindex.html上のid）
# エージェント2本が「取りこぼしあり」と判定したエントリ（実id）
TARGET_IDS = [5991,  # 黒蜜 15公演中2件
              5992,  # ビバラッシュ 15公演中2件
              5993,  # ヤミテラ 5公演中1件
              5996,  # 中村佳穂 8公演中3件（横浜10/21が丸ごと＋2ndステージ3本）
              6000,  # 東西ビッグバン 大阪編
              6003,  # HIZAKI 5公演中1件
              6004,  # 上田正樹&内田勘太郎 宮城10/21
              6007,  # 蜈蚣 10/31大阪
              6009,  # Sick2 ツアー5公演＋ファイナル
              6013,  # RENO 同日2部の20:00回
              6014,  # 藤川千愛 同日2部の19:00回
              6016,  # NoGoD 4公演
              6019]  # DRUMGODS 同日2部の20:00回


def load(name, path):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    argv = sys.argv
    sys.argv = [path, "__lib__"]
    try:
        sp.loader.exec_module(m)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return m


eh = load("eh", "tools/eplus_harvest.py")
ewk = load("ewk", "tools/eplus_word_koen.py")

P = "index.html"
src = io.open(P, encoding="utf-8", newline="").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", src, re.S)
EVENTS = json.loads(m.group(2))
byid = {e["id"]: e for e in EVENTS}

log = io.open("logs/eplus_filled_2026-08-30.md", "w", encoding="utf-8")
log.write("# e+ 取りこぼし公演の追加 2026-08-30（追加のみ・置換なし）\n\n")
log.write("エージェント2本が e+ の公演APIで全公演を洗い出した結果を反映。\n\n")

nent = nslot = 0
for eid in TARGET_IDS:
    e = byid.get(eid)
    if not e:
        print("id%d が無い" % eid)
        continue
    base = (e.get("links") or {}).get("eplus") or ""
    if not base:
        print("id%d に e+ URL が無い" % eid)
        continue
    try:
        h = eh.fetch(base)
    except Exception as ex:
        print("id%d fetch失敗 %s" % (eid, str(ex)[:40]))
        continue
    wid = re.search(r"/sf/word/(\d+)", h or "")
    if not wid:
        print("id%d wordID が取れない" % eid)
        continue
    recs = ewk.koen_by_word(wid.group(1))
    name = (e.get("name") or "").strip()

    def tour_key(s):
        """ツアー名の共通部分を取る。登録名は「…「純愛」～千葉～」のように**会場名が末尾に付く**ので、
        そこを剥がさないと同じツアーの他公演と一致しない（2026-08-30 に全件スキップした原因）。"""
        s = re.sub(r"[\s　]+", "", s or "")
        s = re.sub(r"[～~ー\-]{1}[^～~ー\-]{1,12}[～~ー\-]{1}$", "", s)   # 末尾の ～千葉～ / -大阪編-
        return s

    key = tour_key(name)

    have_urls = {re.sub(r"\?.*$", "", t.get("url") or "") for t in e.get("tickets", [])}
    have_urls.add(re.sub(r"\?.*$", "", base))

    add = []
    for r in recs:
        s = ewk.simp(r)
        cand = (s["name"] or "").strip()
        ck = tour_key(cand)
        # 同じツアーか＝完全一致 or ツアー名の共通部分が一致 or 一方が他方の頭に来る
        # 同じツアーの判定＝①完全一致 ②ツアー名の共通部分が前方一致
        #  ③**短い方が長い方の部分文字列**（登録名にアーティスト名が重複する型＝
        #    「ヤミテラ ヤミテラ ONEMAN TOUR 関西制圧」 vs 「ヤミテラ ONEMAN TOUR 関西制圧」）
        #  ④**語順違いで中身が同じ**（「蜈蚣 halloween oneman『誘拐日和』」 vs
        #    「誘拐日和 蜈蚣 halloween oneman」）＝記号を除いた文字の多重集合で判定
        def bag(x):
            return sorted(re.sub(r"[\s　'\"’”「」『』（）()\[\]【】・,.\-–—~～!！?？:：/／]", "", x or ""))
        same_tour = ((cand == name)
                     or (ck and key and (ck == key or ck.startswith(key) or key.startswith(ck)))
                     or (ck and key and (ck in key or key in ck))
                     or (len(name) > 8 and bag(name) == bag(cand)))
        if not same_tour:
            continue                      # 別イベントは触らない
        u = re.sub(r"\?.*$", "", s["url"] or "")
        if not u or u in have_urls:
            continue
        try:
            ph = eh.fetch(u)
        except Exception:
            continue
        time.sleep(0.4)
        wins = [w for w in eh.parse_windows(ph) if w["ed"] >= TODAY]
        if not wins:
            continue
        iso = "%s-%s-%s" % (s["date"][:4], s["date"][4:6], s["date"][6:8]) if s["date"] else ""
        st = (s["start"] or "")
        tm = "%s:%s" % (st[:2], st[2:4]) if len(st) >= 4 else ""
        pref = (s["pref"] or "").replace("都", "都").replace("府", "府")
        for w in wins:
            same_day = (str(w["ed"]) == iso)
            sess = (" %s公演" % tm) if (same_day and tm) else "公演"
            md = "%d/%d" % (int(iso[5:7]), int(iso[8:10])) if iso else ""
            lab = re.sub(r"\s+", "", w["label"]) or ((w["kind"] or "先着") + "一般発売")
            if w["sd"] >= TODAY:
                typ = "%s（%s %s%s）%d/%d %s発売" % (lab, pref, md, sess, w["sd"].month, w["sd"].day, w["st"])
                tk = {"type": typ, "date": str(w["ed"]), "url": u, "startDate": str(w["sd"])}
            else:
                typ = "%s（%s %s%s）〜%d/%d %s" % (lab, pref, md, sess, w["ed"].month, w["ed"].day, w["et"])
                tk = {"type": typ, "date": str(w["ed"]), "url": u}
            add.append((tk, iso, s["venue"]))
        have_urls.add(u)

    if not add:
        print("id%-5s %-30s 追加なし" % (eid, name[:28]))
        continue
    nent += 1
    log.write("## id=%d %s ＋%d枠\n" % (eid, name, len(add)))
    for tk, iso, ven in add:
        e["tickets"].append(tk)
        nslot += 1
        log.write("  + %s ／ %s %s\n    %s\n" % (tk["type"], iso, ven or "", tk["url"]))
    # 千秋楽が後ろに伸びるときだけ date を更新
    dmax = max([iso for _, iso, _ in add if iso] + [e.get("date") or ""])
    if dmax > (e.get("date") or ""):
        log.write("  公演日 %s → %s（千秋楽が伸びた）\n" % (e.get("date"), dmax))
        e["date"] = dmax
    log.write("\n")
    print("id%-5s %-30s ＋%d枠" % (eid, name[:28], len(add)))

shutil.copy(P, "index.html.bak_0830_epfill")
arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
arr = "\n".join("  " + l if i else l for i, l in enumerate(arr.split("\n")))
out = src[:m.start(2)] + arr + src[m.end(2):]
if "\r\n" in src:
    out = out.replace("\r\n", "\n").replace("\n", "\r\n")
io.open(P, "w", encoding="utf-8", newline="").write(out)
log.write("\n合計 %d エントリ / +%d 枠\n" % (nent, nslot))
log.close()
print("\n=== %d エントリに +%d 枠を追加 → logs/eplus_filled_2026-08-30.md ===" % (nent, nslot))
