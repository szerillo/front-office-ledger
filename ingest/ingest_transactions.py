"""
Front Office Ledger, ingestion module v0.1
===========================================
Pulls the MLB Stats API transaction and draft feeds into a normalized local
store (SQLite + CSV). This is the live half of the ingestion plan in the
design doc; the historical half is Retrosheet's transaction file (1870s to
2020), with 2005 to 2020 as the cross-validation overlap.

Measured coverage (July 2026 probes, June sample windows):
    1985 to 1995: 0 rows        2000: ~10      2005: ~200
    2010+: ~6,000 per month     (1920s Negro Leagues data present separately)
So: Stats API is primary from 2005 forward; Retrosheet backfills earlier.

Usage:
    python3 ingest_transactions.py --team 110 --start 2018-11-01 --end 2026-07-21
    python3 ingest_transactions.py --draft 2019 2020 2021 2022 2023 2024 2025

Output: ledger.sqlite (tables: transactions, draft_picks) and matching CSVs.
Entity resolution: person_id here is MLBAM id, which is the join key into
the Chadwick Bureau register (people.csv, key_mlbam) for BRef/FanGraphs/
Retrosheet crosswalk. That join is deliberately a separate pass.
"""
import argparse, csv, json, sqlite3, sys, time, urllib.request
from datetime import date, timedelta

API = "https://statsapi.mlb.com/api/v1"
UA = {"User-Agent": "FrontOfficeLedger-POC/0.1 (research prototype)"}

def get(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            if i == retries - 1: raise
            time.sleep(2 * (i + 1))

def month_chunks(start, end):
    cur = start
    while cur <= end:
        nxt = (cur.replace(day=1) + timedelta(days=45)).replace(day=1) - timedelta(days=1)
        yield cur, min(nxt, end)
        cur = nxt + timedelta(days=1)

def pull_transactions(team_id, start, end):
    rows = []
    for s, e in month_chunks(start, end):
        url = f"{API}/transactions?startDate={s}&endDate={e}"
        if team_id: url += f"&teamId={team_id}"
        data = get(url)
        for t in data.get("transactions", []):
            rows.append(dict(
                tx_id=t.get("id"),
                date=t.get("date"),
                effective_date=t.get("effectiveDate"),
                type_code=t.get("typeCode"),
                type_desc=t.get("typeDesc"),
                person_id=(t.get("person") or {}).get("id"),
                person_name=(t.get("person") or {}).get("fullName"),
                from_team=(t.get("fromTeam") or {}).get("name"),
                to_team=(t.get("toTeam") or {}).get("name"),
                description=t.get("description"),
            ))
        print(f"  {s} .. {e}: {len(rows)} cumulative", file=sys.stderr)
    return rows

def pull_draft(year):
    rows = []
    data = get(f"{API}/draft/{year}")
    for rnd in data["drafts"]["rounds"]:
        for p in rnd.get("picks", []):
            person = p.get("person") or {}
            rows.append(dict(
                year=year, round=p.get("pickRound"), pick_overall=p.get("pickNumber"),
                round_pick=p.get("roundPickNumber"),
                person_id=person.get("id"), person_name=person.get("fullName"),
                team=(p.get("team") or {}).get("name"),
                signed=p.get("isPass") is False and bool(p.get("signingBonus")),
                bonus=p.get("signingBonus"), pick_value=p.get("pickValue"),
                school=(p.get("school") or {}).get("name"),
            ))
    return rows

def store(rows, table, db="ledger.sqlite"):
    if not rows: return
    con = sqlite3.connect(db)
    cols = list(rows[0].keys())
    con.execute(f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(c + ' TEXT' for c in cols)})")
    con.executemany(f"INSERT INTO {table} VALUES ({', '.join('?' * len(cols))})",
                    [[r[c] for c in cols] for r in rows])
    con.commit(); con.close()
    with open(f"{table}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--team", type=int, default=None)
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--draft", nargs="*", type=int)
    a = ap.parse_args()
    if a.start:
        s = date.fromisoformat(a.start); e = date.fromisoformat(a.end or str(date.today()))
        rows = pull_transactions(a.team, s, e)
        store(rows, "transactions")
        from collections import Counter
        c = Counter(r["type_desc"] for r in rows)
        print(f"\n{len(rows)} transactions stored. By type:")
        for k, v in c.most_common(): print(f"  {v:>5}  {k}")
    if a.draft:
        allrows = []
        for y in a.draft:
            allrows += pull_draft(y); print(f"  draft {y}: {len(allrows)} cumulative picks", file=sys.stderr)
        store(allrows, "draft_picks")
        print(f"{len(allrows)} draft picks stored.")
