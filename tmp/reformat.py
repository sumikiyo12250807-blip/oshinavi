# -*- coding: utf-8 -*-
import re, json, sys
SRC='index.html'
def run(updates):
    src=open(SRC,encoding='utf-8').read()
    def span(src,i):
        m=re.search(r'"id":\s*%d\b'%i,src); s=m.start()
        e=src.find('"id":',s+10); e=e if e>0 else len(src)
        return s,e
    for u in updates:
        i=u['id']; s,e=span(src,i); seg=src[s:e]
        # strip trailing (県名) or （県名） from venue
        if 'venue' in u:
            newv=u['venue']
        else:
            mv=re.search(r'"venue":\s*"(.*?)"',seg).group(1)
            newv=re.sub(r'[（(][^（()）]{1,8}[）)]$','',mv)
        seg=re.sub(r'("venue":\s*")(.*?)(")', lambda m:m.group(1)+newv+m.group(3), seg, count=1)
        # artist / name
        if 'artist' in u:
            seg=re.sub(r'("artist":\s*")(.*?)(")', lambda m:m.group(1)+u['artist']+m.group(3), seg, count=1)
        if 'name' in u:
            seg=re.sub(r'("name":\s*")(.*?)(")', lambda m:m.group(1)+u['name']+m.group(3), seg, count=1)
        # prefecture
        if 'pref' in u:
            seg=re.sub(r'("prefecture":\s*")(.*?)(")', lambda m:m.group(1)+u['pref']+m.group(3), seg, count=1)
        # top date
        if 'date' in u:
            seg=re.sub(r'("date":\s*")(\d{4}-\d{2}-\d{2})(")', lambda m:m.group(1)+u['date']+m.group(3), seg, count=1)
        # dateLabel
        if 'dateLabel' in u:
            seg=re.sub(r'("dateLabel":\s*")(.*?)(")', lambda m:m.group(1)+u['dateLabel']+m.group(3), seg, count=1)
        # rebuild tickets
        tj=[]
        for t in u['tickets']:
            lines=['                  {']
            lines.append('                        "type": %s,'%json.dumps(t['type'],ensure_ascii=False))
            if t.get('startDate'):
                lines.append('                        "startDate": %s,'%json.dumps(t['startDate']))
            lines.append('                        "date": %s,'%json.dumps(t['date']))
            lines.append('                        "url": %s'%json.dumps(t['url']))
            lines.append('                  }')
            tj.append('\n'.join(lines))
        newt='"tickets": [\n'+',\n'.join(tj)+'\n            ]'
        seg=re.sub(r'"tickets":\s*\[.*?\]', newt, seg, count=1, flags=re.S)
        # remove showSalePeriod line
        seg=re.sub(r'\s*"showSalePeriod":\s*true,', '', seg, count=1)
        src=src[:s]+seg+src[e:]
    open(SRC,'w',encoding='utf-8').write(src)
    print('reformatted', [u['id'] for u in updates])


