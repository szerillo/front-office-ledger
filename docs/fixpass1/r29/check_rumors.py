"""After a trade-reports run: is rumors.json fresh in content, not just in its stamp?
A run can write a new "checked" time and still leave a player on the trade block who was traded or extended
since the file's "updated" date. This checks the live file against the league's transaction feed.
Usage: python3 check_rumors.py [hours]   (hours: how recent "checked" must be, default 3). Exit 1 on any problem."""
import json, sys, urllib.request, datetime as dt
H = float(sys.argv[1]) if len(sys.argv) > 1 else 3
get = lambda u: json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=40))
f = get("https://frontofficeledger.com/rumors.json?t=%d" % dt.datetime.now().timestamp())
now = dt.datetime.now(dt.timezone.utc); bad = []
chk = dt.datetime.fromisoformat(f.get("checked", "1970-01-01T00:00:00Z").replace("Z", "+00:00"))
if (now - chk).total_seconds() > H * 3600: bad.append(f"checked {f.get('checked')} is older than {H} h")
since = f.get("updated") or chk.date().isoformat()
tx = get(f"https://statsapi.mlb.com/api/v1/transactions?sportId=1&startDate={since}&endDate={now.date().isoformat()}").get("transactions", [])
moved = {}
for t in tx:
    pid = (t.get("person") or {}).get("id")
    if not pid: continue
    d = (t.get("description") or "").lower()
    if t.get("typeCode") == "TR" or "extension" in d or "signed" in d and "contract extension" in d:
        moved.setdefault(str(pid), []).append(f"{t.get('date')}: {t.get('description')}")
for row in f.get("rows", []):
    pid = str(row[0])
    if pid in moved: bad.append(f"{f['names'].get(pid, pid)} still on the block but the feed shows {moved[pid][0]}")
print(f"rumors.json: {len(f.get('rows', []))} rows, updated {f.get('updated')}, checked {f.get('checked')}; feed since {since}: {len(tx)} transactions")
for b in bad: print("PROBLEM:", b)
print("OK" if not bad else f"{len(bad)} problem(s)"); sys.exit(1 if bad else 0)
