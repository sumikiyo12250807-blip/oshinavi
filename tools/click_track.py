"""アフィリ・売り場ボタンのクリックを GA4 に送る小さな JS（2026-10-27 すちこ「①と②からお願い」）。

Why: GA4 にボタンのクリックを数える仕掛けが無く、「押されていない」のか「押されたのに買われていない」のか
区別できなかった。リンクを押した時に GA4 のイベントを1つ送る。
  affiliate_click … 報酬が入る先（Amazon・楽天チケット・ホテル＝バリューコマース/Expedia）
  ticket_click    … 報酬の無い売り場（ぴあ・e+・ローチケ・TIGET・FANY・ZAIKO・livePocket ほか）
パラメータ link_kind（amazon / rakuten / hotel / ticket）・link_text（ボタンの文字か画像の alt）・page_kind（top / artist / pickup）。

使い方: index.html の head には inject_index() で1回だけ入れる。artist ページは build_artist_pages が SNIPPET を埋める。
"""
import io
import re

MARK = "/* oshinavi-click-track */"


def snippet(page_kind):
    return ("<script>" + MARK + "document.addEventListener('click',function(e){"
            "var a=e.target&&e.target.closest&&e.target.closest('a[href]');if(!a||typeof gtag!=='function')return;"
            # 🆕11/23 セブンネット（バリューコマース経由）が hotel に数えられていた＝先に 7net を見る／
            #   TicketDive・チケットペイ・B.LEAGUE・チケボ・ラグビー・宝塚・フジ・野田地図が数えられていなかった
            "var h=a.href||'',k=/amazon\\.co\\.jp|amzn\\.to/.test(h)?'amazon':/7net\\.omni7|7net%2Eomni7/i.test(h)?'7net'"
            ":/linksynergy|ticket\\.rakuten/.test(h)?'rakuten'"
            ":/valuecommerce|expedia/.test(h)?'hotel'"
            ":/pia\\.jp|eplus\\.jp|l-tike|tiget|fany|zaiko|livepocket|yoshimoto|tv-asahi|ticket-web-shochiku"
            "|ticketdive|ticketpay|bleague|tickebo|ticketrugby|kageki\\.hankyu|fujitvdirect|nodamap/.test(h)?'ticket':'';"
            "if(!k)return;var im=a.querySelector('img'),t=(a.textContent||'').trim()||(im&&im.alt)||'';"
            "gtag('event',k==='ticket'?'ticket_click':'affiliate_click',{link_kind:k,link_text:t.slice(0,60),"
            "page_kind:'" + page_kind + "',link_url:h.slice(0,200),transport_type:'beacon'});},true);</script>")


def inject_index(path="index.html"):
    s = io.open(path, encoding="utf-8", newline="").read()
    if MARK in s:
        # 🆕11/23 入っている古い形を新しい形に差し替える（数える売り場を足した時）
        m = re.search(r"<script>" + re.escape(MARK) + r".*?</script>", s)
        new = snippet("top")
        if m.group(0) == new:
            return False
        s = s[:m.start()] + new + s[m.end():]
        io.open(path, "w", encoding="utf-8", newline="").write(s)
        return True
    nl = "\r\n" if "\r\n" in s[:2000] else "\n"
    m = re.search(r"gtag\('config', 'G-RM1EQ5M4HT'\);\s*</script>", s)
    if not m:
        raise SystemExit("gtag config not found")
    s = s[:m.end()] + nl + "  " + snippet("top") + s[m.end():]
    io.open(path, "w", encoding="utf-8", newline="").write(s)
    return True


if __name__ == "__main__":
    print("index.html", "入れた" if inject_index() else "入っていた")
