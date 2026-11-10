# Deploy step: move the trade book, player fates and quiz notes out of the page into book.js, which loads
# right after the page. The first download gets about 15% smaller; nothing else changes.
# Usage: python3 split_book.py <page.html> <out dir>   (writes <out dir>/index.html and <out dir>/book.js)
import hashlib, sys
src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
EMPTY = {'TRADE_BOOK': '{trades: [], names: {}}', 'PLAYER_FATE': '{}', 'QUIZ_CTX': '{}'}
book = []
for name, empty in EMPTY.items():
    k = s.index('\nconst ' + name + ' = JSON.parse(') + 1; e = s.index('\n', k)
    line = s[k:e]; assert line.rstrip().endswith(';'), name
    book.append(line[len('const '):]); s = s[:k] + 'let ' + name + ' = ' + empty + ';' + s[e:]
js = '\n'.join(book) + '\nbookLoaded();\n'
h = hashlib.sha1(js.encode('utf-8')).hexdigest()[:10]
a = '\nwindow.BOOK_READY = true;\n'; assert s.count(a) == 1; s = s.replace(a, '\nwindow.BOOK_READY = false;\n')
a = "<script>(function(){ var c = document.createElement('script'); c.src = 'cards.js?v="; assert s.count(a) == 1
s = s.replace(a, "<script>(function(){ var b = document.createElement('script'); b.src = 'book.js?v=" + h + "'; document.body.appendChild(b); })();</script>\n" + a)
open(out + '/index.html', 'w', encoding='utf-8').write(s); open(out + '/book.js', 'w', encoding='utf-8').write(js)
print('index.html', len(s), 'book.js', len(js), h)
