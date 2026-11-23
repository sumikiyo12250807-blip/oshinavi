# -*- coding: utf-8 -*-
# 差し替えた JS が文法どおりか（node --check）と、リンクの形ごとに何に数えられるか
import io, re, subprocess, sys
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import click_track as CT
js = re.search(r'<script>(.*)</script>', CT.snippet('top'), re.S).group(1)
io.open('C:/Users/user/oshinavi/tmp/x1123/ct.js', 'w', encoding='utf-8').write(js)
r = subprocess.run(['node', '--check', 'C:/Users/user/oshinavi/tmp/x1123/ct.js'], capture_output=True, text=True)
m = re.search(r"var h=a\.href\|\|'',(k=.*?);if\(!k\)", js).group(1)
test = "var out=[];[%s].forEach(function(h){var %s;out.push(h.slice(0,50)+' => '+k)});console.log(out.join('\\n'))" % (
    ','.join(repr(u) for u in ['https://www.amazon.co.jp/s?k=x', 'https://ck.jp.ap.valuecommerce.com/servlet/referral?sid=1&vc_url=https%3A%2F%2F7net.omni7.jp%2Fdetail%2F1.html',
                                'https://click.linksynergy.com/fs-bin/click?id=z9', 'https://ck.jp.ap.valuecommerce.com/servlet/referral?vc_url=expedia',
                                'https://t.pia.jp/x', 'https://ticketdive.com/event/1', 'https://www.ticketpay.jp/booking/?event_id=1', 'https://ticket.bleague.jp/x', 'https://example.com']), m)
r2 = subprocess.run(['node', '-e', test], capture_output=True, text=True, encoding='utf-8')
io.open('C:/Users/user/oshinavi/tmp/x1123/ct_check.txt', 'w', encoding='utf-8').write('文法 rc=%d %s\n%s%s' % (r.returncode, r.stderr, r2.stdout, r2.stderr))
