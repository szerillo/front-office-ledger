"""Nov 9: MLB Trade Rumors arbitration projections (Matt Swartz's model), parsed from the
annual post. Writes arb_mlbtr_{year}.json [{team, name, svc, aav, note}]. Usage: python3 mlbtr_arb.py <html> <season>"""
import re, html, json, sys
def parse(path):
    s = open(path, encoding="utf-8", errors="ignore").read()
    i = s.find('class="entry-content'); j = s.find('id="comments"', i)
    txt = html.unescape(re.sub(r"<[^>]+>", "\n", s[i:j])); L = [l.strip() for l in txt.split("\n") if l.strip()]
    k = next(n for n, l in enumerate(L) if l.lower().startswith("the projections"))
    team = None; out = []; pend = None
    for l in L[k+1:]:
        if l.startswith("Photo courtesy"): break
        m = re.match(r"^(.+?) \((\d+)\)$", l)
        if m and not re.search(r"\d\.\d{3}", l): team = m.group(1); continue
        m = re.match(r"^\(([\d.]+)\):\s*\$([\d.]+)\s*(MM|K)\s*(.*)$", l)
        if m and pend:
            v = float(m.group(2)) / (1000 if m.group(3) == "K" else 1)
            out.append(dict(team=team, name=pend, svc=float(m.group(1)), aav=v, note=m.group(4).strip())); pend = None; continue
        pend = l
    return out
if __name__ == "__main__":
    out = parse(sys.argv[1]); json.dump(out, open(f"/work/arb_mlbtr_{sys.argv[2]}.json", "w"), indent=0)
    print(sys.argv[2], len(out), "players")
