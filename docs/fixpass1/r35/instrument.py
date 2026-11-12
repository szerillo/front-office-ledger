# instrumented copy of a built site: logs every call of a letter helper that gets a null / non-finite grade,
# with the calling line and what it printed. Usage: instrument.py <site dir> <out dir>
import os, re, shutil, sys
src, out = sys.argv[1], sys.argv[2]
if os.path.exists(out): shutil.rmtree(out)
os.makedirs(out)
for f in os.listdir(src):
    p = os.path.join(src, f)
    if os.path.isfile(p) and f != 'index.html': os.symlink(p, os.path.join(out, f))
for d in ['assets', 'icons', 'data']:
    if os.path.isdir(os.path.join(src, d)): os.symlink(os.path.join(src, d), os.path.join(out, d))
s = open(os.path.join(src, 'index.html'), encoding='utf-8').read()
LOG = "(window.__nullLog = window.__nullLog || []).push([%s, (new Error().stack.split('\\n')[2] || '').replace(/^.*:(\\d+):\\d+\\)?$/, '$1'), String(__r)])"
a = 'const g2letter = g => '
assert s.count(a) == 1
s = s.replace(a, "const g2letter = g => { const __r = __g2l(g); if(g == null || !isFinite(g)) " + LOG % "'g2letter'" + "; return __r; };\nconst __g2l = g => ", 1)
a = 'const gradeClass = g => '
assert s.count(a) == 1
s = s.replace(a, "const gradeClass = g => { const __r = __gc(g); if(g == null || !isFinite(g)) " + LOG % "'gradeClass'" + "; return __r; };\nconst __gc = g => ", 1)
a = 'function deskLetter(rel, cost){'
assert s.count(a) == 1
s = s.replace(a, "function deskLetter(rel, cost){ const __r = __dl(rel, cost); if(!isFinite(rel / Math.max(cost, 1))) " + LOG % "'deskLetter'" + "; return __r; }\nfunction __dl(rel, cost){", 1)
open(os.path.join(out, 'index.html'), 'w', encoding='utf-8').write(s)
print('instrumented', out)
