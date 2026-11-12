"""Rebuild ledger.sqlite (ledger_v2) from data/ledger/*.jsonl.gz. Usage: python3 restore_ledger.py <dir> <out.sqlite>
Rows go in their original order, so rowid order matches the build. Check: content md5 printed per table."""
import sqlite3, gzip, json, sys, hashlib, os
src, out = sys.argv[1], sys.argv[2]
if os.path.exists(out): sys.exit(f"{out} exists; refusing to overwrite")
c = sqlite3.connect(out)
for t in ["sweep_tx", "draft_picks"]:
    parts = sorted(x for x in os.listdir(src) if x.startswith(f"{t}.jsonl.gz"))
    import io
    blob = b"".join(open(f"{src}/{x}", "rb").read() for x in parts)   # sweep_tx is split in 3 MB parts for upload
    with gzip.open(io.BytesIO(blob), "rt", encoding="utf-8") as f:
        c.execute(json.loads(f.readline())["ddl"]); rows = [tuple(json.loads(l)) for l in f]
    c.executemany(f"insert into {t} values ({','.join('?' * len(rows[0]))})", rows); c.commit()
    h = hashlib.md5(repr(c.execute(f"select * from {t} order by rowid").fetchall()).encode()).hexdigest()[:8]
    print(t, len(rows), "content md5", h)
