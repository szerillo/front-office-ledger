# The reverse of split_book.py: rebuild the working page (data inline) from the deployed index.html and
# book.js. Use when starting on a fresh machine. Usage: python3 unsplit_book.py <repo dir> <out page.html>
import re, sys
repo, out = sys.argv[1], sys.argv[2]
s = open(repo + '/index.html', encoding='utf-8').read(); b = open(repo + '/book.js', encoding='utf-8').read()
EMPTY = {'TRADE_BOOK': '{trades: [], names: {}}', 'PLAYER_FATE': '{}', 'QUIZ_CTX': '{}'}
for name, empty in EMPTY.items():
    k = b.index(name + ' = JSON.parse('); e = b.index('\n', k)
    a = 'let ' + name + ' = ' + empty + ';'; assert s.count(a) == 1, name
    s = s.replace(a, 'const ' + b[k:e])
a = '\nwindow.BOOK_READY = false;\n'; assert s.count(a) == 1; s = s.replace(a, '\nwindow.BOOK_READY = true;\n')
s, n = re.subn(r"<script>\(function\(\)\{ var b = document\.createElement\('script'\); b\.src = 'book\.js\?v=[0-9a-f]+'; document\.body\.appendChild\(b\); \}\)\(\);</script>\n", '', s); assert n == 1
import os
if os.path.exists(repo + '/deals.js'):
    dj = open(repo + '/deals.js', encoding='utf-8').read()
    frag = dj[dj.index("JSON.parse('") + len("JSON.parse('"):dj.rindex("');\ndkDealsLoaded")]
    s, n = re.subn(r"\nwindow\.DESK_DEALS_SRC = 'deals\.js\?v=[0-9a-f]+';", '', s); assert n == 1
    k = s.index('\nconst DESK = JSON.parse('); a = '"deals":null'; i = s.index(a, k); assert i < s.index('\n', k + 1)
    s = s[:i] + '"deals":' + frag + s[i + len(a):]
open(out, 'w', encoding='utf-8').write(s); print('wrote', out, len(s))
