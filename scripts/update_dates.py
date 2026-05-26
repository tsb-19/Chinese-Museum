#!/usr/bin/env python3
from datetime import date
from pathlib import Path
import re

today = date.today().isoformat()
idx = Path('index.html')
s = idx.read_text(encoding='utf-8')
s = re.sub(r'最后更新：\d{4}-\d{2}-\d{2}（数据版本）', f'最后更新：{today}（数据版本）', s)
s = re.sub(r'"dateModified": "\d{4}-\d{2}-\d{2}"', f'"dateModified": "{today}"', s)
idx.write_text(s, encoding='utf-8')
sm = Path('sitemap.xml')
ss = sm.read_text(encoding='utf-8')
ss = re.sub(r'<lastmod>\d{4}-\d{2}-\d{2}</lastmod>', f'<lastmod>{today}</lastmod>', ss)
sm.write_text(ss, encoding='utf-8')
print('updated dates to', today)
