import json, time, urllib.request, urllib.error

def gql(query):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request("https://data-graph.mlb.com/graphql", data=body,
        headers={"User-Agent":"Mozilla/5.0","Content-Type":"application/json"})
    for attempt in range(4):
        try: return json.load(urllib.request.urlopen(req, timeout=40))
        except urllib.error.HTTPError as e: return json.loads(e.read().decode('utf-8','ignore'))
        except Exception: time.sleep(4 + attempt*3)
    return None

Q = '''{getPlayerRankingsFromSelection(slug:"sel-pr-%d-top100", limit:120){
  rank
  playerEntity{ eta player{ id useName lastName birthDate birthCountry primaryPosition{abbreviation} } }
}}'''

out = []
for yr in range(2011, 2027):
    r = gql(Q % yr)
    d = (r.get("data") or {}).get("getPlayerRankingsFromSelection") if r else None
    if not d:
        print(yr, "FAILED"); continue
    for row in d:
        pe = row["playerEntity"] or {}
        p = pe.get("player") or {}
        out.append(dict(year=yr, rank=row["rank"], pid=p.get("id"),
            name=f"{p.get('useName','')} {p.get('lastName','')}".strip(),
            pos=(p.get("primaryPosition") or {}).get("abbreviation"),
            eta=pe.get("eta"), bd=p.get("birthDate"), bc=p.get("birthCountry")))
    print(yr, len(d), "rows; no1:", out[-len(d)]["name"] if d else "-")
    time.sleep(2)

json.dump(out, open("/home/claude/prospect_ranks.json", "w"), indent=0)
print("\ntotal rows:", len(out))
missing = [r for r in out if not r["pid"]]
print("rows missing pid:", len(missing))
