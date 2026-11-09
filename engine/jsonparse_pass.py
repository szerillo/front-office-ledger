"""Nov 2026: big data constants as JSON.parse('...') instead of object literals: V8 parses a JSON
string much faster than the same object written as JavaScript, which shortens the time to the
first full render on phones. Run last, after regen_v3 (it is idempotent)."""
import json, re, sys
P = sys.argv[1] if len(sys.argv) > 1 else "/work/front-office-ledger-prototype.html"
NAMES = ["DESK", "TRADE_BOOK", "AUTO_REGIMES", "PLAYER_NAMES", "LB_HIST", "PLAYER_FATE", "QUIZ_CTX", "FA_SKILL", "CALIB", "GMC"]
s = open(P, encoding="utf-8").read()
done = []
for k in NAMES:
    m = re.search(r"\n(const|let|var) " + k + r" = ", s)
    if not m: continue
    st = m.end(); nl = s.find("\n", st)
    body = s[st:nl].rstrip()
    if body.startswith("JSON.parse("): continue
    if body.endswith(";"): body = body[:-1]
    try: obj = json.loads(body)
    except Exception as e:
        print("skip", k, "(not plain JSON:", str(e)[:60], ")"); continue
    js = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    lit = "'" + js.replace("\\", "\\\\").replace("'", "\\'").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029").replace("</", "<\\/") + "'"
    s = s[:st] + "JSON.parse(" + lit + ");" + s[nl:]
    done.append(k)
open(P, "w", encoding="utf-8").write(s)
print("JSON.parse:", ", ".join(done))
