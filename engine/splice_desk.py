"""Add side tables (prospect bios, 2026 stat lines) to desk_data.json and re-splice the page's DESK
constant without running the whole chain. desk_data.py reads the same files, so a full rebuild keeps them."""
import json, re
R = "/work/"
d = json.load(open(R + "desk_data.json"))
d["bio"] = json.load(open(R + "prospect_bio.json"))
d["line26"] = json.load(open(R + "line26.json"))
open(R + "desk_data.json", "w").write(json.dumps(d, separators=(",", ":"), ensure_ascii=False))
P = R + "front-office-ledger-prototype.html"; s = open(P, encoding="utf-8").read()
m = re.search(r"\nconst DESK = ", s); st = m.end(); nl = s.find("\n", st)
assert s[st:nl].startswith("JSON.parse('")
js = json.dumps(d, separators=(",", ":"), ensure_ascii=False)
lit = "'" + js.replace("\\", "\\\\").replace("'", "\\'").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029").replace("</", "<\\/") + "'"
s = s[:st] + "JSON.parse(" + lit + ");" + s[nl:]
open(P, "w", encoding="utf-8").write(s)
print("DESK spliced:", len(lit), "chars; bio", len(d["bio"]), "line26", len(d["line26"]))
