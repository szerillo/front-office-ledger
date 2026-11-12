# Round 48: re-pull diff for an MLBTR arbitration post. Compares name -> service figure between two saved copies.
import re, sys, html, json
def rows(p):
    t = html.unescape(open(p, encoding='utf-8', errors='ignore').read())
    t = re.sub(r'<[^>]+>', ' ', t)
    return {m.group(1).strip(): m.group(2) for m in re.finditer(r"([A-Z][A-Za-z.'À-ſ -]{2,40}?) \((\d\.\d{3})\)", t)}
a, b = rows(sys.argv[1]), rows(sys.argv[2])
cav = lambda p: 'not finalized' in open(p, encoding='utf-8', errors='ignore').read()
out = {'old_rows': len(a), 'new_rows': len(b), 'caveat_old': cav(sys.argv[1]), 'caveat_new': cav(sys.argv[2]),
       'changed': {k: [a[k], b[k]] for k in a if k in b and a[k] != b[k]}, 'added': sorted(set(b) - set(a)), 'dropped': sorted(set(a) - set(b))}
print(json.dumps(out, ensure_ascii=False)[:1500])
